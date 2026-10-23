# Plataforma de Historia Clínica Electrónica (HCE) Interoperable y Telemedicina de Urgencia — Caso 5

**Universidad Autónoma de Chile · Ingeniería Civil Informática**  
**Asignatura:** Arquitectura de Software · **Docente:** Cristofher Rojas Rojas  
**Integrantes:** Benjamín Naranjo — Hernán Escobar  

---

## 1. Descripción del Módulo Funcional Implementado (Evaluación Sumativa 2)

Este repositorio contiene la implementación funcional punta a punta (UI, lógica de negocio, patrones de diseño, control de acceso por roles y persistencia en base de datos) correspondiente a la **Evaluación Sumativa 2** del **Caso 5**.

El sistema materializa las decisiones arquitectónicas documentadas en los **ADR-01 a ADR-08**:
1. **Frontend React 18 + Vite bajo patrón MVVM (ADR-01 y ADR-02):**
   - **`Model` (`src/models/clinicalApi.js`):** Cliente HTTP/REST con contratos FHIR R4 y cola de salida transaccional local (*Transactional Outbox / Store-and-Forward* con claves de idempotencia UUID).
   - **`ViewModel` (`src/viewmodels/useClinicalViewModel.js`):** Concentra el estado observable, la máquina de estados del episodio clínico (`BORRADOR` -> `ENCOLADO_OUTBOX` -> `TRANSMITIENDO` -> `CONFIRMADO_EN_SERVIDOR`), la conmutación del tema de alto contraste exterior WCAG 2.2 AAA (7:1) y el drenaje automático de eventos al recuperar conectividad.
   - **`View` (`src/App.jsx`):** Reproduce fielmente los 3 Mockups de la Evaluación 1 (Panel de Urgencia de Ambulancia Móvil 07, Ficha Clínica FHIR R4 con Arbitraje de Conflictos, y Teleconsulta SFU con Subtitulado en Vivo) más la Consola de Auditoría Forense.
2. **Backend Python 3.13 + FastAPI + SQLAlchemy 2.0 + Pydantic v2 (ADR-03, ADR-05 y ADR-08):**
   - **Autenticación OAuth2 / JWT (HS256, TTL 15 min) y Control de Acceso Basado en Roles (RBAC):** 4 roles diferenciados (`PARAMEDICO`, `MEDICO_URGENCIA`, `MEDICO_TELECONSULTOR`, `AUDITOR_FORENSE`).
   - **Patrón Strategy (`app/strategies/clinical_strategies.py`):**
     - `EmergencySeverityIndexStrategy`: Clasifica automáticamente los signos vitales en niveles de triage ESI-1/ESI-2/ESI-3 y emite alertas fisiológicas críticas.
     - `AppendOnlyCRDTGSetStrategy` vs `OptimisticConcurrencyClinicalArbitrationStrategy`: Implementa la resolución dual de conflictos del **ADR-05** (vectores de versión y desvío a Cola de Arbitraje Clínico).
     - `DrugSafetyGuardStrategy`: Verifica invariantes transaccionales entre las alergias del expediente y las prescripciones médicas (**ADR-03**).
   - **Patrón Observer (`app/observers/audit_observer.py`):**
     - `ForensicAuditLedgerObserver`: Registra cada lectura y escritura en un **Ledger de Auditoría Forense Inmutable** encadenado criptográficamente mediante SHA-256 (`prev_hash` -> `current_hash`).
     - `CriticalTelemetryAlertObserver`: Despacha alertas críticas de código rojo sin acoplar el servicio clínico.
   - **Patrón Repository (`app/repositories/ehr_repository.py`):**
     - `PatientEHRRepository` y `AuditLedgerRepository`: Aíslan el acceso a datos relacional, verifican llaves de idempotencia UUID y ejecutan la auditoría matemática de la cadena de hashes.

---

## 2. Credenciales de Prueba por Rol (RBAC)

Todos los usuarios de demostración utilizan la contraseña institucional: **`urgencia2026`** (también seleccionables con un clic en la pantalla de Login):

| Usuario | Rol RBAC | Nombre y Unidad | Permisos en el Módulo Funcional |
| :--- | :--- | :--- | :--- |
| `paramedico.soto` | `PARAMEDICO` | Camila Soto Rivas (Ambulancia Móvil 07) | Lectura de HCE, captura de signos vitales/triage, operación de cola Offline Outbox y propuesta de alergias en terreno. **Bloqueado (HTTP 403)** para emitir prescripciones médicas o resolver arbitrajes. |
| `dr.valdivia` | `MEDICO_URGENCIA` | Dr. Martín Valdivia Rojas (Clínica Central) | Acceso clínico total: lectura/escritura de HCE, emisión de órdenes médicas con validación cruzada de alergias y resolución manual de la Cola de Arbitraje Clínico (ADR-05). |
| `dra.herrera` | `MEDICO_TELECONSULTOR` | Dra. Elena Herrera Guzmán (Sala SFU-04) | Conducción de Teleconsulta de Urgencia, emisión de directivas remotas con subtitulado en vivo y resolución de conflictos clínicos. |
| `auditor.hipaa` | `AUDITOR_FORENSE` | Ing. Roberto Domínguez (Oficial HIPAA) | Inspección y verificación matemática de la cadena criptográfica SHA-256 del Ledger de Auditoría. **Bloqueado (HTTP 403)** para registrar triage o prescribir fármacos. |

---

## 3. Instrucciones de Ejecución Local y Pruebas Automatizadas

### 3.1 Ejecutar las Pruebas Automatizadas (Pytest)
```powershell
cd "E:\Proyectos\arquitectura de software\backend"
python -m pytest -v
```

### 3.2 Iniciar el Servidor Backend (FastAPI en puerto 8000)
```powershell
cd "E:\Proyectos\arquitectura de software\backend"
python -m uvicorn app.main:app --reload --port 8000
```
- Documentación interactiva OpenAPI / Swagger UI disponible en: `http://127.0.0.1:8000/docs`

### 3.3 Iniciar la Aplicación Frontend (React + Vite en puerto 5173)
```powershell
cd "E:\Proyectos\arquitectura de software\frontend"
npm run dev
```
- Interfaz web disponible en: `http://localhost:5173`
