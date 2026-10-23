"""
Esquemas declarativos Pydantic v2 alineados con recursos HL7 FHIR R4 (Patient, Observation, MedicationRequest, AuditEvent).
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=60, description="Identificador del profesional de salud")
    password: str = Field(..., min_length=4, max_length=120, description="Credencial de acceso")
    device_node: str = Field(default="Ambulancia Móvil 07 (Edge Node)", description="Nodo de borde o estación clínica")


class UserProfileResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    facility: str
    specialty: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 900
    offline_credential_ttl_hours: int = 72
    user: UserProfileResponse


class VitalSignCreateRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=64, description="Clave UUID de idempotencia generada en cliente (ADR-02/ADR-04)")
    episode_code: str = Field(default="URG-2026-0084", min_length=4, max_length=40)
    heart_rate_bpm: int = Field(..., ge=20, le=260, description="Frecuencia cardíaca en lpm (rango fisiológico válido: 20-260)")
    spo2_percent: int = Field(..., ge=40, le=100, description="Saturación periférica de O2 % (rango válido: 40-100)")
    systolic_bp: int = Field(..., ge=40, le=300, description="Presión arterial sistólica mmHg (rango válido: 40-300)")
    diastolic_bp: int = Field(..., ge=20, le=200, description="Presión arterial diastólica mmHg (rango válido: 20-200)")
    temperature_c: float = Field(..., ge=28.0, le=44.0, description="Temperatura corporal en °C (rango válido: 28.0-44.0)")
    glasgow_score: int = Field(default=15, ge=3, le=15, description="Escala de Coma de Glasgow (3-15)")
    origin_node: str = Field(default="Ambulancia Móvil 07 — Ruta Sur", max_length=80)
    clinical_notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("diastolic_bp")
    @classmethod
    def validate_blood_pressure_coherence(cls, diastolic: int, info) -> int:
        systolic = info.data.get("systolic_bp")
        if systolic is not None and diastolic >= systolic:
            raise ValueError(
                f"Incoherencia fisiológica detectada: la presión diastólica ({diastolic} mmHg) "
                f"no puede ser mayor o igual que la presión sistólica ({systolic} mmHg)."
            )
        return diastolic


class VitalSignObservationResponse(BaseModel):
    id: int
    idempotency_key: str
    patient_id: int
    episode_code: str
    heart_rate_bpm: int
    spo2_percent: int
    systolic_bp: int
    diastolic_bp: int
    temperature_c: float
    glasgow_score: int
    triage_category: str
    clinical_alerts: str
    is_critical: bool
    recorded_by: str
    recorded_role: str
    origin_node: str
    clinical_notes: Optional[str] = None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class MutableFieldUpdateRequest(BaseModel):
    field_name: str = Field(..., pattern="^(allergies|active_diagnosis|treatment_plan)$")
    new_value: str = Field(..., min_length=3, max_length=600)
    expected_version: int = Field(..., ge=1, description="Versión del expediente que el cliente cree vigente (ADR-05)")
    origin_node: str = Field(default="Ambulancia Móvil 07", max_length=80)


class SyncConflictResponse(BaseModel):
    id: int
    patient_id: int
    field_name: str
    client_expected_version: int
    server_current_version: int
    server_value: str
    client_proposed_value: str
    submitted_by: str
    origin_node: str
    status: str
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConflictResolutionRequest(BaseModel):
    chosen_value: str = Field(..., min_length=3, max_length=600, description="Valor clínico conciliado definitivo")
    resolution_notes: str = Field(..., min_length=5, max_length=500, description="Justificación clínica obligatoria para el ledger de auditoría")


class MedicalOrderCreateRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=64)
    episode_code: str = Field(default="URG-2026-0084", min_length=4, max_length=40)
    order_type: str = Field(..., pattern="^(FARMACO|TELECONSULTA|PROCEDIMIENTO|DERIVACION)$")
    medication_or_action: str = Field(..., min_length=3, max_length=160)
    dosage_and_route: str = Field(..., min_length=2, max_length=160)
    clinical_justification: str = Field(..., min_length=5, max_length=500)
    teleconsultation_room_id: Optional[str] = Field(default=None, max_length=64)


class MedicalOrderResponse(BaseModel):
    id: int
    idempotency_key: str
    patient_id: int
    episode_code: str
    order_type: str
    medication_or_action: str
    dosage_and_route: str
    clinical_justification: str
    teleconsultation_room_id: Optional[str] = None
    author_name: str
    author_role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PatientEHRResponse(BaseModel):
    id: int
    rut: str
    full_name: str
    birth_date: str
    age: int
    sex: str
    blood_type: str
    chronic_conditions: str
    current_medications: str
    allergies: str
    active_diagnosis: str
    treatment_plan: str
    version: int
    has_pending_conflict: bool
    updated_at: datetime
    vital_signs: List[VitalSignObservationResponse] = []
    orders: List[MedicalOrderResponse] = []
    conflicts: List[SyncConflictResponse] = []

    model_config = {"from_attributes": True}


class AuditLedgerEntryResponse(BaseModel):
    id: int
    sequence_number: int
    actor_username: str
    actor_role: str
    action_type: str
    resource_type: str
    resource_id: str
    details: str
    client_ip_or_node: str
    timestamp_iso: str
    prev_hash: str
    current_hash: str

    model_config = {"from_attributes": True}


class AuditVerificationResponse(BaseModel):
    is_valid: bool
    total_events_verified: int
    genesis_hash: str
    latest_hash: str
    verification_timestamp: str
    status_message: str
    entries: List[AuditLedgerEntryResponse]
