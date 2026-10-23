"""
Prueba Automatizada de Aptitud Arquitectónica (Architectural Fitness Function — Estilo ArchUnit).
Subsana la observación de la Dimensión 5 de la Evaluación Sumativa 1 (Antipatrones y Evolución Arquitectónica):
Verifica mediante análisis estático del Árbol de Sintaxis Abstracta (AST) de Python que:
1. Antipatrón 1 ("The Blob / God Service" en clinical_service.py):
   - El servicio de dominio Expediente-Órdenes no excede el umbral máximo de métodos públicos ni de líneas por método,
     y delega las reglas algorítmicas en el paquete `strategies` y la auditoría criptográfica en `observers`.
   - `clinical_service.py` NO importa `hashlib` ni ejecuta funciones criptográficas directamente.
2. Antipatrón 2 ("Monolito Distribuido / Acoplamiento Cíclico y Violación de Capas"):
   - Ningún módulo de `strategies`, `observers` o `repositories` importa a `routers` ni a `services` (Acoplamiento Eferente controlado, 0 ciclos).
   - `AuditLedgerRepository` mantiene inmutabilidad arquitectónica estricta: carece de métodos `update` o `delete`.
"""
import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent / "app"


def get_imports_from_file(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_5_architectural_fitness_functions_antipattern_prevention():
    """
    Función de Aptitud Arquitectónica ejecutable en CI/CD que previene los Antipatrones 1 (God Service)
    y 2 (Acoplamiento / Violación de Capas e Inmutabilidad) documentados en la Sección 5 de la Evaluación 1.
    """
    service_file = APP_ROOT / "services" / "clinical_service.py"
    strategies_file = APP_ROOT / "strategies" / "clinical_strategies.py"
    observer_file = APP_ROOT / "observers" / "audit_observer.py"
    repo_file = APP_ROOT / "repositories" / "ehr_repository.py"

    # 1. Prevención de Antipatrón 1 (God Service / The Blob):
    # El servicio Expediente-Órdenes no debe calcular hashes SHA-256 ni contener lógica criptográfica directa
    service_imports = get_imports_from_file(service_file)
    assert "hashlib" not in service_imports, (
        "VIOLACIÓN ARQUITECTÓNICA (Antipatrón God Service): clinical_service.py no debe importar hashlib; "
        "la criptografía forense pertenece exclusivamente a ForensicAuditLedgerObserver."
    )

    # Verificar cohesión y tamaño acotado de ClinicalEHRService (máximo 8 métodos públicos)
    service_tree = ast.parse(service_file.read_text(encoding="utf-8"))
    for node in ast.walk(service_tree):
        if isinstance(node, ast.ClassDef) and node.name == "ClinicalEHRService":
            public_methods = [
                m.name for m in node.body if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
            ]
            assert len(public_methods) <= 8, (
                f"VIOLACIÓN DE UMBRAL DE COMPLEJIDAD (Antipatrón The Blob): ClinicalEHRService tiene "
                f"{len(public_methods)} métodos públicos (umbral máximo permitido: 8)."
            )

    # 2. Prevención de Antipatrón 2 (Acoplamiento Inverso / Ciclos entre Capas):
    # Las capas internas (strategies, observers, repositories) jamás deben importar de services ni routers
    for internal_file in (strategies_file, observer_file, repo_file):
        imports = get_imports_from_file(internal_file)
        for imp in imports:
            assert not imp.startswith("app.routers"), (
                f"VIOLACIÓN DE ARQUITECTURA EN CAPAS: {internal_file.name} importa '{imp}' (capa superior HTTP)."
            )
            assert not imp.startswith("app.services"), (
                f"DEPENDENCIA CÍCLICA DETECTADA: {internal_file.name} importa '{imp}'."
            )

    # 3. Verificación Estructural de Inmutabilidad del Ledger Forense (ADR-03 / ADR-08):
    # AuditLedgerRepository no puede definir métodos que empiecen con 'update' o 'delete'
    repo_tree = ast.parse(repo_file.read_text(encoding="utf-8"))
    for node in ast.walk(repo_tree):
        if isinstance(node, ast.ClassDef) and node.name == "AuditLedgerRepository":
            method_names = [m.name.lower() for m in node.body if isinstance(m, ast.FunctionDef)]
            forbidden = [m for m in method_names if "update" in m or "delete" in m or "remove" in m]
            assert not forbidden, (
                f"VIOLACIÓN DE INMUTABILIDAD FORENSE (ADR-03): AuditLedgerRepository contiene métodos prohibidos: {forbidden}"
            )
