"""
PATRÓN DE DISEÑO #1: STRATEGY (Comportamiento)
----------------------------------------------
Problema que resuelve:
En el sistema de HCE y Telemedicina de Urgencia (Caso 5), existen dos familias de algoritmos críticos que varían
según el contexto clínico y el tipo de dato sincronizado:
1. Estrategia de Clasificación de Triage Clínico y Detección de Alertas (ESI - Emergency Severity Index).
2. Estrategia de Sincronización y Resolución de Conflictos (ADR-05: Estrategia Dual):
   - Datos Append-Only (Signos vitales, telemetría): Estrategia CRDT G-Set (fusión automática idempotente).
   - Campos Mutables (Alergias, diagnóstico activo, plan de tratamiento): Estrategia de Concurrencia Optimista
     con desvío a Cola de Arbitraje Clínico ante colisión de vectores de versión.

Justificación arquitectónica:
Evita condicionales monolíticos acoplados en los controladores o servicios, cumple el Principio Abierto/Cerrado (OCP)
y permite certificar unitariamente cada regla clínica y de sincronización sin levantar la interfaz ni la red.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class TriageEvaluationResult:
    triage_category: str
    is_critical: bool
    alerts: List[str]

    @property
    def formatted_alerts(self) -> str:
        return " | ".join(self.alerts) if self.alerts else "Sin alertas fisiológicas críticas"


class ClinicalTriageStrategy(ABC):
    """Interfaz Strategy abstracta para algoritmos de clasificación de severidad de urgencia."""

    @abstractmethod
    def evaluate(
        self,
        heart_rate_bpm: int,
        spo2_percent: int,
        systolic_bp: int,
        diastolic_bp: int,
        temperature_c: float,
        glasgow_score: int,
    ) -> TriageEvaluationResult:
        pass


class EmergencySeverityIndexStrategy(ClinicalTriageStrategy):
    """
    Implementación concreta del protocolo Emergency Severity Index (ESI) + NEWS2 para ambulancias de alta complejidad.
    Detecta hipoxemia crítica (SpO2 < 90%), taquicardia/bradicardia extrema, hipotensión de shock o crisis hipertensiva.
    """

    def evaluate(
        self,
        heart_rate_bpm: int,
        spo2_percent: int,
        systolic_bp: int,
        diastolic_bp: int,
        temperature_c: float,
        glasgow_score: int,
    ) -> TriageEvaluationResult:
        alerts: List[str] = []
        severity_level = 3  # 1 = ESI-1 Crítico Inmediato, 2 = ESI-2 Alto Riesgo, 3 = ESI-3 Estable

        # Evaluación de oxigenación (SpO2)
        if spo2_percent < 90:
            alerts.append(f"ALERTA CRÍTICA: Hipoxemia severa (SpO2 {spo2_percent}% < 90%). Intervención inmediata de vía aérea")
            severity_level = min(severity_level, 1)
        elif spo2_percent < 94:
            alerts.append(f"PRECAUCIÓN: Desaturación moderada (SpO2 {spo2_percent}%). Suplementar O2")
            severity_level = min(severity_level, 2)

        # Evaluación hemodinámica (Frecuencia Cardíaca)
        if heart_rate_bpm >= 130 or heart_rate_bpm <= 45:
            alerts.append(f"ALERTA CRÍTICA: Inestabilidad eléctrica/hemodinámica (FC {heart_rate_bpm} lpm)")
            severity_level = min(severity_level, 1)
        elif heart_rate_bpm > 105 or heart_rate_bpm < 55:
            alerts.append(f"ALERTA: Taquicardia/Bradicardia sinusal (FC {heart_rate_bpm} lpm)")
            severity_level = min(severity_level, 2)

        # Evaluación de perfusión (Presión Arterial)
        if systolic_bp < 90 or systolic_bp >= 200 or diastolic_bp >= 120:
            alerts.append(f"ALERTA CRÍTICA: Compromiso de perfusión / Crisis vascular (PA {systolic_bp}/{diastolic_bp} mmHg)")
            severity_level = min(severity_level, 1)
        elif systolic_bp < 100 or systolic_bp >= 160:
            alerts.append(f"ALERTA: Alteración tensional (PA {systolic_bp}/{diastolic_bp} mmHg)")
            severity_level = min(severity_level, 2)

        # Evaluación térmica y neurológica
        if temperature_c >= 38.5 or temperature_c < 35.0:
            alerts.append(f"ALERTA SIRS/Sepsis: Disregulación térmica ({temperature_c:.1f} °C)")
            severity_level = min(severity_level, 2)

        if glasgow_score <= 12:
            alerts.append(f"ALERTA NEUROLÓGICA CRÍTICA: Compromiso de conciencia (Glasgow {glasgow_score}/15)")
            severity_level = min(severity_level, 1)
        elif glasgow_score < 15:
            alerts.append(f"OBSERVACIÓN NEUROLÓGICA: Glasgow {glasgow_score}/15")
            severity_level = min(severity_level, 2)

        category_map = {
            1: "ESI-1 Crítico (Riesgo Vital Inmediato)",
            2: "ESI-2 Alto Riesgo (Urgencia Prioritaria)",
            3: "ESI-3 Estable (Urgencia Menor)",
        }
        return TriageEvaluationResult(
            triage_category=category_map[severity_level],
            is_critical=(severity_level == 1),
            alerts=alerts,
        )


class SyncResolutionStrategy(ABC):
    """
    Interfaz Strategy para la resolución de sincronización offline-first según el tipo de dato clínico (ADR-05).
    """

    @abstractmethod
    def can_auto_merge(self, client_version: int, server_version: int) -> Tuple[bool, str]:
        pass


class AppendOnlyCRDTGSetStrategy(SyncResolutionStrategy):
    """
    Estrategia para series Append-Only (Signos vitales, telemetría, eventos de auditoría).
    Por propiedad de conmutatividad e idempotencia (UUID), siempre se fusiona automáticamente sin bloqueo.
    """

    def can_auto_merge(self, client_version: int, server_version: int) -> Tuple[bool, str]:
        return True, "CRDT G-Set Append-Only: Fusión automática conmutativa garantizada por clave de idempotencia UUID."


class OptimisticConcurrencyClinicalArbitrationStrategy(SyncResolutionStrategy):
    """
    Estrategia para campos mutables críticos (Alergias, Diagnóstico Activo, Plan de Tratamiento) según ADR-05.
    Si el vector de versión del cliente difiere de la versión actual del servidor, prohíbe la sobrescritura
    ("Last-Write-Wins" está prohibido en clínica) y desvía la escritura a la cola de arbitraje médico.
    """

    def can_auto_merge(self, client_version: int, server_version: int) -> Tuple[bool, str]:
        if client_version == server_version:
            return True, f"Versión coincidente (v{server_version} -> v{server_version + 1}): Actualización atómica aplicada."
        return (
            False,
            f"Colisión de versión detectada (Cliente v{client_version} vs Servidor v{server_version}). "
            "Según ADR-05, se congela la sobrescritura automática y se desvía a la Cola de Arbitraje Clínico.",
        )


class DrugSafetyGuardStrategy:
    """
    Verifica invariantes de negocio entre el Expediente Clínico (alergias) y las Órdenes Médicas (ADR-03).
    Impide prescribir un fármaco contraindicado por alergia registrada en el expediente.
    """

    CONTRAINDICATION_GROUPS = {
        "penicilina": ["penicilina", "amoxicilina", "ampicilina", " betalactámico", "piperacilina"],
        "aines": ["ketorolaco", "ibuprofeno", "diclofenaco", "naproxeno", "aspirina", "metamizol"],
        "sulfas": ["sulfametoxazol", "cotrimoxazol", "furosemida"],
        "yodo": ["contraste yodado", "amiodarona", "povidona"],
    }

    @classmethod
    def check_allergy_contraindication(cls, patient_allergies: str, proposed_medication: str) -> Tuple[bool, str]:
        allergies_lower = patient_allergies.lower()
        med_lower = proposed_medication.lower()

        for allergy_key, related_drugs in cls.CONTRAINDICATION_GROUPS.items():
            if allergy_key in allergies_lower:
                for drug in related_drugs:
                    if drug in med_lower:
                        return (
                            False,
                            f"BLOQUEO DE SEGURIDAD CLÍNICA (Invariante ADR-03): El paciente registra alergia severa a "
                            f"'{allergy_key.upper()}'. La prescripción de '{proposed_medication}' pertenece al grupo "
                            f"farmacológico contraindicado y ha sido rechazada transaccionalmente.",
                        )
        # Verificación directa de subcadena
        for token in [t.strip().lower() for t in patient_allergies.replace(",", ";").split(";") if len(t.strip()) >= 4]:
            if token != "ninguna conocida" and token in med_lower:
                return (
                    False,
                    f"BLOQUEO DE SEGURIDAD CLÍNICA (Invariante ADR-03): El fármaco '{proposed_medication}' "
                    f"colisiona directamente con la alergia registrada ('{token}').",
                )

        return True, "Verificación farmacológica superada sin contraindicaciones."
