/**
 * CAPA VIEW (MVVM — ADR-01)
 * Reproduce fielmente los 3 Mockups de la Evaluación 1 (Sección 2.5, pág. 6):
 * 1. Panel de Urgencia (Ambulancia Móvil 07 — Signos Vitales, Alerta SpO2 Crítica, Cola Outbox Offline-First)
 * 2. Ficha Clínica Interoperable FHIR R4 (Alergias Medicamentosas, Concurrencia Optimista y Arbitraje Clínico ADR-05)
 * 3. Teleconsulta de Urgencia Cifrada (WebRTC SFU + Canal de Subtitulado en Vivo + Órdenes Médicas ADR-03)
 * + 4. Consola de Auditoría Forense Inmutable (Verificación de Cadena Criptográfica SHA-256 ADR-03 / ADR-08)
 */
import React, { useState } from 'react';
import { useClinicalViewModel } from './viewmodels/useClinicalViewModel';

export default function App() {
  const vm = useClinicalViewModel();

  // Estado local de formularios de entrada (efímero de UI según ADR-02)
  const [loginUser, setLoginUser] = useState('paramedico.soto');
  const [loginPass, setLoginPass] = useState('urgencia2026');
  const [deviceNode, setDeviceNode] = useState('Ambulancia Móvil 07 — Ruta Sur (Tablet Ruggerizada)');

  const [vitalsForm, setVitalsForm] = useState({
    heart_rate_bpm: 124,
    spo2_percent: 87,
    systolic_bp: 90,
    diastolic_bp: 56,
    temperature_c: 38.8,
    glasgow_score: 14,
    clinical_notes: 'Paciente con taquipnea durante cruce de túnel urbano. Se ajusta O2 a 6 L/min.',
  });

  const [mutableForm, setMutableForm] = useState({
    field_name: 'allergies',
    new_value: 'Penicilina (Anafilaxia); Sulfas; Látex (reportado por familiar en traslado)',
    simulate_stale_version: false,
  });

  const [orderForm, setOrderForm] = useState({
    order_type: 'FARMACO',
    medication_or_action: 'Aspirina (Ácido Acetilsalicílico) 250mg + Nitroglicerina 0.4mg',
    dosage_and_route: '250mg VO masticable + 0.4mg sublingual',
    clinical_justification: 'Protocolo Síndrome Coronario Agudo en traslado de urgencia',
  });

  const [resolutionMap, setResolutionMap] = useState({});

  const roleLabels = {
    PARAMEDICO: 'Paramédico / TENS Prehospitalario',
    MEDICO_URGENCIA: 'Médico Jefe de Urgencia (Clínica Destino)',
    MEDICO_TELECONSULTOR: 'Médico Especialista Teleconsultor (SFU)',
    AUDITOR_FORENSE: 'Oficial de Privacidad / Auditor Forense HIPAA',
  };

  // =========================================================================
  // PANTALLA DE AUTENTICACIÓN RBAC OAUTH2 / JWT (Requisito obligatorio 3.2)
  // =========================================================================
  if (!vm.session) {
    return (
      <div className={`app-shell ${vm.highContrastAAA ? 'theme-high-contrast-aaa' : ''}`}>
        <header className="top-bar">
          <div className="brand-block">
            <span className="brand-badge">HCE · CASO 5</span>
            <div>
              <div className="brand-title">
                Plataforma de Historia Clínica Electrónica Interoperable y Telemedicina de Urgencia
              </div>
              <div className="brand-subtitle">
                Arquitectura MVVM (React PWA) + Microservicios FastAPI FHIR R4 · SLA 99,999 % · HIPAA / HL7
              </div>
            </div>
          </div>
          <button
            type="button"
            className="btn-tactile"
            onClick={() => vm.setHighContrastAAA(!vm.highContrastAAA)}
          >
            {vm.highContrastAAA ? '☀ Modo Estándar Nocturno' : '👁 Alto Contraste Exterior AAA (7:1)'}
          </button>
        </header>

        <main className="workspace-container" style={{ maxWidth: '980px', marginTop: '1.5rem' }}>
          <div className="clinical-card">
            <div className="card-header">
              <div className="card-title">
                🔐 Control de Acceso Basado en Roles (RBAC) — Autenticación OAuth2 / JWT (ADR-02 y ADR-08)
              </div>
              <span className="badge badge-blue">TLS 1.3 + JWT 15m + Credencial Offline 72h</span>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.1rem' }}>
              Seleccione rápidamente uno de los <strong>4 perfiles institucionales del Caso 5</strong> para verificar
              los permisos diferenciados por rol, o ingrese las credenciales manualmente:
            </p>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
                gap: '0.75rem',
                marginBottom: '1.35rem',
              }}
            >
              {[
                {
                  user: 'paramedico.soto',
                  title: '🚑 Paramédico / TENS',
                  desc: 'Camila Soto · Registra Triage, Signos Vitales y Opera Cola Offline Outbox',
                  node: 'Ambulancia Móvil 07 — Ruta Sur (Tablet Ruggerizada)',
                },
                {
                  user: 'dr.valdivia',
                  title: '🏥 Médico de Urgencia',
                  desc: 'Dr. Martín Valdivia · Ficha FHIR, Prescripción Segura y Arbitraje Clínico ADR-05',
                  node: 'Clínica Alta Complejidad Central — Box Reanimación 01',
                },
                {
                  user: 'dra.herrera',
                  title: '📡 Médico Teleconsultor',
                  desc: 'Dra. Elena Herrera · Sala WebRTC SFU, Subtitulado en Vivo y Directivas Remotas',
                  node: 'Estación Teleconsulta SFU-04 — Red Nacional',
                },
                {
                  user: 'auditor.hipaa',
                  title: '🛡 Auditor Forense HIPAA',
                  desc: 'Ing. Roberto Domínguez · Verificación Criptográfica SHA-256 Append-Only',
                  node: 'Consola Aislada de Auditoría Forense (Segmento Sin Salida)',
                },
              ].map((preset) => (
                <button
                  key={preset.user}
                  type="button"
                  className="btn-tactile"
                  style={{
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    textAlign: 'left',
                    padding: '0.85rem',
                    borderColor: loginUser === preset.user ? 'var(--accent-blue)' : 'var(--border-subtle)',
                  }}
                  onClick={() => {
                    setLoginUser(preset.user);
                    setLoginPass('urgencia2026');
                    setDeviceNode(preset.node);
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: '0.92rem' }}>{preset.title}</div>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    {preset.desc}
                  </div>
                </button>
              ))}
            </div>

            {vm.authError && (
              <div className="notification-banner error" style={{ marginBottom: '1rem' }}>
                <div>
                  <strong>Error de Autenticación:</strong> {vm.authError}
                </div>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                vm.loginWithCredentials(loginUser, loginPass, deviceNode);
              }}
            >
              <div className="grid-2col">
                <div className="form-group">
                  <label className="form-label">Usuario Institucional (Practitioner ID)</label>
                  <input
                    className="form-input"
                    value={loginUser}
                    onChange={(e) => setLoginUser(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Contraseña (Demo: urgencia2026)</label>
                  <input
                    type="password"
                    className="form-input"
                    value={loginPass}
                    onChange={(e) => setLoginPass(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Terminal / Nodo de Borde Registrado (Epic-style Device Binding)</label>
                <input
                  className="form-input"
                  value={deviceNode}
                  onChange={(e) => setDeviceNode(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'flex', gap: '0.8rem', marginTop: '0.5rem' }}>
                <button type="submit" className="btn-tactile btn-primary" disabled={vm.loading}>
                  {vm.loading ? 'Verificando firma JWT...' : 'Iniciar Sesión Segura en Plataforma HCE'}
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    );
  }

  const user = vm.session.user;
  const patient = vm.currentPatient;
  const vitals = vm.latestVitals;

  return (
    <div className={`app-shell ${vm.highContrastAAA ? 'theme-high-contrast-aaa' : ''}`}>
      {/* CABECERA OPERATIVA */}
      <header className="top-bar">
        <div className="brand-block">
          <span className="brand-badge">UNIDAD MÓVIL 07 · EN RUTA</span>
          <div>
            <div className="brand-title">
              HCE Interoperable FHIR R4 & Telemedicina de Urgencia
            </div>
            <div className="brand-subtitle">
               Profesional: {user.full_name} · Rol: [{user.role}] · Máquina Estado Episodio: [{vm.episodeState}]
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
          {/* Selector de Paciente */}
          <select
            className="form-select"
            style={{ minHeight: '48px', width: 'auto' }}
            value={vm.selectedPatientId}
            onChange={(e) => vm.setSelectedPatientId(Number(e.target.value))}
          >
            {vm.patients.map((p) => (
              <option key={p.id} value={p.id}>
                Paciente: {p.full_name} ({p.rut}) — v{p.version}
              </option>
            ))}
          </select>

          {/* Conmutador Offline-First (ADR-02 y ADR-04) */}
          <button
            type="button"
            className={`btn-tactile ${vm.isOfflineTunnel ? 'btn-warning' : 'btn-success'}`}
            onClick={vm.toggleOfflineTunnel}
          >
            {vm.isOfflineTunnel
              ? `📡 OFFLINE (Túnel) · Cola Outbox: ${vm.outboxQueue.length}`
              : '📶 ONLINE (Red 5G/mTLS Activa)'}
          </button>

          {/* Conmutador de Alto Contraste WCAG 2.2 AAA (Sección 2.2 #1) */}
          <button
            type="button"
            className="btn-tactile"
            onClick={() => vm.setHighContrastAAA(!vm.highContrastAAA)}
          >
            {vm.highContrastAAA ? '☀ Contraste Normal' : '👁 Contraste AAA (7:1)'}
          </button>

          <button type="button" className="btn-tactile btn-danger" onClick={vm.logout}>
            Cerrar Sesión
          </button>
        </div>
      </header>

      {/* PESTAÑAS DE NAVEGACIÓN (3 Mockups Evaluación 1 + Ledger Forense) */}
      <nav className="nav-tabs">
        <button
          type="button"
          className={`nav-tab ${vm.activeTab === 'URGENCIA' ? 'active' : ''}`}
          onClick={() => vm.setActiveTab('URGENCIA')}
        >
          🚨 1. Panel de Urgencia (Telemetría & Triage)
        </button>
        <button
          type="button"
          className={`nav-tab ${vm.activeTab === 'FICHA_FHIR' ? 'active' : ''}`}
          onClick={() => vm.setActiveTab('FICHA_FHIR')}
        >
          📋 2. Ficha Clínica FHIR R4 & Arbitraje ADR-05
          {vm.pendingConflicts.length > 0 && (
            <span className="badge badge-red">{vm.pendingConflicts.length} Conflicto</span>
          )}
        </button>
        <button
          type="button"
          className={`nav-tab ${vm.activeTab === 'TELECONSULTA' ? 'active' : ''}`}
          onClick={() => vm.setActiveTab('TELECONSULTA')}
        >
          📹 3. Teleconsulta SFU & Órdenes Médicas
        </button>
        <button
          type="button"
          className={`nav-tab ${vm.activeTab === 'AUDITORIA' ? 'active' : ''}`}
          onClick={() => vm.setActiveTab('AUDITORIA')}
        >
          🔗 4. Ledger Forense SHA-256 (Inmutable)
        </button>
      </nav>

      {/* CONTENIDO PRINCIPAL */}
      <main className="workspace-container">
        {/* Banner de retroalimentación de operaciones, validaciones y errores */}
        {vm.notification && (
          <div className={`notification-banner ${vm.notification.type}`}>
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>
                [{vm.notification.timestamp}] {vm.notification.title}
              </div>
              <div style={{ fontSize: '0.88rem', marginTop: '0.2rem' }}>{vm.notification.detail}</div>
            </div>
            <button
              type="button"
              className="btn-tactile"
              style={{ minHeight: '36px', padding: '0.25rem 0.65rem' }}
              onClick={() => vm.setNotification(null)}
            >
              ✕
            </button>
          </div>
        )}

        {/* =====================================================================
            VISTA 1: PANEL DE URGENCIA (Mockup 1 Evaluación 1 + Patrón Strategy + Outbox)
           ===================================================================== */}
        {vm.activeTab === 'URGENCIA' && patient && (
          <div className="grid-2col">
            {/* Columna Izquierda: Monitor Multiparámetro en Tiempo Real (Mockup 1) */}
            <div className="clinical-card">
              <div className="card-header">
                <div>
                  <div className="brand-subtitle">UNIDAD MÓVIL 07 · EN RUTA</div>
                  <div className="card-title" style={{ fontSize: '1.25rem' }}>
                    Panel de Urgencia — {patient.full_name} ({patient.age} años)
                  </div>
                </div>
                <span className={`badge ${vitals?.is_critical ? 'badge-red' : 'badge-green'}`}>
                  {vitals?.triage_category || 'En evaluación'}
                </span>
              </div>

              <div className="grid-vitals">
                <div className="vital-tile">
                  <span className="vital-label">💚 FRECUENCIA CARDÍACA</span>
                  <div>
                    <span className="vital-value green">{vitals ? vitals.heart_rate_bpm : '--'}</span>
                    <span className="vital-unit">lpm</span>
                  </div>
                  <span className="brand-subtitle"> Derivación II · Ritmo sinusal taquicárdico</span>
                </div>

                <div className={`vital-tile ${vitals && vitals.spo2_percent < 90 ? 'critical' : ''}`}>
                  <span className="vital-label">🫁 SATURACIÓN O₂ (SpO₂)</span>
                  <div>
                    <span className={`vital-value ${vitals && vitals.spo2_percent < 90 ? 'red' : 'green'}`}>
                      {vitals ? `${vitals.spo2_percent}%` : '--'}
                    </span>
                  </div>
                  <span className="badge badge-red">
                    {vitals && vitals.spo2_percent < 90
                      ? '⚠ DOBLE CODIFICACIÓN: HIPOXEMIA CRÍTICA (<90%)'
                      : 'Rango aceptable'}
                  </span>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">🩸 PRESIÓN ARTERIAL NO INVASIVA</span>
                  <div>
                    <span className="vital-value green">
                      {vitals ? `${vitals.systolic_bp}/${vitals.diastolic_bp}` : '--/--'}
                    </span>
                    <span className="vital-unit">mmHg</span>
                  </div>
                  <span className="brand-subtitle">PAM calculada en monitoreo continuo</span>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">🌡 TEMPERATURA CORPORAL</span>
                  <div>
                    <span className="vital-value amber">{vitals ? vitals.temperature_c : '--'}</span>
                    <span className="vital-unit">°C</span>
                  </div>
                  <span className="brand-subtitle">Escala Glasgow: {vitals ? vitals.glasgow_score : 15}/15</span>
                </div>
              </div>

              {/* Bloque de Alerta Crítica lateral del Mockup 1 */}
              {vitals && (
                <div
                  className={`clinical-card ${vitals.is_critical ? 'critical-border' : ''}`}
                  style={{ marginTop: '1rem' }}
                >
                  <div style={{ fontWeight: 800, color: '#fca5a5', fontSize: '0.95rem' }}>
                    ⚡ Evaluación Automática Patrón Strategy (EmergencySeverityIndexStrategy):
                  </div>
                  <div style={{ fontSize: '0.9rem', marginTop: '0.35rem' }}>{vitals.clinical_alerts}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.4rem' }}>
                    Registrado por: {vitals.recorded_by} · Nodo: {vitals.origin_node} · UUID Idempotencia:{' '}
                    <code>{vitals.idempotency_key}</code>
                  </div>
                </div>
              )}

              {/* Estado de la Cola Store-and-Forward (ADR-02 y ADR-04) */}
              <div
                style={{
                  marginTop: '1rem',
                  padding: '0.85rem 1rem',
                  borderRadius: '8px',
                  backgroundColor: 'var(--bg-panel)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <strong style={{ color: 'var(--accent-amber)' }}>
                    {vm.isOfflineTunnel ? 'MODO OFFLINE ACTIVO (ADR-02 / ADR-04)' : 'COLA OUTBOX SINCRONIZADA'}
                  </strong>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Eventos clínicos pendientes en IndexedDB/Outbox local: <strong>{vm.outboxQueue.length}</strong>
                  </div>
                </div>
                {vm.outboxQueue.length > 0 && !vm.isOfflineTunnel && (
                  <button type="button" className="btn-tactile btn-primary" onClick={vm.drainOutboxQueue}>
                    Sincronizar Ahora ({vm.outboxQueue.length})
                  </button>
                )}
              </div>
            </div>

            {/* Columna Derecha: Formulario de Captura de Triage y Signos Vitales */}
            <div className="clinical-card">
              <div className="card-header">
                <div className="card-title">
                  📝 Captura de Signos Vitales y Triage (Append-Only CRDT G-Set — ADR-05)
                </div>
                <span className="badge badge-blue">Idempotencia UUID</span>
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  vm.submitVitalSigns(vitalsForm);
                }}
              >
                <div className="grid-vitals">
                  <div className="form-group">
                    <label className="form-label">Frecuencia Cardíaca (20 - 260 lpm)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={vitalsForm.heart_rate_bpm}
                      onChange={(e) =>
                        setVitalsForm({ ...vitalsForm, heart_rate_bpm: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Saturación SpO₂ (40 - 100 %)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={vitalsForm.spo2_percent}
                      onChange={(e) =>
                        setVitalsForm({ ...vitalsForm, spo2_percent: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">PA Sistólica (40 - 300 mmHg)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={vitalsForm.systolic_bp}
                      onChange={(e) =>
                        setVitalsForm({ ...vitalsForm, systolic_bp: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">PA Diastólica (&lt; Sistólica mmHg)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={vitalsForm.diastolic_bp}
                      onChange={(e) =>
                        setVitalsForm({ ...vitalsForm, diastolic_bp: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Temperatura (28.0 - 44.0 °C)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-input"
                      value={vitalsForm.temperature_c}
                      onChange={(e) =>
                        setVitalsForm({ ...vitalsForm, temperature_c: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Escala de Coma de Glasgow (3 - 15)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={vitalsForm.glasgow_score}
                      onChange={(e) =>
                        setVitalsForm({ ...vitalsForm, glasgow_score: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Notas Clínicas de Traslado / Hallazgos Prehospitalarios</label>
                  <textarea
                    className="form-textarea"
                    value={vitalsForm.clinical_notes}
                    onChange={(e) =>
                      setVitalsForm({ ...vitalsForm, clinical_notes: e.target.value })
                    }
                  />
                </div>

                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  <button type="submit" className="btn-tactile btn-danger">
                    {vm.isOfflineTunnel
                      ? '💾 Guardar y Firmar en Cola Outbox Local (Offline)'
                      : '🚀 Registrar Triage y Notificar Hospital (FHIR Observation)'}
                  </button>

                  <button
                    type="button"
                    className="btn-tactile"
                    onClick={() =>
                      setVitalsForm({
                        ...vitalsForm,
                        systolic_bp: 85,
                        diastolic_bp: 110,
                      })
                    }
                  >
                    🧪 Probar Validación Fallida (PA Diastólica &gt; Sistólica)
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* =====================================================================
            VISTA 2: FICHA CLÍNICA FHIR R4 Y ARBITRAJE CLÍNICO (Mockup 2 + ADR-05)
           ===================================================================== */}
        {vm.activeTab === 'FICHA_FHIR' && patient && (
          <div className="grid-2col">
            {/* Ficha Clínica Completa (Fiel al Mockup 2 de la página 6) */}
            <div className="clinical-card">
              <div className="card-header">
                <div>
                  <span className="badge badge-red">⚠ ALERGIA SEVERA DOCUMENTADA: {patient.allergies}</span>
                  <h2 style={{ fontSize: '1.35rem', marginTop: '0.45rem' }}>{patient.full_name}</h2>
                  <div className="brand-subtitle">
                    RUT: {patient.rut} · {patient.age} años ({patient.birth_date}) · Sexo: {patient.sex} · Grupo:{' '}
                    {patient.blood_type}
                  </div>
                </div>
                <span className="badge badge-blue">Vector Versión ADR-05: v{patient.version}</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
                <div className="vital-tile">
                  <span className="vital-label">🩺 DIAGNÓSTICO ACTIVO EN URGENCIA (Campo Mutable Protegido)</span>
                  <div style={{ fontWeight: 700, fontSize: '1.02rem', marginTop: '0.25rem' }}>
                    {patient.active_diagnosis}
                  </div>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">🧬 PATOLOGÍAS CRÓNICAS DE BASE (FHIR Condition)</span>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.4rem' }}>
                    {patient.chronic_conditions.split(';').map((c, idx) => (
                      <span key={idx} className="badge badge-blue">
                        {c.trim()}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">💊 MEDICACIÓN HABITUAL VIGENTE (FHIR MedicationStatement)</span>
                  <div style={{ fontSize: '0.92rem', marginTop: '0.35rem' }}>{patient.current_medications}</div>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">📋 PLAN DE TRATAMIENTO ACTIVO (Campo Mutable Protegido)</span>
                  <div style={{ fontSize: '0.92rem', marginTop: '0.35rem' }}>{patient.treatment_plan}</div>
                </div>
              </div>
            </div>

            {/* Columna Derecha: Control de Concurrencia Optimista y Cola de Arbitraje Clínico (ADR-05) */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div className="clinical-card">
                <div className="card-header">
                  <div className="card-title">
                    🔄 Actualizar Campo Mutable con Vector de Versión (ADR-05)
                  </div>
                  <span className="badge badge-amber">Concurrencia Optimista</span>
                </div>

                <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '0.9rem' }}>
                  Según el <strong>ADR-05</strong>, los campos mutables (alergias, diagnóstico activo, plan de
                  tratamiento) no admiten fusión automática tipo <em>Last-Write-Wins</em>. Si un nodo desconectado
                  envía una versión anterior a la versión actual del servidor (<strong>v{patient.version}</strong>), la
                  escritura se congela y se envía a la <strong>Cola de Arbitraje Clínico</strong>.
                </p>

                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const expectedVer = mutableForm.simulate_stale_version
                      ? Math.max(1, patient.version - 1)
                      : patient.version;
                    vm.updateMutableField(mutableForm.field_name, mutableForm.new_value, expectedVer);
                  }}
                >
                  <div className="form-group">
                    <label className="form-label">Campo Clínico Mutable a Modificar</label>
                    <select
                      className="form-select"
                      value={mutableForm.field_name}
                      onChange={(e) => setMutableForm({ ...mutableForm, field_name: e.target.value })}
                    >
                      <option value="allergies">Lista de Alergias Medicamentosas (allergies)</option>
                      <option value="active_diagnosis">Diagnóstico Activo (active_diagnosis)</option>
                      <option value="treatment_plan">Plan de Tratamiento (treatment_plan)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Nuevo Valor Clínico Propuesto</label>
                    <textarea
                      className="form-textarea"
                      value={mutableForm.new_value}
                      onChange={(e) => setMutableForm({ ...mutableForm, new_value: e.target.value })}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={mutableForm.simulate_stale_version}
                        onChange={(e) =>
                          setMutableForm({ ...mutableForm, simulate_stale_version: e.target.checked })
                        }
                        style={{ width: '20px', height: '20px' }}
                      />
                      <span style={{ fontSize: '0.86rem', color: 'var(--accent-amber)', fontWeight: 600 }}>
                        Simular colisión de concurrencia offline (enviar versión desactualizada v
                        {Math.max(1, patient.version - 1)} frente a servidor v{patient.version})
                      </span>
                    </label>
                  </div>

                  <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
                    <button type="submit" className="btn-tactile btn-primary">
                      Enviar Actualización Mutable (v
                      {mutableForm.simulate_stale_version
                        ? Math.max(1, patient.version - 1)
                        : patient.version}
                      )
                    </button>
                    <button
                      type="button"
                      className="btn-tactile btn-warning"
                      onClick={async () => {
                        // Paso 1: Incrementar versión en servidor como clínica destino y Paso 2: enviar versión vieja=1
                        await vm.updateMutableField(
                          'allergies',
                          'Penicilina (Anafilaxia); Sulfas; Contraste Yodado (actualizado en Clínica)',
                          patient.version
                        );
                        await vm.updateMutableField(
                          'allergies',
                          'Penicilina (Anafilaxia); Sulfas; Látex (agregado sin red en Ambulancia 07)',
                          1
                        );
                      }}
                    >
                      ⚡ Demostrar Conflicto Ambulancia vs Clínica (1-Click ADR-05)
                    </button>
                  </div>
                </form>
              </div>

              {/* Cola de Arbitraje Clínico */}
              <div className={`clinical-card ${vm.pendingConflicts.length > 0 ? 'critical-border' : ''}`}>
                <div className="card-header">
                  <div className="card-title">
                    ⚖ Cola de Arbitraje Clínico Manual (ADR-05)
                  </div>
                  <span className={`badge ${vm.pendingConflicts.length > 0 ? 'badge-red' : 'badge-green'}`}>
                    {vm.pendingConflicts.length} Pendientes
                  </span>
                </div>

                {vm.pendingConflicts.length === 0 ? (
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)' }}>
                    No existen conflictos de vectores de versión pendientes de conciliación para este paciente.
                  </p>
                ) : (
                  vm.pendingConflicts.map((conf) => {
                    const currentRes = resolutionMap[conf.id] || {
                      chosen: `${conf.server_value}; ${conf.client_proposed_value}`,
                      notes: 'Se fusionan clínicamente ambos hallazgos de alergia (Hospital + Ambulancia) para preservar seguridad del paciente.',
                    };
                    return (
                      <div key={conf.id} className="vital-tile critical" style={{ marginBottom: '0.85rem' }}>
                        <div style={{ fontWeight: 700, fontSize: '0.92rem' }}>
                          Conflicto #{conf.id} en campo <code>{conf.field_name}</code> (Cliente envió v
                          {conf.client_expected_version} vs Servidor v{conf.server_current_version})
                        </div>
                        <div style={{ fontSize: '0.82rem', marginTop: '0.4rem' }}>
                          <div>
                            • <strong>Versión en Servidor:</strong> {conf.server_value}
                          </div>
                          <div>
                            • <strong>Versión Propuesta por {conf.submitted_by}:</strong>{' '}
                            {conf.client_proposed_value}
                          </div>
                        </div>

                        <div className="form-group" style={{ marginTop: '0.65rem' }}>
                          <label className="form-label">Valor Clínico Conciliado Definitivo</label>
                          <input
                            className="form-input"
                            value={currentRes.chosen}
                            onChange={(e) =>
                              setResolutionMap({
                                ...resolutionMap,
                                [conf.id]: { ...currentRes, chosen: e.target.value },
                              })
                            }
                          />
                        </div>
                        <div className="form-group">
                          <label className="form-label">Justificación Médica para Auditoría Forense</label>
                          <input
                            className="form-input"
                            value={currentRes.notes}
                            onChange={(e) =>
                              setResolutionMap({
                                ...resolutionMap,
                                [conf.id]: { ...currentRes, notes: e.target.value },
                              })
                            }
                          />
                        </div>
                        <button
                          type="button"
                          className="btn-tactile btn-success"
                          onClick={() =>
                            vm.resolveClinicalConflict(conf.id, currentRes.chosen, currentRes.notes)
                          }
                        >
                          ✔ Firmar Conciliación Médica (Solo Rol Médico)
                        </button>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        )}

        {/* =====================================================================
            VISTA 3: TELECONSULTA DE URGENCIA Y ÓRDENES MÉDICAS (Mockup 3 + ADR-03)
           ===================================================================== */}
        {vm.activeTab === 'TELECONSULTA' && patient && (
          <div className="grid-2col">
            {/* Consola de Videoconferencia WebRTC SFU + Subtitulado en Vivo (Mockup 3, pág. 6) */}
            <div className="clinical-card">
              <div className="card-header">
                <div>
                  <div className="brand-subtitle">UNIDAD MÓVIL 07 · TELECONSULTA CIFRADA SRTP/WebRTC</div>
                  <div className="card-title">Sala Activa: SFU-SALA-MOVIL-07-URG (ICE Restart 120s Activo)</div>
                </div>
                <span className="badge badge-green">● ENLACE ESTABLE · 38 ms</span>
              </div>

              {/* Visor Simulado del Especialista en Vivo (Fiel al Mockup 3) */}
              <div
                style={{
                  backgroundColor: '#070b12',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '2rem 1.5rem',
                  textAlign: 'center',
                  position: 'relative',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    top: '12px',
                    left: '12px',
                  }}
                >
                  <span className="badge badge-red">● REC CIFRADO AES-256 · 04:12</span>
                </div>

                <div style={{ fontSize: '3.2rem', marginBottom: '0.5rem' }}>👩‍⚕️📡</div>
                <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>
                  Dra. Elena Herrera Guzmán — Cardiología & Telemedicina de Urgencia
                </div>
                <div className="brand-subtitle" style={{ marginTop: '0.25rem' }}>
                  Flujo de Media: SRTP/UDP vía Clúster SFU Multi-AZ (ADR-07 / ADR-08)
                </div>

                {/* Subtitulado en Vivo Desacoplado (Solución Problema Crítico #2: Ruido de sirena y respirador) */}
                <div
                  style={{
                    marginTop: '1.5rem',
                    padding: '0.9rem 1.15rem',
                    backgroundColor: 'rgba(15, 23, 42, 0.92)',
                    border: '1px solid var(--accent-blue)',
                    borderRadius: '8px',
                    textAlign: 'left',
                  }}
                >
                  <div style={{ fontSize: '0.74rem', color: 'var(--accent-green)', fontWeight: 700 }}>
                    💬 SUBTITULADO CLÍNICO EN VIVO (Doble Codificación ante Ruido de Sirena — Sección 2.2 #2):
                  </div>
                  <div style={{ fontSize: '0.96rem', fontWeight: 600, marginTop: '0.25rem' }}>
                    {patient.orders.length > 0
                      ? `Especialista (${patient.orders[patient.orders.length - 1].author_name}): "${
                          patient.orders[patient.orders.length - 1].medication_or_action
                        } — ${patient.orders[patient.orders.length - 1].dosage_and_route}."`
                      : 'Especialista: "Administren oxígeno a 4 litros por minuto. Preparen el acceso venoso."'}
                  </div>
                </div>
              </div>

              {/* Historial de Órdenes y Directivas del Episodio */}
              <div style={{ marginTop: '1.15rem' }}>
                <div className="card-title" style={{ marginBottom: '0.6rem' }}>
                  📜 Órdenes Médicas y Directivas Registradas en el Episodio ({patient.orders.length})
                </div>
                {patient.orders.map((ord) => (
                  <div key={ord.id} className="vital-tile" style={{ marginBottom: '0.6rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span className="badge badge-blue">{ord.order_type}</span>
                      <span className="brand-subtitle">{ord.author_name} ({ord.author_role})</span>
                    </div>
                    <div style={{ fontWeight: 700, marginTop: '0.35rem' }}>
                      {ord.medication_or_action} — <span style={{ color: 'var(--accent-green)' }}>{ord.dosage_and_route}</span>
                    </div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                      Justificación: {ord.clinical_justification}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Columna Derecha: Emisión de Orden Médica con Verificación Transaccional de Alergias (ADR-03) */}
            <div className="clinical-card">
              <div className="card-header">
                <div className="card-title">
                  💉 Emitir Orden Médica / Prescripción Electrónica (Servicio Cohesivo Expediente-Órdenes ADR-03)
                </div>
                <span className="badge badge-amber">Invariante ACID</span>
              </div>

              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '0.9rem' }}>
                Según el <strong>ADR-03</strong>, el servicio mantiene unidos <em>Expediente Clínico</em> y{' '}
                <em>Órdenes</em> porque comparten invariantes de seguridad que no toleran consistencia eventual: toda
                prescripción verifica inmediatamente las alergias activas del paciente (<strong>{patient.allergies}</strong>)
                y bloquea contraindicaciones cruzadas.
              </p>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  vm.submitMedicalOrder(orderForm);
                }}
              >
                <div className="form-group">
                  <label className="form-label">Tipo de Orden FHIR</label>
                  <select
                    className="form-select"
                    value={orderForm.order_type}
                    onChange={(e) => setOrderForm({ ...orderForm, order_type: e.target.value })}
                  >
                    <option value="FARMACO">FARMACO (MedicationRequest)</option>
                    <option value="TELECONSULTA">TELECONSULTA (Directiva en Sala SFU)</option>
                    <option value="PROCEDIMIENTO">PROCEDIMIENTO (ServiceRequest)</option>
                    <option value="DERIVACION">DERIVACION (Traslado Interinstitucional)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Fármaco o Indicación Clínica</label>
                  <input
                    className="form-input"
                    value={orderForm.medication_or_action}
                    onChange={(e) => setOrderForm({ ...orderForm, medication_or_action: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Posología y Vía de Administración</label>
                  <input
                    className="form-input"
                    value={orderForm.dosage_and_route}
                    onChange={(e) => setOrderForm({ ...orderForm, dosage_and_route: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Justificación Clínica</label>
                  <textarea
                    className="form-textarea"
                    value={orderForm.clinical_justification}
                    onChange={(e) => setOrderForm({ ...orderForm, clinical_justification: e.target.value })}
                    required
                  />
                </div>

                <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
                  <button type="submit" className="btn-tactile btn-primary">
                    ✍ Firmar y Emitir Orden Médica
                  </button>

                  <button
                    type="button"
                    className="btn-tactile btn-danger"
                    onClick={() =>
                      vm.submitMedicalOrder({
                        order_type: 'FARMACO',
                        medication_or_action: 'Amoxicilina / Ácido Clavulánico 1g EV (Betalactámico)',
                        dosage_and_route: '1g endovenoso cada 8 horas',
                        clinical_justification: 'Prueba de bloqueo automático por alergia a Penicilina (ADR-03)',
                      })
                    }
                  >
                    🧪 Probar Bloqueo de Alergia a Penicilina (Amoxicilina EV)
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* =====================================================================
            VISTA 4: LEDGER DE AUDITORÍA FORENSE INMUTABLE (ADR-03 / ADR-08 / Observer)
           ===================================================================== */}
        {vm.activeTab === 'AUDITORIA' && (
          <div className="clinical-card">
            <div className="card-header">
              <div>
                <div className="card-title">
                  🔗 Ledger de Auditoría Forense Inmutable (Hash-Encadenado SHA-256 — ADR-03 y ADR-08)
                </div>
                <div className="brand-subtitle">
                  Generado desacopladamente mediante el Patrón Observer (ForensicAuditLedgerObserver)
                </div>
              </div>
              <button
                type="button"
                className="btn-tactile btn-primary"
                onClick={() => vm.refreshClinicalData()}
              >
                🔍 Re-verificar Integridad Criptográfica SHA-256
              </button>
            </div>

            {!vm.auditReport ? (
              <div className="notification-banner warning">
                <div>
                  <strong>Acceso Restringido por RBAC:</strong> El rol actual ({user.role}) no posee privilegios de
                  inspección criptográfica completa del Ledger Forense. Inicie sesión como{' '}
                  <code>auditor.hipaa</code>, <code>dr.valdivia</code> o <code>dra.herrera</code> para auditar la cadena.
                </div>
              </div>
            ) : (
              <>
                <div
                  className={`notification-banner ${vm.auditReport.is_valid ? 'success' : 'critical'}`}
                  style={{ marginBottom: '1rem' }}
                >
                  <div>
                    <div style={{ fontWeight: 800 }}>
                      {vm.auditReport.is_valid
                        ? '✔ CADENA CRIPTOGRÁFICA ÍNTEGRA (HIPAA Security Rule Compliant)'
                        : '❌ ALERTA FORENSE: ADULTERACIÓN DETECTADA EN CADENA'}
                    </div>
                    <div style={{ fontSize: '0.86rem', marginTop: '0.2rem' }}>
                      {vm.auditReport.status_message} · Último Hash Raíz:{' '}
                      <code className="hash-code">{vm.auditReport.latest_hash}</code>
                    </div>
                  </div>
                </div>

                <div style={{ overflowX: 'auto' }}>
                  <table className="ledger-table">
                    <thead>
                      <tr>
                        <th># Seq</th>
                        <th>Timestamp UTC</th>
                        <th>Actor (Rol RBAC)</th>
                        <th>Evento Clínico / Seguridad</th>
                        <th>Recurso FHIR</th>
                        <th>Detalle Auditado</th>
                        <th>Prev Hash → Current Hash (SHA-256)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {vm.auditReport.entries.map((entry) => (
                        <tr key={entry.id}>
                          <td style={{ fontWeight: 700 }}>#{entry.sequence_number}</td>
                          <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                            {entry.timestamp_iso.replace('T', ' ').slice(0, 19)}
                          </td>
                          <td>
                            <strong>{entry.actor_username}</strong>
                            <div className="brand-subtitle">{entry.actor_role}</div>
                          </td>
                          <td>
                            <span
                              className={`badge ${
                                entry.action_type.includes('BLOCKED') ||
                                entry.action_type.includes('CONFLICT') ||
                                entry.action_type.includes('FAILED')
                                  ? 'badge-red'
                                  : 'badge-blue'
                              }`}
                            >
                              {entry.action_type}
                            </span>
                          </td>
                          <td>{entry.resource_id}</td>
                          <td style={{ maxWidth: '340px' }}>{entry.details}</td>
                          <td>
                            <div className="hash-code" title={entry.prev_hash}>
                              Prev: {entry.prev_hash.slice(0, 14)}...
                            </div>
                            <div
                              className="hash-code"
                              style={{ marginTop: '0.2rem', color: '#6ee7b7' }}
                              title={entry.current_hash}
                            >
                              Curr: {entry.current_hash.slice(0, 14)}...
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
