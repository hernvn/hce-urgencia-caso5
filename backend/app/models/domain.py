"""
Modelos de Dominio y Persistencia (SQLAlchemy 2.0 ORM).
Alineados con los recursos estándar HL7 FHIR R4 y las decisiones arquitectónicas ADR-02, ADR-03 y ADR-05.
"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class UserModel(Base):
    """Representa un profesional o auditor autenticado mediante RBAC (Practitioner en FHIR R4)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(40), nullable=False)  # PARAMEDICO | MEDICO_URGENCIA | MEDICO_TELECONSULTOR | AUDITOR_FORENSE
    facility = Column(String(100), nullable=False)  # Ej: "Ambulancia Móvil 07", "Clínica Central Urgencias"
    specialty = Column(String(80), nullable=True)
    active = Column(Boolean, default=True)


class PatientModel(Base):
    """
    Recurso FHIR R4 Patient y resumen clínico mutable protegido por Concurrencia Optimista (ADR-05).
    El campo `version` actúa como vector de versión para detectar conflictos de edición concurrente
    entre una ambulancia offline y la clínica de destino.
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    birth_date = Column(String(15), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(20), nullable=False)
    blood_type = Column(String(10), nullable=False)
    chronic_conditions = Column(Text, nullable=False, default="")  # Separadas por punto y coma
    current_medications = Column(Text, nullable=False, default="")  # Separadas por punto y coma

    # Campos mutables críticos sujetos a control de concurrencia optimista (ADR-05)
    allergies = Column(Text, nullable=False, default="Ninguna conocida")
    active_diagnosis = Column(String(255), nullable=False, default="En evaluación inicial")
    treatment_plan = Column(Text, nullable=False, default="Monitorización basal")
    version = Column(Integer, nullable=False, default=1)
    has_pending_conflict = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    vital_signs = relationship("VitalSignObservationModel", back_populates="patient", cascade="all, delete-orphan")
    orders = relationship("MedicalOrderModel", back_populates="patient", cascade="all, delete-orphan")
    conflicts = relationship("SyncConflictModel", back_populates="patient", cascade="all, delete-orphan")


class VitalSignObservationModel(Base):
    """
    Recurso FHIR R4 Observation (Signos Vitales y Triage).
    Estructura Append-Only (G-Set CRDT según ADR-05) con clave de idempotencia UUID generada en el cliente (ADR-02/ADR-04).
    """
    __tablename__ = "vital_sign_observations"

    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String(64), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    episode_code = Column(String(40), nullable=False, index=True)

    heart_rate_bpm = Column(Integer, nullable=False)        # Frecuencia cardíaca (lpm)
    spo2_percent = Column(Integer, nullable=False)          # Saturación de oxígeno (%)
    systolic_bp = Column(Integer, nullable=False)           # Presión arterial sistólica (mmHg)
    diastolic_bp = Column(Integer, nullable=False)          # Presión arterial diastólica (mmHg)
    temperature_c = Column(Float, nullable=False)           # Temperatura corporal (°C)
    glasgow_score = Column(Integer, nullable=False, default=15)  # Escala de coma de Glasgow (3-15)

    # Clasificación calculada mediante el Patrón Strategy (ESI / Triage + Reglas Clínicas)
    triage_category = Column(String(30), nullable=False)    # ESI-1 Crítico | ESI-2 Alto Riesgo | ESI-3 Estable
    clinical_alerts = Column(Text, nullable=False, default="Sin alertas críticas")
    is_critical = Column(Boolean, nullable=False, default=False)

    recorded_by = Column(String(80), nullable=False)
    recorded_role = Column(String(40), nullable=False)
    origin_node = Column(String(80), nullable=False, default="Ambulancia Móvil 07")
    clinical_notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=utc_now, nullable=False)

    patient = relationship("PatientModel", back_populates="vital_signs")


class MedicalOrderModel(Base):
    """
    Recurso FHIR R4 MedicationRequest / ServiceRequest (Órdenes Médicas y Teleconsulta).
    Mantenido cohesivamente junto al expediente clínico según ADR-03 para garantizar invariantes de seguridad
    (ninguna prescripción se emite sin verificar alergias del expediente en la misma transacción ACID).
    """
    __tablename__ = "medical_orders"

    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String(64), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    episode_code = Column(String(40), nullable=False)

    order_type = Column(String(40), nullable=False)  # FARMACO | TELECONSULTA | PROCEDIMIENTO | DERIVACION
    medication_or_action = Column(String(160), nullable=False)
    dosage_and_route = Column(String(160), nullable=False)
    clinical_justification = Column(Text, nullable=False)
    teleconsultation_room_id = Column(String(64), nullable=True)

    author_name = Column(String(100), nullable=False)
    author_role = Column(String(40), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    patient = relationship("PatientModel", back_populates="orders")


class SyncConflictModel(Base):
    """
    Cola de Arbitraje Clínico para conflictos de concurrencia optimista en campos mutables (ADR-05).
    Cuando la versión enviada por un cliente desconectado no coincide con la versión del servidor,
    ambas versiones en pugna se preservan para resolución manual del médico a cargo.
    """
    __tablename__ = "sync_conflicts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name = Column(String(60), nullable=False)  # Ej: "allergies", "active_diagnosis"
    client_expected_version = Column(Integer, nullable=False)
    server_current_version = Column(Integer, nullable=False)
    server_value = Column(Text, nullable=False)
    client_proposed_value = Column(Text, nullable=False)
    submitted_by = Column(String(80), nullable=False)
    origin_node = Column(String(80), nullable=False)
    status = Column(String(30), nullable=False, default="PENDIENTE")  # PENDIENTE | RESUELTO
    resolved_by = Column(String(80), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    patient = relationship("PatientModel", back_populates="conflicts")


class AuditLedgerModel(Base):
    """
    Ledger de Auditoría Forense Inmutable con Encadenamiento Criptográfico SHA-256 (ADR-03 y ADR-08).
    Cada registro almacena el hash del evento previo (`prev_hash`) y calcula su propio `current_hash`,
    formando una cadena verificable que evidencia cualquier intento de adulteración en base de datos.
    """
    __tablename__ = "audit_ledger"

    id = Column(Integer, primary_key=True, index=True)
    sequence_number = Column(Integer, unique=True, index=True, nullable=False)
    actor_username = Column(String(60), nullable=False, index=True)
    actor_role = Column(String(40), nullable=False)
    action_type = Column(String(60), nullable=False, index=True)
    resource_type = Column(String(60), nullable=False)
    resource_id = Column(String(60), nullable=False)
    details = Column(Text, nullable=False)
    client_ip_or_node = Column(String(80), nullable=False, default="127.0.0.1")
    timestamp_iso = Column(String(40), nullable=False)
    prev_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), unique=True, nullable=False)
