"""
Inicializador de Datos Semilla (Seed Data) del Caso 5:
- 4 Usuarios con Roles diferenciados (PARAMEDICO, MEDICO_URGENCIA, MEDICO_TELECONSULTOR, AUDITOR_FORENSE)
- 2 Pacientes con expedientes clínicos FHIR R4 realistas (incluyendo a Carlos Mendoza Silva de los mockups de la Evaluación 1, página 6)
- Observaciones iniciales de signos vitales, órdenes previas y bloque génesis en el Ledger Forense.
"""
from sqlalchemy.orm import Session

from app.database import hash_password
from app.models.domain import MedicalOrderModel, PatientModel, UserModel, VitalSignObservationModel
from app.observers.audit_observer import ClinicalDomainEvent, clinical_event_bus


def seed_initial_data(db: Session) -> None:
    if db.query(UserModel).count() > 0:
        return

    # 1. Crear los 4 usuarios con roles diferenciados (Requisito obligatorio de Rúbrica 3.2)
    demo_users = [
        UserModel(
            username="paramedico.soto",
            hashed_password=hash_password("urgencia2026"),
            full_name="Camila Soto Rivas (TENS / Paramédico)",
            role="PARAMEDICO",
            facility="Ambulancia Avanzada SAMU/Red Móvil 07 — Ruta Sur",
            specialty="Soporte Vital Avanzado Prehospitalario (APHA)",
        ),
        UserModel(
            username="dr.valdivia",
            hashed_password=hash_password("urgencia2026"),
            full_name="Dr. Martín Valdivia Rojas",
            role="MEDICO_URGENCIA",
            facility="Clínica Alta Complejidad Central — Box Reanimación 01",
            specialty="Medicina de Urgencia y Cuidados Críticos",
        ),
        UserModel(
            username="dra.herrera",
            hashed_password=hash_password("urgencia2026"),
            full_name="Dra. Elena Herrera Guzmán",
            role="MEDICO_TELECONSULTOR",
            facility="Centro Comando Telemedicina Red Nacional (SFU Sala 04)",
            specialty="Cardiología Intervencional y Telemedicina",
        ),
        UserModel(
            username="auditor.hipaa",
            hashed_password=hash_password("urgencia2026"),
            full_name="Ing. Roberto Domínguez (Oficial de Privacidad OPD/HIPAA)",
            role="AUDITOR_FORENSE",
            facility="Unidad de Cumplimiento Normativo y Auditoría Forense",
            specialty="Auditoría Criptográfica HIPAA / HL7 FHIR R4",
        ),
    ]
    db.add_all(demo_users)
    db.commit()

    # 2. Crear Pacientes (fiel al Mockup de la Evaluación 1, página 6: Carlos Mendoza Silva, 68 años)
    patient_1 = PatientModel(
        rut="8.452.910-K",
        full_name="Carlos Mendoza Silva",
        birth_date="14-05-1958",
        age=68,
        sex="Masculino",
        blood_type="O Rh+",
        chronic_conditions="Hipertensión Arterial Crónica; Diabetes Mellitus Tipo 2; Cardiopatía Coronaria",
        current_medications="Metformina 850mg c/12h; Enalapril 10mg c/12h; Atorvastatina 20mg/día",
        allergies="Penicilina (Anafilaxia documentada); Sulfas",
        active_diagnosis="Síndrome Coronario Agudo en traslado + Insuficiencia Respiratoria Aguda",
        treatment_plan="Oxigenoterapia por mascarilla reservorio 4 L/min; Vía venosa periférica permeable; Monitorización ECG 12 derivaciones",
        version=1,
        has_pending_conflict=False,
    )

    patient_2 = PatientModel(
        rut="14.920.311-4",
        full_name="Lucía Fernández Morales",
        birth_date="22-11-1982",
        age=43,
        sex="Femenino",
        blood_type="A Rh-",
        chronic_conditions="Asma Bronquial Moderada Persistente",
        current_medications="Budesonida/Formoterol inhalador SOS",
        allergies="AINES (Broncoespasmo severo por Ketorolaco/Ibuprofeno)",
        active_diagnosis="Crisis Asmática Moderada en observación en Centro Ambulatorio",
        treatment_plan="Nebulización con Salbutamol + Bromuro de Ipratropio; Control SpO2 seriado",
        version=1,
        has_pending_conflict=False,
    )

    db.add_all([patient_1, patient_2])
    db.commit()
    db.refresh(patient_1)
    db.refresh(patient_2)

    # 3. Signos vitales iniciales del traslado en ambulancia (fiel al Mockup pág. 6: FC 118, SpO2 89%, PA 92/58, Temp 38.7)
    initial_obs = VitalSignObservationModel(
        idempotency_key="seed-uuid-obs-carlos-0001",
        patient_id=patient_1.id,
        episode_code="URG-2026-0084",
        heart_rate_bpm=118,
        spo2_percent=89,
        systolic_bp=92,
        diastolic_bp=58,
        temperature_c=38.7,
        glasgow_score=14,
        triage_category="ESI-1 Crítico (Riesgo Vital Inmediato)",
        clinical_alerts=(
            "ALERTA CRÍTICA: Hipoxemia severa (SpO2 89% < 90%). Intervención inmediata de vía aérea | "
            "ALERTA: Taquicardia/Bradicardia sinusal (FC 118 lpm) | "
            "ALERTA: Alteración tensional (PA 92/58 mmHg) | "
            "ALERTA SIRS/Sepsis: Disregulación térmica (38.7 °C)"
        ),
        is_critical=True,
        recorded_by="Camila Soto Rivas (TENS / Paramédico)",
        recorded_role="PARAMEDICO",
        origin_node="Ambulancia Móvil 07 — Ruta Sur (Telemetría MQTT)",
        clinical_notes="Paciente diaforético, disnea en reposo durante traslado por túnel urbano.",
    )
    db.add(initial_obs)

    # 4. Orden inicial de teleconsulta (fiel al Mockup pág. 6: "Administren oxígeno a 4 litros por minuto. Preparen el acceso venoso.")
    initial_order = MedicalOrderModel(
        idempotency_key="seed-uuid-order-carlos-0001",
        patient_id=patient_1.id,
        episode_code="URG-2026-0084",
        order_type="TELECONSULTA",
        medication_or_action="Oxígeno suplementario + Acceso venoso periférico #18G",
        dosage_and_route="Oxígeno a 4 L/min por naricera/mascarilla; Vía venosa antecubital",
        clinical_justification="Indicación en vivo durante Teleconsulta de Urgencia por hipoxemia SpO2 89% e hipotensión limítrofe 92/58 mmHg.",
        teleconsultation_room_id="SFU-SALA-MOVIL-07-URG",
        author_name="Dra. Elena Herrera Guzmán",
        author_role="MEDICO_TELECONSULTOR",
    )
    db.add(initial_order)
    db.commit()

    # 5. Registrar eventos iniciales en el Ledger Forense Inmutable (Patrón Observer)
    clinical_event_bus.publish(
        db,
        ClinicalDomainEvent(
            actor_username="SYSTEM_GENESIS",
            actor_role="KERNEL_HSM",
            action_type="LEDGER_GENESIS_INITIALIZED",
            resource_type="AuditLedger",
            resource_id="Chain/Root-2026",
            details="Inicialización de cadena forense inmutable SHA-256 (Cumplimiento HIPAA Security Rule y HL7 FHIR AuditEvent).",
            client_node="Centro de Datos On-Premise Consorcio (HSM)",
        ),
    )
    clinical_event_bus.publish(
        db,
        ClinicalDomainEvent(
            actor_username="paramedico.soto",
            actor_role="PARAMEDICO",
            action_type="TRIAGE_VITAL_SIGNS_RECORDED",
            resource_type="Observation",
            resource_id=f"Observation/{initial_obs.id}",
            details="Triage inicial en ambulancia para Carlos Mendoza Silva: SpO2 89% (Crítica), FC 118 lpm, PA 92/58 mmHg, T 38.7°C.",
            client_node="Ambulancia Móvil 07 — Ruta Sur",
            is_critical_alert=True,
        ),
    )
    clinical_event_bus.publish(
        db,
        ClinicalDomainEvent(
            actor_username="dra.herrera",
            actor_role="MEDICO_TELECONSULTOR",
            action_type="TELEMEDICINE_DIRECTIVE_ISSUED",
            resource_type="MedicationRequest",
            resource_id=f"MedicationRequest/{initial_order.id}",
            details="Teleconsulta SFU Sala Móvil 07: 'Administren oxígeno a 4 litros por minuto. Preparen el acceso venoso.'",
            client_node="Estación Teleconsulta SFU-04",
        ),
    )
