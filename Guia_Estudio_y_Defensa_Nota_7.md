# Guía Maestra de Estudio y Defensa Técnica (Objetivo: Nota 7.0)
## Caso 5 — Plataforma de Historia Clínica Electrónica (HCE) Interoperable y Telemedicina de Urgencia
**Integrantes:** Benjamín Naranjo — Hernán Escobar · **Docente:** Cristofher Rojas Rojas

---

## 1. Evaluación Crítica de tu Proyecto: ¿Qué ajustamos hoy para blindar el 7.0?

Me comentaste algo clave: **el profesor te dijo hoy que veía el proyecto "muy saturado de información" y te preguntó por la adaptación a celulares, tablets y computadores.**

> [!IMPORTANT]
> **¿Por qué te dijo eso el profesor y cómo lo acabamos de convertir en tu mejor punto a favor?**
> En la **Evaluación 1 (Página 4, Sección 2.2, Problema Crítico #4)** ustedes mismos escribieron esta regla arquitectónica:
> *"Jerarquía visual que restringe la pantalla a un **máximo de siete elementos de decisión simultáneos, difiriendo el resto a divulgación progresiva**."*
>
> Cuando todos los formularios estaban abiertos al mismo tiempo junto con los monitores de signos vitales, un evaluador estricto podía decir: *"En su documento dijeron máximo 7 elementos simultáneos con divulgación progresiva, pero en pantalla me muestran 15 campos a la vez"*.

### Los 2 ajustes estratégicos que acabo de programar en tu aplicación (`App.jsx` y `useClinicalViewModel.js`):

1. **Modo Foco Urgencia ($\le 7$ elementos simultáneos + Divulgación Progresiva):**
   - Agregué en la barra superior el botón **`✔ Modo Foco Urgencia Activo (≤ 7 Elementos · Divulgación Progresiva)`** (activado por defecto).
   - En este modo, la pantalla muestra **únicamente los signos vitales críticos y la alerta clínica**, ocultando los formularios largos detrás de un botón limpio (`➕ Abrir Formulario de Nuevo Triage`). Si el profesor quiere ver todos los controles abiertos de golpe, haces un clic y se expande todo.
2. **Simulador Integrado de Dispositivos (`🖥 Automático`, `📟 Tablet Ambulancia 820px`, `📱 Celular Médico 390px`):**
   - Sin siquiera abrir el inspector `F12`, ahora tienes en la barra superior **3 botones de dispositivo**.
   - Con un solo clic frente al profesor, el contenedor se transforma en vivo en una **Tablet de Ambulancia (`820px`)** o en un **Celular Médico (`390px`)** con botones táctiles de `52px` a ancho completo.

---

## 2. Cómo Justificar Cada Elección Arquitectónica y Tecnológica (Por Capa)

Estudia esta tabla. La clave con un profesor estricto es **nunca decir "elegimos X porque es popular o fácil"**, sino **"elegimos X por la restricción operativa Y del Caso 5, descartando Z por esta razón técnica"**:

| ComponenteElegido | ¿Por qué elegimos esta tecnología / patrón? (Argumento de Defensa) | ¿Por qué descartamos la alternativa? (Trade-off) | Dónde está en nuestro código |
| :--- | :--- | :--- | :--- |
| **Patrón MVVM en Frontend** (`ADR-01`) | Porque en una ambulancia la pantalla no cambia solo cuando el usuario hace clic; cambia por **eventos asíncronos externos** (llega telemetría del monitor, se corta el 5G en un túnel, salta una alerta de hipoxemia). El `ViewModel` concentra esa máquina de estados y actualiza la `View` reactivamente. | Descartamos **MVC** porque en MVC el controlador tendría que actualizar manualmente cada parte de la vista ante cada evento asíncrono, produciendo estados visuales inconsistentes en plena urgencia. | `useClinicalViewModel.js` (ViewModel), `App.jsx` (View), `clinicalApi.js` (Model) |
| **React 18 + Vite como PWA Responsiva** (`ADR-01`) | Permite tener **una sola base de código** que corre en las **3 clases de dispositivos del caso**: PC de hospital (`1440px`), Tablet ruggerizada de ambulancia (`820px`) y Celular del médico (`390px`), soportando almacenamiento local Offline-First y alto contraste WCAG 2.2 AAA ($7:1$). | Descartamos hacer **3 apps nativas separadas** (iOS, Android y Windows como hace *Epic Systems* con Haiku/Canto/Rover) porque el consorcio tiene un equipo de ingeniería reducido y mantener las mismas reglas clínicas en 3 lenguajes distintos duplicaría los errores. | `manifest.json`, `clinical.css` (`@media` + simulador de viewport) |
| **Cola Offline Store-and-Forward + UUID** (`ADR-02` / `ADR-04`) | Cuando la ambulancia entra a un túnel sin señal, el triage no se puede perder. Se guarda localmente en la cola **Transactional Outbox** firmado con un `idempotency_key` UUID v4. Al salir del túnel, se drena solo. | Descartamos **peticiones HTTP directas sin cola ni UUID** porque un corte de red perdería los datos en pantalla, y un reintento automático sin UUID **duplicaría** un signo vital o una administración de medicamento en la base de datos. | `enqueueOutboxTransaction()` en `clinicalApi.js` y validación UUID en `ehr_repository.py` |
| **Microservicios de Grano Grueso en Python / FastAPI** (`ADR-03`) | 1) **Aislamiento de fallos (SLA $99,999\%$):** Si el servidor de video WebRTC se satura, el registro de urgencias sigue vivo.<br>2) **Cohesión Expediente–Órdenes:** Mantuvimos juntos `Patient` y `MedicalOrder` porque validar alergias antes de recetar un fármaco exige una transacción ACID inmediata.<br>3) **FastAPI + Pydantic v2:** Ejecución asíncrona ASGI de baja latencia y validación automática de contratos **HL7 FHIR R4**. | Descartamos **Monolito** (porque un fallo en video o DICOM botaría todo el hospital) y descartamos **Microservicios de grano fino** (porque separar Alergias y Recetas en distintos servidores metería *consistencia eventual*, arriesgando recetar Penicilina a un alérgico). | `main.py`, `clinical_service.py`, `fhir_schemas.py` |
| **Estrategia Dual de Sincronización** (`ADR-05`) | No todos los datos clínicos tienen el mismo riesgo ante un conflicto offline:<br>- **Signos vitales (Append-Only):** Se unen automáticamente como un conjunto creciente (**CRDT G-Set**).<br>- **Alergias y Diagnóstico (Mutables):** Usan **Concurrencia Optimista con vector `version`**. Si hay choque entre ambulancia y clínica, se congela en la **Cola de Arbitraje Clínico**. | Descartamos **"Última Escritura Gana" (*Last-Write-Wins*)** en campos mutables porque si la clínica actualiza la ficha 1 segundo después que la ambulancia, borraría silenciosamente una alergia recién descubierta por el paramédico. | `clinical_strategies.py` (`AppendOnlyCRDTGSetStrategy` y `OptimisticConcurrency...`) |
| **SQLAlchemy 2.0 + SQLite WAL / PostgreSQL** (`ADR-05/06`) | Asegura consistencia fuerte (**CP** en el teorema CAP) para el núcleo transaccional (pacientes, órdenes, conflictos) y nos permite correr las 5 pruebas automatizadas en memoria en $1,4\text{ segundos}$. | Descartamos usar **solo una base NoSQL documental** (como MongoDB puro) para órdenes médicas porque carece de la rigidez relacional necesaria para las invariantes clínicas críticas. | `database.py`, `domain.py`, `ehr_repository.py` |
| **OAuth2 / JWT (15m) + RBAC + Ledger SHA-256** (`ADR-06/08`) | Cumple con **HIPAA Security Rule**: JWT sin estado con expiración corta de 15 min, 4 roles estrictos (`PARAMEDICO`, `MEDICO_URGENCIA`, `MEDICO_TELECONSULTOR`, `AUDITOR_FORENSE`) y una cadena de bloques hash **SHA-256** (`prev_hash` $\rightarrow$ `current_hash`) donde alterar un solo dato rompe toda la cadena. | Descartamos **una tabla de logs común y corriente** porque un administrador de base de datos malintencionado podría hacer un `UPDATE` o `DELETE` sobre un log médico sin que nadie pudiera demostrarlo matemáticamente. | `audit_observer.py` (`ForensicAuditLedgerObserver`) y `verify_chain_integrity()` |

---

## 3. Explicación Rápida de los 4 Patrones de Diseño (Para responder en 30 segundos)

Si el profesor te dice: *"Explíqueme los patrones de diseño que aplicaron y muéstremelos en el código"*:

1. **Patrón Strategy (`backend/app/strategies/clinical_strategies.py`):**
   - **¿Qué problema resuelve?** Evita llenar el servicio clínico de `if/else` gigantes para calcular el Triage o validar sincronizaciones.
   - **¿Cómo funciona?** Definimos la interfaz abstracta `ClinicalTriageStrategy` y la clase concreta `EmergencySeverityIndexStrategy` (que evalúa FC, $\text{SpO}_2$, PA, Temperatura y Glasgow y devuelve si es `ESI-1 Crítico`, `ESI-2` o `ESI-3`). También encapsula la estrategia de concurrencia optimista (`ADR-05`) y el bloqueo de alergias (`DrugSafetyGuardStrategy`).
2. **Patrón Observer (`backend/app/observers/audit_observer.py`):**
   - **¿Qué problema resuelve?** Evita el **Antipatrón *God Service***: el servicio médico no tiene por qué saber cómo se calcula un hash criptográfico SHA-256 de auditoría ni cómo se envían alertas de telemetría.
   - **¿Cómo funciona?** Cuando ocurre cualquier acción médica, `ClinicalEHRService` solo publica un evento en `clinical_event_bus`. Dos observadores suscritos reaccionan desacopladamente: `ForensicAuditLedgerObserver` (que calcula el SHA-256 encadenado al bloque anterior) y `CriticalTelemetryAlertObserver`.
3. **Patrón Repository (`backend/app/repositories/ehr_repository.py`):**
   - **¿Qué problema resuelve?** Separa la lógica de negocio de las consultas SQL/ORM.
   - **¿Cómo funciona?** `PatientEHRRepository` se encarga de buscar si un `idempotency_key` UUID ya llegó antes para no duplicarlo, y `AuditLedgerRepository` **no tiene métodos `update()` ni `delete()`**, haciendo que la inmutabilidad del registro forense sea una regla estructural del código.
4. **Patrón MVVM (`frontend/src/viewmodels/useClinicalViewModel.js`):**
   - **¿Qué problema resuelve?** Separa la vista gráfica (`App.jsx`) de la lógica de estado de la ambulancia, el modo offline y la accesibilidad.

---

## 4. Simulacro de Preguntas "Trampa" de un Profesor Estricto (y Cómo Responderlas)

### Pregunta 1: *"Hoy vi su sistema muy cargado de texto y cosas en pantalla. En urgencias un médico no tiene tiempo de leer tanto. ¿Cómo justifican eso?"*
* **Tu respuesta ganadora:**
  > *"Tiene toda la razón, profesor, y de hecho ese fue el **Problema Crítico #4** que documentamos en la Sección 2.2 de nuestra Evaluación 1 (fatiga visual en turnos de 12 horas). Aplicamos la regla de **Divulgación Progresiva basada en la Ley de Miller ($\le 7$ elementos simultáneos)**: como puede ver aquí arriba, activamos el **Modo Foco Urgencia**, donde la pantalla muestra únicamente los 4 signos vitales gigantes, la categoría ESI y la alerta roja, ocultando los formularios de edición hasta que el profesional presiona el botón de desplegar."*

### Pregunta 2: *"¿Por qué me dicen que es una arquitectura de microservicios si estoy viendo un solo servidor FastAPI corriendo en el puerto 8000?"*
* **Tu respuesta ganadora:**
  > *"Porque en el **ADR-03** definimos microservicios de **grano grueso alineados a subdominios DDD**, donde el núcleo transaccional **Expediente–Órdenes** es deliberadamente un único servicio cohesivo para garantizar invariantes ACID (que nunca se emita una receta sin validar las alergias en la misma transacción). La rúbrica de la Evaluación 2 pide implementar **un módulo representativo funcional** de la arquitectura, y nosotros implementamos precisamente ese microservicio núcleo junto con el Ledger Forense desacoplado por eventos."*

### Pregunta 3: *"¿Cómo sé que su aplicación realmente sirve para la tablet de la ambulancia, el celular del médico y el PC del hospital?"*
* **Tu respuesta ganadora:**
  > *"Porque además de usar CSS Grid responsivo con *breakpoints* en `1024px` (tablet) y `640px` (celular) y objetivos táctiles mínimos de `48px` a `52px` para uso con guantes de nitrilo, incluimos un **conmutador de dispositivo en vivo** en la barra superior. Mire: hago clic en **Tablet Ambulancia (820px)** o en **Celular Médico (390px)** y toda la interfaz se adapta a una sola columna vertical operable con el pulgar, además de contar con el botón de **Alto Contraste AAA (7:1)** para cuando da el sol directo en la cabina."*

### Pregunta 4: *"En la Evaluación 1 tuvieron un 3.0 en Antipatrones. ¿Qué hicieron distinto ahora?"*
* **Tu respuesta ganadora:**
  > *"En la Evaluación 1 solo habíamos descrito los antipatrones en texto. Ahora los llevamos al código con **Funciones de Aptitud Arquitectónica automatizadas** en `backend/tests/test_architectural_fitness.py`. Ese test analiza el árbol sintáctico (AST) de nuestro código Python cada vez que corremos `pytest` y falla automáticamente si `ClinicalEHRService` intenta hacer criptografía directa (evitando el antipatrón *God Service*), si alguna capa inferior importa a una capa superior (evitando acoplamiento cíclico) o si alguien intenta agregar un método `delete` al repositorio de auditoría."*
