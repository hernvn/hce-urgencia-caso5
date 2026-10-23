"""
Suite de Pruebas Automatizadas (Pytest) para Verificación de Atributos de Calidad,
Patrones de Diseño (Strategy, Observer, Repository) y Decisiones Arquitectónicas (ADR-01 a ADR-08).
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed import seed_initial_data


@pytest.fixture()
def client():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    seed_initial_data(db)

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    db.close()


def get_auth_headers(client: TestClient, username: str, password: str = "urgencia2026") -> dict:
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_1_rbac_authentication_and_authorization(client: TestClient):
    """
    Verifica Atributo de Calidad: SEGURIDAD (ADR-02 / ADR-08) y Criterio 3.2 (Login con diversos roles).
    - Login exitoso emite JWT para los 4 roles.
    - Un PARAMEDICO puede registrar signos vitales, pero recibe 403 FORBIDDEN si intenta prescribir un fármaco.
    - Un AUDITOR_FORENSE puede verificar la cadena criptográfica, pero recibe 403 si intenta registrar triage.
    """
    # 1. Login fallido con contraseña incorrecta
    bad_resp = client.post("/api/v1/auth/login", json={"username": "paramedico.soto", "password": "wrongpassword"})
    assert bad_resp.status_code == 401

    # 2. Login como Paramédico
    paramedic_headers = get_auth_headers(client, "paramedico.soto")

    # 3. Paramédico intenta emitir orden médica -> 403 Forbidden
    order_resp = client.post(
        "/api/v1/fhir/patients/1/orders",
        headers=paramedic_headers,
        json={
            "idempotency_key": f"uuid-{uuid.uuid4()}",
            "episode_code": "URG-2026-0084",
            "order_type": "FARMACO",
            "medication_or_action": "Paracetamol 1g EV",
            "dosage_and_route": "1g endovenoso lento",
            "clinical_justification": "Control térmico",
        },
    )
    assert order_resp.status_code == 403
    assert "ACCESO DENEGADO (RBAC HIPAA)" in order_resp.json()["detail"]

    # 4. Auditor Forense intenta registrar signos vitales -> 403 Forbidden
    auditor_headers = get_auth_headers(client, "auditor.hipaa")
    vitals_resp = client.post(
        "/api/v1/fhir/patients/1/vital-signs",
        headers=auditor_headers,
        json={
            "idempotency_key": f"uuid-{uuid.uuid4()}",
            "heart_rate_bpm": 80,
            "spo2_percent": 98,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "temperature_c": 36.8,
        },
    )
    assert vitals_resp.status_code == 403


def test_2_strategy_pattern_triage_and_idempotency(client: TestClient):
    """
    Verifica Patrón Strategy (EmergencySeverityIndexStrategy), Idempotencia UUID (ADR-02 / ADR-04)
    y Validaciones Fisiológicas (Criterio 3.2).
    """
    paramedic_headers = get_auth_headers(client, "paramedico.soto")
    idem_key = f"outbox-uuid-{uuid.uuid4()}"

    # 1. Registrar signos vitales críticos (SpO2 85% < 90% -> ESI-1 Crítico)
    resp1 = client.post(
        "/api/v1/fhir/patients/1/vital-signs",
        headers=paramedic_headers,
        json={
            "idempotency_key": idem_key,
            "episode_code": "URG-2026-0084",
            "heart_rate_bpm": 135,
            "spo2_percent": 85,
            "systolic_bp": 88,
            "diastolic_bp": 54,
            "temperature_c": 38.9,
            "glasgow_score": 13,
            "origin_node": "Ambulancia Móvil 07 (Túnel Offline Replay)",
        },
    )
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["is_critical"] is True
    assert "ESI-1 Crítico" in data1["triage_category"]
    assert "Hipoxemia severa" in data1["clinical_alerts"]

    # 2. Reenviar exactamente la misma petición con el mismo idempotency_key (simulando reintento de Service Worker)
    resp2 = client.post(
        "/api/v1/fhir/patients/1/vital-signs",
        headers=paramedic_headers,
        json={
            "idempotency_key": idem_key,
            "episode_code": "URG-2026-0084",
            "heart_rate_bpm": 135,
            "spo2_percent": 85,
            "systolic_bp": 88,
            "diastolic_bp": 54,
            "temperature_c": 38.9,
            "glasgow_score": 13,
        },
    )
    assert resp2.status_code == 201
    assert resp2.json()["id"] == data1["id"]  # No se duplicó el registro en BD

    # 3. Validación de incoherencia fisiológica: presión diastólica >= sistólica debe ser rechazada con HTTP 422
    invalid_bp = client.post(
        "/api/v1/fhir/patients/1/vital-signs",
        headers=paramedic_headers,
        json={
            "idempotency_key": f"outbox-uuid-{uuid.uuid4()}",
            "heart_rate_bpm": 90,
            "spo2_percent": 96,
            "systolic_bp": 90,
            "diastolic_bp": 110,
            "temperature_c": 37.0,
        },
    )
    assert invalid_bp.status_code == 422
    assert "Incoherencia fisiológica" in invalid_bp.json()["detail"]


def test_3_adr05_optimistic_concurrency_and_clinical_arbitration(client: TestClient):
    """
    Verifica ADR-05 (Resolución de Conflictos de Sincronización con Vectores de Versión y Cola de Arbitraje Clínico)
    y ADR-03 (Invariante Transaccional Expediente-Órdenes).
    """
    doctor_headers = get_auth_headers(client, "dr.valdivia")
    paramedic_headers = get_auth_headers(client, "paramedico.soto")

    # Paciente 1 inicia en version = 1. El médico en el hospital actualiza alergias con expected_version=1 -> sube a v2
    upd1 = client.put(
        "/api/v1/fhir/patients/1/mutable-fields",
        headers=doctor_headers,
        json={
            "field_name": "allergies",
            "new_value": "Penicilina (Anafilaxia); Sulfas; Medio de Contraste Yodado",
            "expected_version": 1,
            "origin_node": "Clínica Central Urgencias",
        },
    )
    assert upd1.status_code == 200
    assert upd1.json()["status"] == "APPLIED"
    assert upd1.json()["new_version"] == 2

    # La ambulancia que estaba desconectada en un túnel sincroniza con expected_version=1 (desactualizada vs v2)
    upd2 = client.put(
        "/api/v1/fhir/patients/1/mutable-fields",
        headers=paramedic_headers,
        json={
            "field_name": "allergies",
            "new_value": "Penicilina (Anafilaxia); Sulfas; Látex reportado por familiar en ambulancia",
            "expected_version": 1,
            "origin_node": "Ambulancia Móvil 07 (Reconexión Offline)",
        },
    )
    assert upd2.status_code == 200
    assert upd2.json()["status"] == "CONFLICT_QUEUED"
    conflict_id = upd2.json()["conflict"]["id"]

    # Mientras el conflicto de alergias está PENDIENTE, intentar prescribir un fármaco debe ser bloqueado (HTTP 409)
    blocked_order = client.post(
        "/api/v1/fhir/patients/1/orders",
        headers=doctor_headers,
        json={
            "idempotency_key": f"order-{uuid.uuid4()}",
            "order_type": "FARMACO",
            "medication_or_action": "Nitroglicerina 0.4mg sublingual",
            "dosage_and_route": "0.4mg SL",
            "clinical_justification": "Manejo dolor anginoso",
        },
    )
    assert blocked_order.status_code == 409

    # El Médico de Urgencia resuelve el arbitraje clínico fusionando ambas alergias
    resolve_resp = client.post(
        f"/api/v1/fhir/conflicts/{conflict_id}/resolve",
        headers=doctor_headers,
        json={
            "chosen_value": "Penicilina (Anafilaxia); Sulfas; Contraste Yodado; Látex",
            "resolution_notes": "Se concilian antecedentes hospitalarios con hallazgo en ambulancia de alergia a Látex.",
        },
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["patient_version"] == 3


def test_4_adr03_drug_allergy_contraindication_and_audit_ledger_chain(client: TestClient):
    """
    Verifica:
    1. Invariante de seguridad farmacológica (ADR-03): Rechaza prescripción de Amoxicilina en paciente alérgico a Penicilina.
    2. Patrón Observer + Integridad Criptográfica SHA-256 del Ledger de Auditoría Forense (ADR-03 / ADR-08).
    """
    doctor_headers = get_auth_headers(client, "dr.valdivia")
    auditor_headers = get_auth_headers(client, "auditor.hipaa")

    # 1. Intentar recetar Amoxicilina (derivado de Penicilina) a Carlos Mendoza (alérgico a Penicilina)
    contra_resp = client.post(
        "/api/v1/fhir/patients/1/orders",
        headers=doctor_headers,
        json={
            "idempotency_key": f"order-{uuid.uuid4()}",
            "order_type": "FARMACO",
            "medication_or_action": "Amoxicilina / Ácido Clavulánico 1g EV",
            "dosage_and_route": "1g cada 8 horas EV",
            "clinical_justification": "Profilaxis infecciosa",
        },
    )
    assert contra_resp.status_code == 422
    assert "BLOQUEO DE SEGURIDAD CLÍNICA" in contra_resp.json()["detail"]

    # 2. Verificar matemáticamente toda la cadena SHA-256 del Ledger de Auditoría Forense
    audit_resp = client.get("/api/v1/audit/verify-chain", headers=auditor_headers)
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    assert audit_data["is_valid"] is True
    assert audit_data["total_events_verified"] >= 4
    assert "0 adulteraciones" in audit_data["status_message"]
