"""
Controladores REST / FHIR R4 y Autenticación OAuth2/JWT con Control de Acceso Basado en Roles (RBAC).
"""
from datetime import datetime, timezone
from typing import List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import create_access_token, decode_access_token, get_db, verify_password
from app.models.domain import UserModel
from app.observers.audit_observer import ClinicalDomainEvent, clinical_event_bus, critical_alert_observer
from app.repositories.ehr_repository import AuditLedgerRepository, PatientEHRRepository, UserRepository
from app.schemas.fhir_schemas import (
    AuditLedgerEntryResponse,
    AuditVerificationResponse,
    ConflictResolutionRequest,
    LoginRequest,
    MedicalOrderCreateRequest,
    MedicalOrderResponse,
    MutableFieldUpdateRequest,
    PatientEHRResponse,
    TokenResponse,
    UserProfileResponse,
    VitalSignCreateRequest,
    VitalSignObservationResponse,
)
from app.services.clinical_service import ClinicalEHRService

router = APIRouter(prefix="/api/v1")
security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida: Token JWT ausente en cabecera Authorization.",
        )
    try:
        payload = decode_access_token(credentials.credentials)
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token JWT inválido: claim 'sub' ausente.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada (TTL 15 min superado según ADR-02). Utilice credencial offline o reautentique.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de verificación criptográfica en token JWT.",
        )

    user = UserRepository(db).get_by_username(username)
    if not user or not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo.")
    return user


def require_roles(allowed_roles: List[str]):
    """Dependencia declarativa para hacer cumplir RBAC estricto por endpoint."""

    def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"ACCESO DENEGADO (RBAC HIPAA): El rol '{current_user.role}' no posee privilegios para "
                    f"ejecutar esta operación. Roles autorizados: {', '.join(allowed_roles)}."
                ),
            )
        return current_user

    return role_checker


# =====================================================================
# 1. AUTENTICACIÓN Y GESTIÓN DE SESIÓN (ADR-02 y ADR-08)
# =====================================================================

@router.post("/auth/login", response_model=TokenResponse, tags=["Seguridad y RBAC (ADR-02 / ADR-08)"])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(payload.username)
    if not user or not verify_password(payload.password, user.hashed_password):
        clinical_event_bus.publish(
            db,
            ClinicalDomainEvent(
                actor_username=payload.username,
                actor_role="UNAUTHENTICATED",
                action_type="AUTH_LOGIN_FAILED",
                resource_type="PractitionerSession",
                resource_id=payload.username,
                details=f"Intento fallido de inicio de sesión desde nodo '{payload.device_node}'",
                client_node=payload.device_node,
                is_critical_alert=True,
            ),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas. Verifique usuario y contraseña institucional.",
        )

    token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "facility": user.facility,
        }
    )

    clinical_event_bus.publish(
        db,
        ClinicalDomainEvent(
            actor_username=user.username,
            actor_role=user.role,
            action_type="AUTH_LOGIN_SUCCESS",
            resource_type="PractitionerSession",
            resource_id=f"Practitioner/{user.id}",
            details=f"Sesión iniciada por {user.full_name} ({user.role}) en '{payload.device_node}'. JWT TTL=15m, Offline Credential=72h.",
            client_node=payload.device_node,
        ),
    )

    return TokenResponse(
        access_token=token,
        user=UserProfileResponse.model_validate(user),
    )


@router.get("/auth/demo-users", response_model=List[UserProfileResponse], tags=["Seguridad y RBAC (ADR-02 / ADR-08)"])
def list_demo_users(db: Session = Depends(get_db)):
    """Retorna la lista de perfiles precargados para facilitar la evaluación y el video demostrativo."""
    return UserRepository(db).list_all()


# =====================================================================
# 2. RECURSOS CLÍNICOS FHIR R4 (EXPEDIENTE, TRIAGE Y ÓRDENES - ADR-03/05)
# =====================================================================

@router.get("/fhir/patients", response_model=List[PatientEHRResponse], tags=["HCE Interoperable FHIR R4 (ADR-03)"])
def list_patients(
    current_user: UserModel = Depends(
        require_roles(["PARAMEDICO", "MEDICO_URGENCIA", "MEDICO_TELECONSULTOR", "AUDITOR_FORENSE"])
    ),
    db: Session = Depends(get_db),
):
    return PatientEHRRepository(db).get_all_patients()


@router.get("/fhir/patients/{patient_id}", response_model=PatientEHRResponse, tags=["HCE Interoperable FHIR R4 (ADR-03)"])
def get_patient_fhir_ehr(
    patient_id: int,
    current_user: UserModel = Depends(
        require_roles(["PARAMEDICO", "MEDICO_URGENCIA", "MEDICO_TELECONSULTOR", "AUDITOR_FORENSE"])
    ),
    db: Session = Depends(get_db),
):
    service = ClinicalEHRService(db)
    return service.get_patient_ehr(patient_id=patient_id, actor=current_user, client_node=current_user.facility)


@router.post(
    "/fhir/patients/{patient_id}/vital-signs",
    response_model=VitalSignObservationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Telemetría y Triage (ADR-02 / ADR-04 / Strategy)"],
)
def record_vital_signs(
    patient_id: int,
    payload: VitalSignCreateRequest,
    current_user: UserModel = Depends(require_roles(["PARAMEDICO", "MEDICO_URGENCIA"])),
    db: Session = Depends(get_db),
):
    service = ClinicalEHRService(db)
    obs, _ = service.record_vital_signs_triage(patient_id=patient_id, payload=payload, actor=current_user)
    return obs


@router.put(
    "/fhir/patients/{patient_id}/mutable-fields",
    tags=["Sincronización y Arbitraje Clínico (ADR-05)"],
)
def update_mutable_field(
    patient_id: int,
    payload: MutableFieldUpdateRequest,
    current_user: UserModel = Depends(require_roles(["PARAMEDICO", "MEDICO_URGENCIA", "MEDICO_TELECONSULTOR"])),
    db: Session = Depends(get_db),
):
    service = ClinicalEHRService(db)
    return service.update_mutable_clinical_field(patient_id=patient_id, payload=payload, actor=current_user)


@router.post(
    "/fhir/conflicts/{conflict_id}/resolve",
    tags=["Sincronización y Arbitraje Clínico (ADR-05)"],
)
def resolve_conflict(
    conflict_id: int,
    payload: ConflictResolutionRequest,
    current_user: UserModel = Depends(require_roles(["MEDICO_URGENCIA", "MEDICO_TELECONSULTOR"])),
    db: Session = Depends(get_db),
):
    service = ClinicalEHRService(db)
    return service.resolve_sync_conflict(conflict_id=conflict_id, payload=payload, actor=current_user)


@router.post(
    "/fhir/patients/{patient_id}/orders",
    response_model=MedicalOrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Órdenes Médicas y Telemedicina (ADR-03)"],
)
def create_medical_order(
    patient_id: int,
    payload: MedicalOrderCreateRequest,
    current_user: UserModel = Depends(require_roles(["MEDICO_URGENCIA", "MEDICO_TELECONSULTOR"])),
    db: Session = Depends(get_db),
):
    service = ClinicalEHRService(db)
    return service.create_medical_order(patient_id=patient_id, payload=payload, actor=current_user)


# =====================================================================
# 3. LEDGER DE AUDITORÍA FORENSE INMUTABLE (ADR-03 / ADR-08 / Observer)
# =====================================================================

@router.get(
    "/audit/verify-chain",
    response_model=AuditVerificationResponse,
    tags=["Auditoría Forense Inmutable (ADR-03 / Observer)"],
)
def verify_audit_ledger(
    current_user: UserModel = Depends(
        require_roles(["AUDITOR_FORENSE", "MEDICO_URGENCIA", "MEDICO_TELECONSULTOR"])
    ),
    db: Session = Depends(get_db),
):
    audit_repo = AuditLedgerRepository(db)
    is_valid, total, genesis, latest, message = audit_repo.verify_chain_integrity()
    entries = audit_repo.list_entries(limit=100)
    return AuditVerificationResponse(
        is_valid=is_valid,
        total_events_verified=total,
        genesis_hash=genesis,
        latest_hash=latest,
        verification_timestamp=datetime.now(timezone.utc).isoformat(),
        status_message=message,
        entries=[AuditLedgerEntryResponse.model_validate(e) for e in entries],
    )


@router.get("/telemetry/critical-alerts", tags=["Telemetría y Triage (ADR-02 / ADR-04 / Strategy)"])
def get_active_critical_alerts(
    current_user: UserModel = Depends(
        require_roles(["PARAMEDICO", "MEDICO_URGENCIA", "MEDICO_TELECONSULTOR", "AUDITOR_FORENSE"])
    ),
):
    return {"alerts": critical_alert_observer.recent_critical_alerts}
