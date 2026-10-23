"""
PATRÓN DE DISEÑO #2: OBSERVER (Comportamiento / Event-Driven)
-------------------------------------------------------------
Problema que resuelve:
El mandato regulatorio del Caso 5 exige trazabilidad forense inmutable (HIPAA / FHIR AuditEvent) para cada lectura,
escritura, prescripción, alerta crítica o conflicto de sincronización, sin acoplar la lógica clínica del servicio
Expediente-Órdenes al motor criptográfico de auditoría ni a los despachadores de alertas (evitando el Antipatrón 1
"The Blob / God Service" y el Antipatrón 2 "Monolito Distribuido" documentados en la Sección 5).

Cómo se refleja en la implementación:
`ClinicalDomainEventBus` actúa como Subject (Publicador) y notifica a suscriptores desacoplados (`ClinicalEventObserver`):
1. `ForensicAuditLedgerObserver`: Calcula el encadenamiento criptográfico SHA-256 (`prev_hash` + payload -> `current_hash`)
   e inserta un registro append-only en el Ledger de Auditoría.
2. `CriticalTelemetryAlertObserver`: Registra en memoria de baja latencia las alertas de código rojo para las estaciones
   de teleconsulta y paneles de urgencia.
"""
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.domain import AuditLedgerModel

GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class ClinicalDomainEvent:
    actor_username: str
    actor_role: str
    action_type: str       # Ej: "FHIR_READ_EHR", "TRIAGE_VITAL_SIGNS_RECORDED", "SYNC_CONFLICT_DETECTED", "ORDER_CREATED"
    resource_type: str     # Ej: "Patient", "Observation", "MedicationRequest", "SyncConflict"
    resource_id: str
    details: str
    client_node: str = "Ambulancia Móvil 07"
    is_critical_alert: bool = False
    timestamp_iso: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ClinicalEventObserver(ABC):
    """Interfaz Observer abstracta para suscriptores de eventos de dominio clínico."""

    @abstractmethod
    def on_clinical_event(self, db: Session, event: ClinicalDomainEvent) -> None:
        pass


class ForensicAuditLedgerObserver(ClinicalEventObserver):
    """
    Suscriptor concreto que materializa el Ledger de Auditoría Forense Inmutable (ADR-03 y ADR-08).
    Cada evento se encadena criptográficamente con el hash SHA-256 del evento inmediato anterior,
    garantizando que cualquier modificación o borrado posterior en la base de datos rompa la cadena.
    """

    @staticmethod
    def compute_entry_hash(
        sequence_number: int,
        actor_username: str,
        actor_role: str,
        action_type: str,
        resource_type: str,
        resource_id: str,
        details: str,
        timestamp_iso: str,
        prev_hash: str,
    ) -> str:
        canonical_payload = (
            f"{sequence_number}|{actor_username}|{actor_role}|{action_type}|"
            f"{resource_type}|{resource_id}|{details}|{timestamp_iso}|{prev_hash}"
        )
        return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

    def on_clinical_event(self, db: Session, event: ClinicalDomainEvent) -> None:
        last_entry = (
            db.query(AuditLedgerModel)
            .order_by(AuditLedgerModel.sequence_number.desc())
            .first()
        )
        if last_entry is None:
            next_seq = 1
            prev_hash = GENESIS_HASH
        else:
            next_seq = last_entry.sequence_number + 1
            prev_hash = last_entry.current_hash

        current_hash = self.compute_entry_hash(
            sequence_number=next_seq,
            actor_username=event.actor_username,
            actor_role=event.actor_role,
            action_type=event.action_type,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            details=event.details,
            timestamp_iso=event.timestamp_iso,
            prev_hash=prev_hash,
        )

        ledger_record = AuditLedgerModel(
            sequence_number=next_seq,
            actor_username=event.actor_username,
            actor_role=event.actor_role,
            action_type=event.action_type,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            details=event.details,
            client_ip_or_node=event.client_node,
            timestamp_iso=event.timestamp_iso,
            prev_hash=prev_hash,
            current_hash=current_hash,
        )
        db.add(ledger_record)
        db.commit()


class CriticalTelemetryAlertObserver(ClinicalEventObserver):
    """
    Suscriptor concreto que escucha eventos clínicos y mantiene un buffer de alertas críticas activas
    para notificar a la consola de Telemedicina y al hospital de destino sin bloquear la transacción.
    """

    def __init__(self) -> None:
        self.recent_critical_alerts: List[Dict[str, str]] = []

    def on_clinical_event(self, db: Session, event: ClinicalDomainEvent) -> None:
        if event.is_critical_alert or "CONFLICT" in event.action_type or "BLOCKED" in event.action_type:
            self.recent_critical_alerts.insert(
                0,
                {
                    "timestamp": event.timestamp_iso,
                    "action_type": event.action_type,
                    "resource_id": event.resource_id,
                    "actor": f"{event.actor_username} ({event.actor_role})",
                    "node": event.client_node,
                    "details": event.details,
                },
            )
            # Conservar las últimas 25 alertas críticas en memoria
            self.recent_critical_alerts = self.recent_critical_alerts[:25]


class ClinicalDomainEventBus:
    """Subject / Publicador del Patrón Observer que administra la suscripción y notificación de eventos."""

    def __init__(self) -> None:
        self._observers: List[ClinicalEventObserver] = []

    def subscribe(self, observer: ClinicalEventObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def publish(self, db: Session, event: ClinicalDomainEvent) -> None:
        for observer in self._observers:
            observer.on_clinical_event(db, event)


# Instancia singleton del bus de eventos de dominio con sus dos observadores registrados
audit_ledger_observer = ForensicAuditLedgerObserver()
critical_alert_observer = CriticalTelemetryAlertObserver()

clinical_event_bus = ClinicalDomainEventBus()
clinical_event_bus.subscribe(audit_ledger_observer)
clinical_event_bus.subscribe(critical_alert_observer)
