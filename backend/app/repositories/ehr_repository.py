"""
PATRÓN DE DISEÑO #3: REPOSITORY (Arquitectónico / Acceso a Datos)
-----------------------------------------------------------------
Problema que resuelve:
En una arquitectura de persistencia políglota e híbrida (Sección 3.3, ADR-03 y ADR-05), la capa de aplicación
(servicios clínicos de dominio) no debe conocer sentencias SQL, detalles del ORM SQLAlchemy ni los mecanismos de
verificación de llaves de idempotencia (`idempotency_key` UUID) de la cola Store-and-Forward (ADR-02 / ADR-04).

Cómo se refleja en la implementación:
`PatientEHRRepository` y `AuditLedgerRepository` encapsulan todas las consultas y escrituras transaccionales,
garantizando idempotencia ante reintentos de red de la ambulancia y ofreciendo métodos de dominio limpios y
fácilmente sustituibles por dobles de prueba (mocks/in-memory SQLite) durante las pruebas automatizadas.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.domain import (
    AuditLedgerModel,
    MedicalOrderModel,
    PatientModel,
    SyncConflictModel,
    UserModel,
    VitalSignObservationModel,
)
from app.observers.audit_observer import ForensicAuditLedgerObserver, GENESIS_HASH


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def list_all(self) -> List[UserModel]:
        return self.db.query(UserModel).order_by(UserModel.id.asc()).all()


class PatientEHRRepository:
    """Repositorio del agregado Expediente Clínico - Órdenes (ADR-03)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all_patients(self) -> List[PatientModel]:
        return self.db.query(PatientModel).order_by(PatientModel.id.asc()).all()

    def get_patient_by_id(self, patient_id: int) -> Optional[PatientModel]:
        return self.db.query(PatientModel).filter(PatientModel.id == patient_id).first()

    def get_vital_sign_by_idempotency_key(self, key: str) -> Optional[VitalSignObservationModel]:
        return (
            self.db.query(VitalSignObservationModel)
            .filter(VitalSignObservationModel.idempotency_key == key)
            .first()
        )

    def save_vital_sign_observation(self, observation: VitalSignObservationModel) -> VitalSignObservationModel:
        self.db.add(observation)
        self.db.commit()
        self.db.refresh(observation)
        return observation

    def get_order_by_idempotency_key(self, key: str) -> Optional[MedicalOrderModel]:
        return (
            self.db.query(MedicalOrderModel)
            .filter(MedicalOrderModel.idempotency_key == key)
            .first()
        )

    def save_medical_order(self, order: MedicalOrderModel) -> MedicalOrderModel:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_mutable_field(self, patient: PatientModel, field_name: str, new_value: str) -> PatientModel:
        setattr(patient, field_name, new_value)
        patient.version += 1
        patient.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def create_sync_conflict(
        self,
        patient: PatientModel,
        field_name: str,
        client_expected_version: int,
        server_current_version: int,
        server_value: str,
        client_proposed_value: str,
        submitted_by: str,
        origin_node: str,
    ) -> SyncConflictModel:
        conflict = SyncConflictModel(
            patient_id=patient.id,
            field_name=field_name,
            client_expected_version=client_expected_version,
            server_current_version=server_current_version,
            server_value=server_value,
            client_proposed_value=client_proposed_value,
            submitted_by=submitted_by,
            origin_node=origin_node,
            status="PENDIENTE",
        )
        patient.has_pending_conflict = True
        self.db.add(conflict)
        self.db.commit()
        self.db.refresh(conflict)
        return conflict

    def get_conflict_by_id(self, conflict_id: int) -> Optional[SyncConflictModel]:
        return self.db.query(SyncConflictModel).filter(SyncConflictModel.id == conflict_id).first()

    def resolve_conflict(
        self,
        conflict: SyncConflictModel,
        chosen_value: str,
        resolved_by: str,
        resolution_notes: str,
    ) -> Tuple[PatientModel, SyncConflictModel]:
        patient = self.get_patient_by_id(conflict.patient_id)
        setattr(patient, conflict.field_name, chosen_value)
        patient.version += 1
        patient.updated_at = datetime.now(timezone.utc)

        conflict.status = "RESUELTO"
        conflict.resolved_by = resolved_by
        conflict.resolution_notes = resolution_notes
        conflict.resolved_at = datetime.now(timezone.utc)

        # Verificar si quedan otros conflictos pendientes para este paciente
        remaining = (
            self.db.query(SyncConflictModel)
            .filter(
                SyncConflictModel.patient_id == patient.id,
                SyncConflictModel.status == "PENDIENTE",
                SyncConflictModel.id != conflict.id,
            )
            .count()
        )
        patient.has_pending_conflict = remaining > 0

        self.db.commit()
        self.db.refresh(patient)
        self.db.refresh(conflict)
        return patient, conflict


class AuditLedgerRepository:
    """
    Repositorio de solo lectura y verificación criptográfica para el Ledger Forense (ADR-03 / ADR-08).
    Intencionalmente carece de métodos `update()` o `delete()` para reflejar la propiedad arquitectónica Append-Only.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_entries(self, limit: int = 100) -> List[AuditLedgerModel]:
        return (
            self.db.query(AuditLedgerModel)
            .order_by(AuditLedgerModel.sequence_number.desc())
            .limit(limit)
            .all()
        )

    def verify_chain_integrity(self) -> Tuple[bool, int, str, str, str]:
        """
        Recorre secuencialmente todo el Ledger Forense desde el bloque génesis y recalcula cada hash SHA-256
        para certificar matemáticamente que ningún registro ha sido modificado ni eliminado.
        """
        entries = (
            self.db.query(AuditLedgerModel)
            .order_by(AuditLedgerModel.sequence_number.asc())
            .all()
        )
        if not entries:
            return True, 0, GENESIS_HASH, GENESIS_HASH, "Ledger vacío (sin eventos registrados aún)."

        expected_prev_hash = GENESIS_HASH
        for idx, entry in enumerate(entries, start=1):
            if entry.sequence_number != idx:
                return (
                    False,
                    idx,
                    GENESIS_HASH,
                    entry.current_hash,
                    f"Ruptura de secuencia detectada en el bloque #{idx} (esperado {idx}, encontrado {entry.sequence_number}).",
                )
            if entry.prev_hash != expected_prev_hash:
                return (
                    False,
                    idx,
                    GENESIS_HASH,
                    entry.current_hash,
                    f"Corrupción de encadenamiento en bloque #{entry.sequence_number}: prev_hash no coincide con el bloque anterior.",
                )

            recalculated = ForensicAuditLedgerObserver.compute_entry_hash(
                sequence_number=entry.sequence_number,
                actor_username=entry.actor_username,
                actor_role=entry.actor_role,
                action_type=entry.action_type,
                resource_type=entry.resource_type,
                resource_id=entry.resource_id,
                details=entry.details,
                timestamp_iso=entry.timestamp_iso,
                prev_hash=entry.prev_hash,
            )
            if recalculated != entry.current_hash:
                return (
                    False,
                    idx,
                    GENESIS_HASH,
                    entry.current_hash,
                    f"Adulteración de contenido detectada en bloque #{entry.sequence_number}: hash recalculado difiere del almacenado.",
                )
            expected_prev_hash = entry.current_hash

        return (
            True,
            len(entries),
            GENESIS_HASH,
            entries[-1].current_hash,
            f"Integridad criptográfica SHA-256 verificada exitosamente sobre {len(entries)} bloques encadenados (0 adulteraciones).",
        )
