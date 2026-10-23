/**
 * CAPA VIEW (MVVM — ADR-01)
 * Incluye dos modos conmutables en tiempo real:
 * 1. MODO PRODUCCIÓN CLÍNICA (Por defecto): Interfaz médica limpia, 100% enfocada en el usuario final
 *    (Paramédico, Médico de Urgencia, Teleconsultor, Oficial de Privacidad), sin jerga de ingeniería ni notas de ADRs.
 * 2. MODO RAYOS X ARQUITECTÓNICO (Docente / Defensa): Muestra las etiquetas de trazabilidad hacia los ADR-01..08,
 *    los patrones de diseño aplicados (MVVM, Strategy, Observer, Repository) y botones de simulación de fallos.
 */
import React, { useState } from 'react';
import { useClinicalViewModel } from './viewmodels/useClinicalViewModel';

export default function App() {
  const vm = useClinicalViewModel();
  const arch = vm.showArchitectureNotes;

  // Estado local de formularios de entrada
  const [loginUser, setLoginUser] = useState('paramedico.soto');
  const [loginPass, setLoginPass] = useState('urgencia2026');
  const [deviceNode, setDeviceNode] = useState('Ambulancia Móvil 07 — Ruta Sur');
  const [showTriageFormDrawer, setShowTriageFormDrawer] = useState(false);
  const [showMutableFormDrawer, setShowMutableFormDrawer] = useState(false);

  const [vitalsForm, setVitalsForm] = useState({
    heart_rate_bpm: 124,
    spo2_percent: 87,
    systolic_bp: 90,
    diastolic_bp: 56,
    temperature_c: 38.8,
    glasgow_score: 14,
    clinical_notes: 'Paciente con taquipnea durante traslado. Se ajusta O2 suplementario a 6 L/min.',
  });

  const [mutableForm, setMutableForm] = useState({
    field_name: 'allergies',
    new_value: 'Penicilina (Anafilaxia); Sulfas; Látex (reportado por familiar en traslado)',
    simulate_stale_version: false,
  });

  const [orderForm, setOrderForm] = useState({
    order_type: 'FARMACO',
    medication_or_action: 'Aspirina 250mg + Nitroglicerina 0.4mg',
    dosage_and_route: '250mg VO masticable + 0.4mg sublingual',
    clinical_justification: 'Protocolo Síndrome Coronario Agudo en traslado de urgencia',
  });

  const [resolutionMap, setResolutionMap] = useState({});

  // =========================================================================
  // PANTALLA DE INICIO DE SESIÓN (Limpia en Modo Clínica / Explicada en Modo Rayos X)
  // =========================================================================
  if (!vm.session) {
    return (
      <div className={`app-shell ${vm.highContrastAAA ? 'theme-high-contrast-aaa' : ''}`}>
        <header className="top-bar">
          <div className="brand-block">
            <span className="brand-badge">RED SALUD · URGENCIA</span>
            <div>
              <div className="brand-title">
                Plataforma de Historia Clínica Electrónica y Telemedicina de Urgencia
              </div>
              <div className="brand-subtitle">
                {arch
                  ? 'Arquitectura MVVM (React PWA) + Microservicios FastAPI FHIR R4 · SLA 99,999 % · HIPAA / HL7'
                  : 'Sistema Integrado de Atención Prehospitalaria, Recepción Hospitalaria y Teleconsulta'}
              </div>
            </div>
          </div>

          <div className="top-bar-actions">
            <button
              type="button"
              className={`btn-tactile ${arch ? 'btn-warning' : ''}`}
              onClick={() => vm.setShowArchitectureNotes(!arch)}
            >
              {arch ? '🔬 Modo Rayos X Arquitectónico (Activo)' : '🏥 Vista Clínica de Producción (Limpia)'}
            </button>
            <button
              type="button"
              className="btn-tactile"
              onClick={() => vm.setHighContrastAAA(!vm.highContrastAAA)}
            >
              {vm.highContrastAAA ? '☀ Modo Nocturno' : '👁 Alto Contraste Exterior'}
            </button>
          </div>
        </header>

        <main className="workspace-container" style={{ maxWidth: '880px', marginTop: '1.75rem' }}>
          <div className="clinical-card">
            <div className="card-header">
              <div className="card-title">
                {arch
                  ? '🔐 Control de Acceso Basado en Roles (RBAC) — Autenticación OAuth2 / JWT (ADR-02 y ADR-08)'
                  : '🔐 Acceso Institucional para Personal de Salud Autorizado'}
              </div>
              <span className="badge badge-blue">
                {arch ? 'TLS 1.3 + JWT 15m + Credencial Offline 72h' : 'Conexión Cifrada'}
              </span>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1rem' }}>
              {arch
                ? 'Seleccione uno de los 4 perfiles RBAC del Caso 5 para comprobar los permisos diferenciados por estamento:'
                : 'Seleccione su perfil operativo o ingrese sus credenciales institucionales:'}
            </p>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(195px, 1fr))',
                gap: '0.7rem',
                marginBottom: '1.25rem',
              }}
            >
              {[
                {
                  user: 'paramedico.soto',
                  title: '🚑 Paramédico / TENS',
                  desc: arch
                    ? 'Camila Soto · Triage ESI y Cola Offline Outbox (ADR-02)'
                    : 'Camila Soto · Unidad Móvil 07',
                  node: 'Ambulancia Móvil 07 — Ruta Sur',
                },
                {
                  user: 'dr.valdivia',
                  title: '🏥 Médico de Urgencia',
                  desc: arch
                    ? 'Dr. Martín Valdivia · Ficha FHIR, Recetas y Arbitraje ADR-05'
                    : 'Dr. Martín Valdivia · Box Reanimación 01',
                  node: 'Clínica Central — Box Reanimación 01',
                },
                {
                  user: 'dra.herrera',
                  title: '📡 Médico Teleconsultor',
                  desc: arch
                    ? 'Dra. Elena Herrera · Sala WebRTC SFU y Subtitulado en Vivo'
                    : 'Dra. Elena Herrera · Centro Telemedicina',
                  node: 'Estación Teleconsulta Sala 04',
                },
                {
                  user: 'auditor.hipaa',
                  title: '🛡 Oficial de Privacidad',
                  desc: arch
                    ? 'Ing. Roberto Domínguez · Verificación Cadena SHA-256 (Observer)'
                    : 'Ing. Roberto Domínguez · Auditoría Clínica',
                  node: 'Unidad de Cumplimiento y Auditoría',
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
                    padding: '0.8rem',
                    borderColor: loginUser === preset.user ? 'var(--accent-blue)' : 'var(--border-subtle)',
                  }}
                  onClick={() => {
                    setLoginUser(preset.user);
                    setLoginPass('urgencia2026');
                    setDeviceNode(preset.node);
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{preset.title}</div>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                    {preset.desc}
                  </div>
                </button>
              ))}
            </div>

            {vm.authError && (
              <div className="notification-banner error" style={{ marginBottom: '1rem' }}>
                <div>
                  <strong>Acceso rechazado:</strong> {vm.authError}
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
                  <label className="form-label">Credencial Profesional</label>
                  <input
                    className="form-input"
                    value={loginUser}
                    onChange={(e) => setLoginUser(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Contraseña Institucional</label>
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
                <label className="form-label">
                  {arch ? 'Terminal / Nodo de Borde Registrado (Device Binding)' : 'Unidad o Estación de Trabajo'}
                </label>
                <input
                  className="form-input"
                  value={deviceNode}
                  onChange={(e) => setDeviceNode(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'flex', gap: '0.8rem', marginTop: '0.5rem' }}>
                <button type="submit" className="btn-tactile btn-primary" disabled={vm.loading}>
                  {vm.loading ? 'Autenticando...' : 'Ingresar a la Plataforma'}
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
              {arch
                ? 'HCE Interoperable FHIR R4 & Telemedicina de Urgencia'
                : 'Consola Clínica de Urgencia y Telemedicina'}
            </div>
            <div className="brand-subtitle">
              {arch
                ? `Profesional: ${user.full_name} · Rol RBAC: [${user.role}] · Máquina Estado Episodio: [${vm.episodeState}]`
                : `${user.full_name} · ${user.facility}`}
            </div>
          </div>
        </div>

        <div className="top-bar-actions">
          {/* Selector de Paciente */}
          <select
            className="form-select patient-select"
            value={vm.selectedPatientId}
            onChange={(e) => vm.setSelectedPatientId(Number(e.target.value))}
          >
            {vm.patients.map((p) => (
              <option key={p.id} value={p.id}>
                Paciente: {p.full_name} ({p.rut}){arch ? ` — v${p.version}` : ''}
              </option>
            ))}
          </select>

          {/* Conmutador de Conectividad */}
          <button
            type="button"
            className={`btn-tactile ${vm.isOfflineTunnel ? 'btn-warning' : 'btn-success'}`}
            onClick={vm.toggleOfflineTunnel}
          >
            {vm.isOfflineTunnel
              ? `📡 Sin Cobertura (${vm.outboxQueue.length} en espera)`
              : '📶 En Línea'}
          </button>

          {/* Conmutador de Alto Contraste */}
          <button
            type="button"
            className="btn-tactile"
            onClick={() => vm.setHighContrastAAA(!vm.highContrastAAA)}
          >
            {vm.highContrastAAA ? '☀ Brillo Estándar' : '👁 Alto Contraste'}
          </button>

          {/* Conmutador Vista Clínica Limpia vs Modo Rayos X Arquitectónico */}
          <button
            type="button"
            className={`btn-tactile ${arch ? 'btn-warning' : ''}`}
            onClick={() => vm.setShowArchitectureNotes(!arch)}
            title="Alternar entre interfaz limpia de usuario final y vista con explicaciones de arquitectura para evaluación docente"
          >
            {arch ? '🔬 Rayos X Arquitectura: ON' : '🔬 Rayos X Arquitectura: OFF'}
          </button>

          <button type="button" className="btn-tactile btn-danger" onClick={vm.logout}>
            Salir
          </button>
        </div>
      </header>

      {/* BARRA DE HERRAMIENTAS DE DEMOSTRACIÓN ARQUITECTÓNICA (Solo visible si el usuario activa Rayos X Arquitectura) */}
      {arch && (
        <div className="ergonomics-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <span style={{ color: 'var(--accent-amber)', fontWeight: 700 }}>
              🔬 Modo Evaluación Docente Activo:
            </span>
            <button
              type="button"
              className={`device-pill ${vm.compactClinicalMode ? 'active' : ''}`}
              onClick={() => vm.setCompactClinicalMode(!vm.compactClinicalMode)}
            >
              {vm.compactClinicalMode
                ? '✔ Modo Foco Urgencia (≤ 7 Elementos · Divulgación Progresiva)'
                : '☰ Formularios Expandidos'}
            </button>
          </div>

          <div className="device-pill-group">
            <span style={{ color: 'var(--text-secondary)', fontWeight: 600, alignSelf: 'center', marginRight: '0.25rem' }}>
              📐 Simular Dispositivo (ADR-01):
            </span>
            {[
              { id: 'AUTO', label: '🖥 Escritorio (100%)' },
              { id: 'TABLET_820', label: '📟 Tablet Ambulancia (820px)' },
              { id: 'MOBILE_390', label: '📱 Celular Médico (390px)' },
            ].map((vp) => (
              <button
                key={vp.id}
                type="button"
                className={`device-pill ${vm.viewportMode === vp.id ? 'active' : ''}`}
                onClick={() => vm.setViewportMode(vp.id)}
              >
                {vp.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* PESTAÑAS DE NAVEGACIÓN */}
      <nav className="nav-tabs">
        <button
          type="button"
          className={`nav-tab ${vm.activeTab === 'URGENCIA' ? 'active' : ''}`}
          onClick={() => vm.setActiveTab('URGENCIA')}
        >
          🚨 Panel de Urgencia
        </button>
        <button
          type="button"
          className={`nav-tab ${vm.activeTab === 'FICHA_FHIR' ? 'active' : ''}`}
          onClick={() => vm.setActiveTab('FICHA_FHIR')}
        >
          📋 Ficha Clínica
          {vm.pendingConflicts.length > 0 && (
            <span className="badge badge-red">{vm.pendingConflicts.length} Alerta</span>
          )}
        </button>
        <button
          type="button"
          className={`nav-tab ${vm.activeTab === 'TELECONSULTA' ? 'active' : ''}`}
          onClick={() => vm.setActiveTab('TELECONSULTA')}
        >
          📹 Teleconsulta y Indicaciones
        </button>
        <button
          type="button"
          className={`nav-tab ${vm.activeTab === 'AUDITORIA' ? 'active' : ''}`}
          onClick={() => vm.setActiveTab('AUDITORIA')}
        >
          {arch ? '🔗 Ledger Forense SHA-256 (Observer)' : '🛡 Registro de Auditoría'}
        </button>
      </nav>

      {/* CONTENIDO PRINCIPAL */}
      <main className={`workspace-container viewport-frame-${vm.viewportMode}`}>
        {/* Banner de notificaciones */}
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
            VISTA 1: PANEL DE URGENCIA (Mockup 1 Evaluación 1)
           ===================================================================== */}
        {vm.activeTab === 'URGENCIA' && patient && (
          <div className="grid-2col">
            {/* Columna Izquierda: Monitor Multiparámetro en Tiempo Real */}
            <div className="clinical-card">
              <div className="card-header">
                <div>
                  <div className="brand-subtitle">UNIDAD MÓVIL 07 · MONITORIZACIÓN EN RUTA</div>
                  <div className="card-title" style={{ fontSize: '1.22rem' }}>
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
                  <span className="brand-subtitle">Derivación II · Ritmo sinusal</span>
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
                      ? '⚠ SpO₂ Crítica (< 90%) — Intervención requerida'
                      : 'Rango normal'}
                  </span>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">🩸 PRESIÓN ARTERIAL</span>
                  <div>
                    <span className="vital-value green">
                      {vitals ? `${vitals.systolic_bp}/${vitals.diastolic_bp}` : '--/--'}
                    </span>
                    <span className="vital-unit">mmHg</span>
                  </div>
                  <span className="brand-subtitle"> Monitoreo no invasivo continuo</span>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">🌡 TEMPERATURA</span>
                  <div>
                    <span className="vital-value amber">{vitals ? vitals.temperature_c : '--'}</span>
                    <span className="vital-unit">°C</span>
                  </div>
                  <span className="brand-subtitle">Escala Glasgow: {vitals ? vitals.glasgow_score : 15}/15</span>
                </div>
              </div>

              {/* Alerta Clínica */}
              {vitals && (
                <div
                  className={`clinical-card ${vitals.is_critical ? 'critical-border' : ''}`}
                  style={{ marginTop: '1rem' }}
                >
                  <div style={{ fontWeight: 800, color: '#fca5a5', fontSize: '0.93rem' }}>
                    {arch
                      ? '⚡ Evaluación Automática Patrón Strategy (EmergencySeverityIndexStrategy):'
                      : '⚡ Alerta Clínica de Triage:'}
                  </div>
                  <div style={{ fontSize: '0.9rem', marginTop: '0.3rem' }}>{vitals.clinical_alerts}</div>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
                    Registrado por: {vitals.recorded_by} · Unidad: {vitals.origin_node}
                    {arch && (
                      <>
                        {' '}· UUID Idempotencia: <code>{vitals.idempotency_key}</code>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* Estado de sincronización local si está desconectado o si Modo Rayos X está activo */}
              {(vm.isOfflineTunnel || vm.outboxQueue.length > 0 || arch) && (
                <div
                  style={{
                    marginTop: '0.9rem',
                    padding: '0.75rem 1rem',
                    borderRadius: '8px',
                    backgroundColor: 'var(--bg-panel)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <strong style={{ color: 'var(--accent-amber)', fontSize: '0.86rem' }}>
                      {vm.isOfflineTunnel
                        ? 'Modo Sin Cobertura Activo (Guardado Local)'
                        : 'Sincronización con Hospital al Día'}
                    </strong>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                      Registros pendientes de envío: <strong>{vm.outboxQueue.length}</strong>
                      {arch && ' (Cola Transactional Outbox ADR-02 / ADR-04)'}
                    </div>
                  </div>
                  {vm.outboxQueue.length > 0 && !vm.isOfflineTunnel && (
                    <button type="button" className="btn-tactile btn-primary" onClick={vm.drainOutboxQueue}>
                      Enviar Pendientes ({vm.outboxQueue.length})
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Columna Derecha: Registro de Signos Vitales */}
            <div className="clinical-card">
              <div className="card-header">
                <div className="card-title">
                  {arch
                    ? '📝 Captura de Signos Vitales y Triage (Append-Only CRDT G-Set — ADR-05)'
                    : '📝 Ingreso de Signos Vitales y Control de Triage'}
                </div>
                {arch && <span className="badge badge-blue">Idempotencia UUID</span>}
              </div>

              {vm.compactClinicalMode && !showTriageFormDrawer ? (
                <div style={{ textAlign: 'center', padding: '1.2rem 0.5rem' }}>
                  <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                    Vista enfocada en monitorización crítica. Presione el botón para registrar un nuevo control de signos vitales.
                  </p>
                  <button
                    type="button"
                    className="btn-tactile btn-danger"
                    onClick={() => setShowTriageFormDrawer(true)}
                  >
                    ➕ Nuevo Control de Signos Vitales
                  </button>
                </div>
              ) : (
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    vm.submitVitalSigns(vitalsForm);
                  }}
                >
                  {vm.compactClinicalMode && (
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.6rem' }}>
                      <button
                        type="button"
                        className="device-pill"
                        onClick={() => setShowTriageFormDrawer(false)}
                      >
                        ▲ Ocultar Formulario
                      </button>
                    </div>
                  )}
                  <div className="grid-vitals">
                    <div className="form-group">
                      <label className="form-label">Frecuencia Cardíaca (lpm)</label>
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
                      <label className="form-label">Saturación SpO₂ (%)</label>
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
                      <label className="form-label">PA Sistólica (mmHg)</label>
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
                      <label className="form-label">PA Diastólica (mmHg)</label>
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
                      <label className="form-label">Temperatura (°C)</label>
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
                      <label className="form-label">Escala de Glasgow (3 - 15)</label>
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
                    <label className="form-label">Observaciones Clínicas de Traslado</label>
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
                        ? '💾 Guardar Registro en Dispositivo (Sin Red)'
                        : '✔ Confirmar Signos Vitales y Notificar Hospital'}
                    </button>

                    {arch && (
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
                        🧪 Simular Error Fisiológico (PA Diastólica &gt; Sistólica)
                      </button>
                    )}
                  </div>
                </form>
              )}
            </div>
          </div>
        )}

        {/* =====================================================================
            VISTA 2: FICHA CLÍNICA Y CONCILIACIÓN DE ANTECEDENTES (Mockup 2)
           ===================================================================== */}
        {vm.activeTab === 'FICHA_FHIR' && patient && (
          <div className="grid-2col">
            {/* Ficha Clínica Completa */}
            <div className="clinical-card">
              <div className="card-header">
                <div>
                  <span className="badge badge-red">⚠ ALERGIA FARMACOLÓGICA: {patient.allergies}</span>
                  <h2 style={{ fontSize: '1.35rem', marginTop: '0.45rem' }}>{patient.full_name}</h2>
                  <div className="brand-subtitle">
                    RUT: {patient.rut} · {patient.age} años ({patient.birth_date}) · {patient.sex} · Grupo Sanguíneo:{' '}
                    {patient.blood_type}
                  </div>
                </div>
                <span className="badge badge-blue">
                  {arch ? `Vector Versión ADR-05: v${patient.version}` : `Ficha Rev. #${patient.version}`}
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div className="vital-tile">
                  <span className="vital-label">🩺 DIAGNÓSTICO PRINCIPAL EN URGENCIA</span>
                  <div style={{ fontWeight: 700, fontSize: '1rem', marginTop: '0.25rem' }}>
                    {patient.active_diagnosis}
                  </div>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">🧬 DIAGNÓSTICOS Y PATOLOGÍAS CRÓNICAS</span>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.4rem' }}>
                    {patient.chronic_conditions.split(';').map((c, idx) => (
                      <span key={idx} className="badge badge-blue">
                        {c.trim()}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">💊 MEDICACIÓN HABITUAL VIGENTE</span>
                  <div style={{ fontSize: '0.92rem', marginTop: '0.3rem' }}>{patient.current_medications}</div>
                </div>

                <div className="vital-tile">
                  <span className="vital-label">📋 PLAN TERAPÉUTICO ACTUAL</span>
                  <div style={{ fontSize: '0.92rem', marginTop: '0.3rem' }}>{patient.treatment_plan}</div>
                </div>
              </div>
            </div>

            {/* Columna Derecha: Actualización de Antecedentes y Conciliación */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
              <div className="clinical-card">
                <div className="card-header">
                  <div className="card-title">
                    {arch
                      ? '🔄 Actualizar Campo Mutable con Vector de Versión (ADR-05)'
                      : '✏️ Actualizar Antecedentes Clínicos del Paciente'}
                  </div>
                  {arch && <span className="badge badge-amber">Concurrencia Optimista</span>}
                </div>

                {arch && (
                  <p style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', marginBottom: '0.85rem' }}>
                    Según el <strong>ADR-05</strong>, los campos mutables no admiten sobrescritura automática{' '}
                    <em>Last-Write-Wins</em>. Si un nodo desconectado envía una revisión anterior a la vigente (
                    <strong>v{patient.version}</strong>), se desvía a la <strong>Cola de Arbitraje Clínico</strong>.
                  </p>
                )}

                {vm.compactClinicalMode && !showMutableFormDrawer ? (
                  <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
                    <button
                      type="button"
                      className="btn-tactile btn-primary"
                      onClick={() => setShowMutableFormDrawer(true)}
                    >
                      ➕ Modificar Alergias, Diagnóstico o Plan
                    </button>
                  </div>
                ) : (
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
                      <label className="form-label">Sección del Expediente</label>
                      <select
                        className="form-select"
                        value={mutableForm.field_name}
                        onChange={(e) => setMutableForm({ ...mutableForm, field_name: e.target.value })}
                      >
                        <option value="allergies">Alergias Medicamentosas</option>
                        <option value="active_diagnosis">Diagnóstico Activo</option>
                        <option value="treatment_plan">Plan de Tratamiento</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Información Clínica Actualizada</label>
                      <textarea
                        className="form-textarea"
                        value={mutableForm.new_value}
                        onChange={(e) => setMutableForm({ ...mutableForm, new_value: e.target.value })}
                        required
                      />
                    </div>

                    {arch && (
                      <div className="form-group">
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer' }}>
                          <input
                            type="checkbox"
                            checked={mutableForm.simulate_stale_version}
                            onChange={(e) =>
                              setMutableForm({ ...mutableForm, simulate_stale_version: e.target.checked })
                            }
                            style={{ width: '18px', height: '18px' }}
                          />
                          <span style={{ fontSize: '0.84rem', color: 'var(--accent-amber)', fontWeight: 600 }}>
                            Simular envío desde ambulancia con revisión anterior (v
                            {Math.max(1, patient.version - 1)} vs v{patient.version})
                          </span>
                        </label>
                      </div>
                    )}

                    <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
                      <button type="submit" className="btn-tactile btn-primary">
                        Guardar Cambios en Ficha
                      </button>

                      <button
                        type="button"
                        className="btn-tactile btn-warning"
                        onClick={async () => {
                          await vm.updateMutableField(
                            'allergies',
                            'Penicilina (Anafilaxia); Sulfas; Contraste Yodado (registrado en Hospital)',
                            patient.version
                          );
                          await vm.updateMutableField(
                            'allergies',
                            'Penicilina (Anafilaxia); Sulfas; Látex (reportado en Ambulancia 07)',
                            1
                          );
                        }}
                      >
                        {arch
                          ? '⚡ Demostrar Conflicto Ambulancia vs Clínica (ADR-05)'
                          : '⚡ Simular Edición Simultánea (Ambulancia / Hospital)'}
                      </button>
                    </div>
                  </form>
                )}
              </div>

              {/* Conciliación Médica de Antecedentes */}
              <div className={`clinical-card ${vm.pendingConflicts.length > 0 ? 'critical-border' : ''}`}>
                <div className="card-header">
                  <div className="card-title">
                    {arch
                      ? '⚖ Cola de Arbitraje Clínico Manual (ADR-05)'
                      : '⚖ Conciliación Médica de Antecedentes Simultáneos'}
                  </div>
                  <span className={`badge ${vm.pendingConflicts.length > 0 ? 'badge-red' : 'badge-green'}`}>
                    {vm.pendingConflicts.length} Pendientes
                  </span>
                </div>

                {vm.pendingConflicts.length === 0 ? (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    El expediente se encuentra conciliado y sin ediciones simultáneas pendientes de revisión.
                  </p>
                ) : (
                  vm.pendingConflicts.map((conf) => {
                    const currentRes = resolutionMap[conf.id] || {
                      chosen: `${conf.server_value}; ${conf.client_proposed_value}`,
                      notes: 'Se unifican ambos antecedentes clínicos reportados en traslado y recepción hospitalaria.',
                    };
                    return (
                      <div key={conf.id} className="vital-tile critical" style={{ marginBottom: '0.85rem' }}>
                        <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>
                          Edición simultánea detectada en <code>{conf.field_name}</code>
                        </div>
                        <div style={{ fontSize: '0.82rem', marginTop: '0.35rem' }}>
                          <div>
                            • <strong>Registro actual en Hospital:</strong> {conf.server_value}
                          </div>
                          <div>
                            • <strong>Registro enviado por {conf.submitted_by}:</strong> {conf.client_proposed_value}
                          </div>
                        </div>

                        <div className="form-group" style={{ marginTop: '0.6rem' }}>
                          <label className="form-label">Antecedente Clínico Unificado</label>
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
                          <label className="form-label">Nota Médica de Respaldo</label>
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
                          ✔ Confirmar y Firmar Conciliación Médica
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
            VISTA 3: TELECONSULTA Y ÓRDENES MÉDICAS (Mockup 3)
           ===================================================================== */}
        {vm.activeTab === 'TELECONSULTA' && patient && (
          <div className="grid-2col">
            {/* Consola de Videoconferencia */}
            <div className="clinical-card">
              <div className="card-header">
                <div>
                  <div className="brand-subtitle">UNIDAD MÓVIL 07 · TELECONSULTA EN RUTA</div>
                  <div className="card-title">
                    {arch
                      ? 'Sala Activa: SFU-SALA-MOVIL-07-URG (WebRTC / SRTP + ICE Restart 120s)'
                      : 'Conexión en Vivo con Especialista de Turno'}
                  </div>
                </div>
                <span className="badge badge-green">● CONECTADO · 38 ms</span>
              </div>

              <div
                style={{
                  backgroundColor: '#070b12',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '1.85rem 1.4rem',
                  textAlign: 'center',
                  position: 'relative',
                }}
              >
                <div style={{ position: 'absolute', top: '12px', left: '12px' }}>
                  <span className="badge badge-red">● EN VIVO · 04:12</span>
                </div>

                <div style={{ fontSize: '3rem', marginBottom: '0.4rem' }}>👩‍⚕️📡</div>
                <div style={{ fontWeight: 700, fontSize: '1.08rem' }}>
                  Dra. Elena Herrera Guzmán — Cardiología y Urgencia
                </div>
                <div className="brand-subtitle" style={{ marginTop: '0.2rem' }}>
                  {arch
                    ? 'Transporte Multimedia: SRTP/UDP vía Clúster SFU Multi-AZ (ADR-07 / ADR-08)'
                    : 'Audio y Video Cifrado de Baja Latencia'}
                </div>

                {/* Subtitulado Clínico en Vivo */}
                <div
                  style={{
                    marginTop: '1.35rem',
                    padding: '0.85rem 1.1rem',
                    backgroundColor: 'rgba(15, 23, 42, 0.92)',
                    border: '1px solid var(--accent-blue)',
                    borderRadius: '8px',
                    textAlign: 'left',
                  }}
                >
                  <div style={{ fontSize: '0.73rem', color: 'var(--accent-green)', fontWeight: 700 }}>
                    {arch
                      ? '💬 SUBTITULADO CLÍNICO EN VIVO (Doble Codificación ante Ruido de Sirena — Sección 2.2 #2):'
                      : '💬 TRANSCRIPCIÓN EN VIVO DEL ESPECIALISTA:'}
                  </div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 600, marginTop: '0.2rem' }}>
                    {patient.orders.length > 0
                      ? `Especialista (${patient.orders[patient.orders.length - 1].author_name}): "${
                          patient.orders[patient.orders.length - 1].medication_or_action
                        } — ${patient.orders[patient.orders.length - 1].dosage_and_route}."`
                      : 'Especialista: "Administren oxígeno a 4 litros por minuto. Preparen el acceso venoso."'}
                  </div>
                </div>
              </div>

              {/* Historial de Indicaciones */}
              <div style={{ marginTop: '1.1rem' }}>
                <div className="card-title" style={{ marginBottom: '0.55rem' }}>
                  📜 Indicaciones y Prescripciones del Episodio ({patient.orders.length})
                </div>
                {patient.orders.map((ord) => (
                  <div key={ord.id} className="vital-tile" style={{ marginBottom: '0.55rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span className="badge badge-blue">{ord.order_type}</span>
                      <span className="brand-subtitle">{ord.author_name}</span>
                    </div>
                    <div style={{ fontWeight: 700, marginTop: '0.3rem' }}>
                      {ord.medication_or_action} —{' '}
                      <span style={{ color: 'var(--accent-green)' }}>{ord.dosage_and_route}</span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                      Indicación: {ord.clinical_justification}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Columna Derecha: Emisión de Orden Médica */}
            <div className="clinical-card">
              <div className="card-header">
                <div className="card-title">
                  {arch
                    ? '💉 Emitir Orden Médica (Servicio Cohesivo Expediente-Órdenes ADR-03)'
                    : '💉 Registrar Indicación Médica o Receta Electrónica'}
                </div>
                <span className="badge badge-amber">
                  {arch ? 'Invariante ACID' : 'Control Farmacológico Activo'}
                </span>
              </div>

              <p style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', marginBottom: '0.85rem' }}>
                Alergias registradas del paciente: <strong style={{ color: '#fca5a5' }}>{patient.allergies}</strong>. El
                sistema verifica automáticamente contraindicaciones cruzadas antes de autorizar cualquier prescripción.
              </p>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  vm.submitMedicalOrder(orderForm);
                }}
              >
                <div className="form-group">
                  <label className="form-label">Tipo de Indicación</label>
                  <select
                    className="form-select"
                    value={orderForm.order_type}
                    onChange={(e) => setOrderForm({ ...orderForm, order_type: e.target.value })}
                  >
                    <option value="FARMACO">Prescripción de Fármaco</option>
                    <option value="TELECONSULTA">Indicación de Teleconsulta en Ruta</option>
                    <option value="PROCEDIMIENTO">Procedimiento Clínico</option>
                    <option value="DERIVACION">Derivación / Preparación de Box</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Medicamento o Acción Clínica</label>
                  <input
                    className="form-input"
                    value={orderForm.medication_or_action}
                    onChange={(e) => setOrderForm({ ...orderForm, medication_or_action: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Dosis y Vía de Administración</label>
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
                    ✍ Firmar y Emitir Indicación
                  </button>

                  <button
                    type="button"
                    className="btn-tactile btn-danger"
                    onClick={() =>
                      vm.submitMedicalOrder({
                        order_type: 'FARMACO',
                        medication_or_action: 'Amoxicilina / Ácido Clavulánico 1g EV',
                        dosage_and_route: '1g endovenoso cada 8 horas',
                        clinical_justification: 'Evaluación de alerta de alergia a Penicilina',
                      })
                    }
                  >
                    {arch
                      ? '🧪 Probar Bloqueo de Alergia a Penicilina (ADR-03)'
                      : '⚠ Probar Contraindicación (Amoxicilina EV)'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* =====================================================================
            VISTA 4: REGISTRO DE AUDITORÍA FORENSE
           ===================================================================== */}
        {vm.activeTab === 'AUDITORIA' && (
          <div className="clinical-card">
            <div className="card-header">
              <div>
                <div className="card-title">
                  {arch
                    ? '🔗 Ledger de Auditoría Forense Inmutable (Hash-Encadenado SHA-256 — ADR-03 y ADR-08)'
                    : '🛡 Registro Forense de Accesos y Modificaciones Clínicas'}
                </div>
                <div className="brand-subtitle">
                  {arch
                    ? 'Generado desacopladamente mediante el Patrón Observer (ForensicAuditLedgerObserver)'
                    : 'Trazabilidad inmutable de seguridad de datos de pacientes (Normativa HIPAA)'}
                </div>
              </div>
              <button
                type="button"
                className="btn-tactile btn-primary"
                onClick={() => vm.refreshClinicalData()}
              >
                🔍 Verificar Integridad del Registro
              </button>
            </div>

            {!vm.auditReport ? (
              <div className="notification-banner warning">
                <div>
                  <strong>Permiso Restringido:</strong> Su perfil actual ({user.role}) no cuenta con autorización para
                  inspeccionar la bitácora forense completa. Ingrese con perfil de Oficial de Privacidad o Médico.
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
                        ? '✔ REGISTRO DE AUDITORÍA ÍNTEGRO Y VERIFICADO (0 ADULTERACIONES)'
                        : '❌ ALERTA DE SEGURIDAD: ALTERACIÓN DETECTADA EN BITÁCORA'}
                    </div>
                    <div style={{ fontSize: '0.85rem', marginTop: '0.2rem' }}>
                      {vm.auditReport.status_message} · Sello Criptográfico Actual:{' '}
                      <code className="hash-code">{vm.auditReport.latest_hash}</code>
                    </div>
                  </div>
                </div>

                <div style={{ overflowX: 'auto' }}>
                  <table className="ledger-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Fecha y Hora UTC</th>
                        <th>Profesional</th>
                        <th>Operación</th>
                        <th>Expediente / Recurso</th>
                        <th>Detalle Clínico</th>
                        <th>Sello SHA-256 Encadenado</th>
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
                              Ant: {entry.prev_hash.slice(0, 12)}...
                            </div>
                            <div
                              className="hash-code"
                              style={{ marginTop: '0.2rem', color: '#6ee7b7' }}
                              title={entry.current_hash}
                            >
                              Act: {entry.current_hash.slice(0, 12)}...
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
