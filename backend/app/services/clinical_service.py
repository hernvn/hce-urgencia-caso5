"""
Capa de Aplicación (Lógica de Negocio del Servicio Cohesivo Expediente-Órdenes según ADR-03).
Orquesta los Patrones Strategy, Observer y Repository manteniendo trazabilidad forense HIPAA/FHIR.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.domain import MedicalOrderModel, PatientModel, UserModel, VitalSignObservationModel
from app.observers.audit_observer import ClinicalDomainEvent, clinical_event_bus
from app.repositories.ehr_repository import PatientEHRRepository
from app.schemas.fhir_schemas import (
    ConflictResolutionRequest,
    MedicalOrderCreateRequest,
    MutableFieldUpdateRequest,
    VitalSignCreateRequest,
)
from app.strategies.clinical_strategies import (
    AppendOnlyCRDTGSetStrategy,
    ClinicalTriageStrategy,
    DrugSafetyGuardStrategy,
    EmergencySeverityIndexStrategy,
    OptimisticConcurrencyClinicalArbitrationStrategy,
)


class ClinicalEHRService:
    """
    Servicio de dominio que implementa el agregado Expediente Clínico - Órdenes (ADR-03).
    Recibe por inyección de dependencias la estrategia de Triage Clínico y las estrategias de resolución de sincronización.
    """

    def __init__(
        self,
        db: Session,
        triage_strategy: ClinicalTriageStrategy | None = None,
    ) -> None:
        self.db = db
        self.repo = PatientEHRRepository(db)
        self.triage_strategy = triage_strategy or EmergencySeverityIndexStrategy()
        self.append_only_strategy = AppendOnlyCRDTGSetStrategy()
        self.mutable_sync_strategy = OptimisticConcurrencyClinicalArbitrationStrategy()

    def get_patient_ehr(self, patient_id: int, actor: UserModel, client_node: str = "Consola Clínica") -> PatientModel:
        patient = self.repo.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recurso FHIR Patient/{patient_id} no existe en el registro maestro.",
            )

        # Toda lectura de HCE genera un evento forense inmutable (ADR-03 / Sección 3.3 Escenario 4°)
        clinical_event_bus.publish(
            self.db,
            ClinicalDomainEvent(
                actor_username=actor.username,
                actor_role=actor.role,
                action_type="FHIR_READ_EHR",
                resource_type="Patient",
                resource_id=f"Patient/{patient.id} ({patient.rut})",
                details=f"Acceso a expediente clínico completo de {patient.full_name} (v{patient.version})",
                client_node=client_node,
            ),
        )
        return patient

    def record_vital_signs_triage(
        self,
        patient_id: int,
        payload: VitalSignCreateRequest,
        actor: UserModel,
    ) -> tuple[VitalSignObservationModel, bool]:
        """
        Registra signos vitales (Append-Only CRDT G-Set según ADR-05) garantizando idempotencia (ADR-02 / ADR-04)
        y clasificando el riesgo vital mediante el Patrón Strategy (`EmergencySeverityIndexStrategy`).
        Retorna (observación, fue_idempotente_duplicado).
        """
        patient = self.repo.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente ID {patient_id} no encontrado.",
            )

        # Verificación de clave de idempotencia UUID (Store-and-Forward Outbox ADR-02 / ADR-04)
        existing = self.repo.get_vital_sign_by_idempotency_key(payload.idempotency_key)
        if existing:
            clinical_event_bus.publish(
                self.db,
                ClinicalDomainEvent(
                    actor_username=actor.username,
                    actor_role=actor.role,
                    action_type="IDEMPOTENT_REPLAY_IGNORED",
                    resource_type="Observation",
                    resource_id=f"Observation/{existing.id}",
                    details=f"Reintento de red detectado con idempotency_key={payload.idempotency_key}. Duplicado prevenido.",
                    client_node=payload.origin_node,
                ),
            )
            return existing, True

        # Evaluar estrategia de Triage Clínico (Patrón Strategy)
        triage_eval = self.triage_strategy.evaluate(
            heart_rate_bpm=payload.heart_rate_bpm,
            spo2_percent=payload.spo2_percent,
            systolic_bp=payload.systolic_bp,
            diastolic_bp=payload.diastolic_bp,
            temperature_c=payload.temperature_c,
            glasgow_score=payload.glasgow_score,
        )

        observation = VitalSignObservationModel(
            idempotency_key=payload.idempotency_key,
            patient_id=patient.id,
            episode_code=payload.episode_code,
            heart_rate_bpm=payload.heart_rate_bpm,
            spo2_percent=payload.spo2_percent,
            systolic_bp=payload.systolic_bp,
            diastolic_bp=payload.diastolic_bp,
            temperature_c=payload.temperature_c,
            glasgow_score=payload.glasgow_score,
            triage_category=triage_eval.triage_category,
            clinical_alerts=triage_eval.formatted_alerts,
            is_critical=triage_eval.is_critical,
            recorded_by=actor.full_name,
            recorded_role=actor.role,
            origin_node=payload.origin_node,
            clinical_notes=payload.clinical_notes,
        )
        saved = self.repo.save_vital_sign_observation(observation)

        # Notificar al bus de eventos (Patrón Observer -> Ledger Forense + Alerta Crítica)
        clinical_event_bus.publish(
            self.db,
            ClinicalDomainEvent(
                actor_username=actor.username,
                actor_role=actor.role,
                action_type="TRIAGE_VITAL_SIGNS_RECORDED",
                resource_type="Observation",
                resource_id=f"Observation/{saved.id}",
                details=(
                    f"Signos vitales registrados para {patient.full_name}: "
                    f"FC={saved.heart_rate_bpm} lpm, SpO2={saved.spo2_percent}%, "
                    f"PA={saved.systolic_bp}/{saved.diastolic_bp} mmHg, T={saved.temperature_c}°C -> "
                    f"[{saved.triage_category}] {saved.clinical_alerts}"
                ),
                client_node=payload.origin_node,
                is_critical_alert=saved.is_critical,
            ),
        )
        return saved, False

    def update_mutable_clinical_field(
        self,
        patient_id: int,
        payload: MutableFieldUpdateRequest,
        actor: UserModel,
    ) -> dict:
        """
        Actualiza un campo mutable del expediente (alergias, diagnóstico activo, plan de tratamiento)
        aplicando la Estrategia de Concurrencia Optimista con Arbitraje Clínico (ADR-05).
        """
        patient = self.repo.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente ID {patient_id} no encontrado.",
            )

        can_merge, strategy_msg = self.mutable_sync_strategy.can_auto_merge(
            client_version=payload.expected_version,
            server_version=patient.version,
        )

        current_server_val = getattr(patient, payload.field_name)

        if can_merge:
            updated_patient = self.repo.update_mutable_field(
                patient=patient,
                field_name=payload.field_name,
                new_value=payload.new_value,
            )
            clinical_event_bus.publish(
                self.db,
                ClinicalDomainEvent(
                    actor_username=actor.username,
                    actor_role=actor.role,
                    action_type="FHIR_MUTABLE_FIELD_UPDATED",
                    resource_type="Patient",
                    resource_id=f"Patient/{patient.id}",
                    details=(
                        f"Actualización de '{payload.field_name}' (v{payload.expected_version} -> v{updated_patient.version}): "
                        f"'{current_server_val}' => '{payload.new_value}'"
                    ),
                    client_node=payload.origin_node,
                ),
            )
            return {
                "status": "APPLIED",
                "message": strategy_msg,
                "new_version": updated_patient.version,
                "conflict": None,
            }

        # Conflicto detectado (ADR-05): No sobrescribir silenciosamente. Desviar a Cola de Arbitraje Clínico.
        conflict = self.repo.create_sync_conflict(
            patient=patient,
            field_name=payload.field_name,
            client_expected_version=payload.expected_version,
            server_current_version=patient.version,
            server_value=current_server_val,
            client_proposed_value=payload.new_value,
            submitted_by=f"{actor.full_name} ({actor.role})",
            origin_node=payload.origin_node,
        )

        clinical_event_bus.publish(
            self.db,
            ClinicalDomainEvent(
                actor_username=actor.username,
                actor_role=actor.role,
                action_type="SYNC_CONFLICT_ARBITRATION_QUEUED",
                resource_type="SyncConflict",
                resource_id=f"SyncConflict/{conflict.id}",
                details=(
                    f"CONFLICTO ADR-05 en '{payload.field_name}' de {patient.full_name}: "
                    f"Cliente envió v{payload.expected_version} ('{payload.new_value}'), pero servidor está en "
                    f"v{patient.version} ('{current_server_val}'). Congelado para arbitraje médico."
                ),
                client_node=payload.origin_node,
                is_critical_alert=True,
            ),
        )
        return {
            "status": "CONFLICT_QUEUED",
            "message": strategy_msg,
            "new_version": patient.version,
            "conflict": {
                "id": conflict.id,
                "field_name": conflict.field_name,
                "client_expected_version": conflict.client_expected_version,
                "server_current_version": conflict.server_current_version,
                "server_value": conflict.server_value,
                "client_proposed_value": conflict.client_proposed_value,
                "status": conflict.status,
            },
        }

    def resolve_sync_conflict(
        self,
        conflict_id: int,
        payload: ConflictResolutionRequest,
        actor: UserModel,
    ) -> dict:
        """
        Permite únicamente a un Médico (Urgencia o Teleconsultor) resolver manualmente un conflicto en la cola de arbitraje (ADR-05).
        """
        conflict = self.repo.get_conflict_by_id(conflict_id)
        if not conflict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conflicto de sincronización #{conflict_id} no existe.",
            )
        if conflict.status == "RESUELTO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El conflicto #{conflict_id} ya fue resuelto previamente por {conflict.resolved_by}.",
            )

        patient, resolved_conflict = self.repo.resolve_conflict(
            conflict=conflict,
            chosen_value=payload.chosen_value,
            resolved_by=f"{actor.full_name} ({actor.role})",
            resolution_notes=payload.resolution_notes,
        )

        clinical_event_bus.publish(
            self.db,
            ClinicalDomainEvent(
                actor_username=actor.username,
                actor_role=actor.role,
                action_type="SYNC_CONFLICT_RESOLVED",
                resource_type="SyncConflict",
                resource_id=f"SyncConflict/{resolved_conflict.id}",
                details=(
                    f"Arbitraje clínico ADR-05 completado sobre '{resolved_conflict.field_name}' de {patient.full_name} "
                    f"(nueva v{patient.version}): Valor definitivo='{payload.chosen_value}'. "
                    f"Justificación: {payload.resolution_notes}"
                ),
                client_node=actor.facility,
            ),
        )
        return {
            "status": "RESOLVED",
            "patient_version": patient.version,
            "resolved_field": resolved_conflict.field_name,
            "chosen_value": payload.chosen_value,
        }

    def create_medical_order(
        self,
        patient_id: int,
        payload: MedicalOrderCreateRequest,
        actor: UserModel,
    ) -> MedicalOrderModel:
        """
        Emite una orden médica o prescripción electrónica dentro del servicio cohesivo Expediente-Órdenes (ADR-03).
        Valida transaccionalmente que el fármaco no colisione con las alergias del paciente y que no existan conflictos
        de alergias pendientes de arbitraje sin resolver.
        """
        patient = self.repo.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente ID {patient_id} no encontrado.",
            )

        # Idempotencia por clave UUID
        existing = self.repo.get_order_by_idempotency_key(payload.idempotency_key)
        if existing:
            return existing

        # Invariante 1 (ADR-05 + ADR-03): Si hay un conflicto pendiente en la lista de alergias, bloquear prescripciones farmacológicas
        if payload.order_type == "FARMACO" and patient.has_pending_conflict:
            pending_allergy_conflicts = [
                c for c in patient.conflicts if c.status == "PENDIENTE" and c.field_name == "allergies"
            ]
            if pending_allergy_conflicts:
                clinical_event_bus.publish(
                    self.db,
                    ClinicalDomainEvent(
                        actor_username=actor.username,
                        actor_role=actor.role,
                        action_type="ORDER_BLOCKED_PENDING_ARBITRATION",
                        resource_type="MedicationRequest",
                        resource_id=f"Patient/{patient.id}",
                        details=(
                            f"Intento de prescribir '{payload.medication_or_action}' bloqueado: "
                            "existe un conflicto de sincronización pendiente de arbitraje en el campo 'allergies'."
                        ),
                        client_node=actor.facility,
                        is_critical_alert=True,
                    ),
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "INVARIANCIA CLÍNICA (ADR-03 / ADR-05): No se permite emitir órdenes farmacológicas mientras "
                        "exista un conflicto de sincronización pendiente de arbitraje en las alergias del paciente. "
                        "Resuelva primero el arbitraje clínico pendiente."
                    ),
                )

        # Invariante 2 (ADR-03): Verificación cruzada inmediata contra alergias registradas en el expediente
        if payload.order_type == "FARMACO":
            is_safe, safety_msg = DrugSafetyGuardStrategy.check_allergy_contraindication(
                patient_allergies=patient.allergies,
                proposed_medication=payload.medication_or_action,
            )
            if not is_safe:
                clinical_event_bus.publish(
                    self.db,
                    ClinicalDomainEvent(
                        actor_username=actor.username,
                        actor_role=actor.role,
                        action_type="DRUG_ALLERGY_CONTRAINDICATION_BLOCKED",
                        resource_type="MedicationRequest",
                        resource_id=f"Patient/{patient.id}",
                        details=safety_msg,
                        client_node=actor.facility,
                        is_critical_alert=True,
                    ),
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=safety_msg,
                )

        order = MedicalOrderModel(
            idempotency_key=payload.idempotency_key,
            patient_id=patient.id,
            episode_code=payload.episode_code,
            order_type=payload.order_type,
            medication_or_action=payload.medication_or_action,
            dosage_and_route=payload.dosage_and_route,
            clinical_justification=payload.clinical_justification,
            teleconsultation_room_id=payload.teleconsultation_room_id,
            author_name=actor.full_name,
            author_role=actor.role,
        )
        saved_order = self.repo.save_medical_order(order)

        clinical_event_bus.publish(
            self.db,
            ClinicalDomainEvent(
                actor_username=actor.username,
                actor_role=actor.role,
                action_type="MEDICAL_ORDER_CREATED",
                resource_type="MedicationRequest",
                resource_id=f"MedicationRequest/{saved_order.id}",
                details=(
                    f"Orden [{saved_order.order_type}] emitida para {patient.full_name}: "
                    f"{saved_order.medication_or_action} ({saved_order.dosage_and_route}). "
                    f"Justificación: {saved_order.clinical_justification}"
                ),
                client_node=actor.facility,
            ),
        )
        return saved_order
