/**
 * PATRÓN ARQUITECTÓNICO DE PRESENTACIÓN: MVVM (Model - View - ViewModel, ADR-01)
 * -----------------------------------------------------------------------------
 * Problema que resuelve:
 * Desacopla la lógica de presentación clínica —reglas de despliegue de alertas semánticas,
 * máquina de estados del episodio offline-first (ADR-02), conmutación de alto contraste WCAG 2.2 AAA (Sección 2.2)
 * y drenaje de la cola Store-and-Forward con claves de idempotencia UUID (ADR-04)— respecto del árbol visual React.
 *
 * Beneficio verificable:
 * La Vista (`App.jsx`) es puramente declarativa y se limita a enlazar (data-binding) las propiedades observables
 * y comandos expuestos por `useClinicalViewModel()`.
 */
import { useState, useEffect, useCallback } from 'react';
import {
  ClinicalApiModel,
  getOutboxQueue,
  enqueueOutboxTransaction,
  clearOutboxTransaction,
} from '../models/clinicalApi';

function generateUUID() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'uuid-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9);
}

export function useClinicalViewModel() {
  // 1. Estado de Autenticación y RBAC (ADR-02 / ADR-08)
  const [session, setSession] = useState(null);
  const [demoUsers, setDemoUsers] = useState([]);
  const [authError, setAuthError] = useState(null);

  // 2. Estado de Accesibilidad y Conectividad Offline-First (Sección 2.2 y ADR-02 / ADR-04)
  const [highContrastAAA, setHighContrastAAA] = useState(false); // Solución Problema Crítico #1 (WCAG 2.2 AAA 7:1)
  const [isOfflineTunnel, setIsOfflineTunnel] = useState(false); // Simulador de pérdida de señal en túnel
  const [outboxQueue, setOutboxQueue] = useState(() => getOutboxQueue());
  const [episodeState, setEpisodeState] = useState('CONFIRMADO_EN_SERVIDOR'); // BORRADOR | ENCOLADO_OUTBOX | TRANSMITIENDO | CONFIRMADO_EN_SERVIDOR

  // 3. Estado Clínico Observable (FHIR R4 Patient, Observations, Orders, Conflicts, Audit Ledger)
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(1);
  const [currentPatient, setCurrentPatient] = useState(null);
  const [auditReport, setAuditReport] = useState(null);
  const [activeTab, setActiveTab] = useState('URGENCIA'); // URGENCIA | FICHA_FHIR | TELECONSULTA | AUDITORIA
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  const notify = useCallback((type, title, detail) => {
    setNotification({ type, title, detail, timestamp: new Date().toLocaleTimeString() });
  }, []);

  // Cargar usuarios de demostración al iniciar
  useEffect(() => {
    ClinicalApiModel.getDemoUsers()
      .then(setDemoUsers)
      .catch(() => {});
  }, []);

  // Cargar expediente completo del paciente e informe de auditoría cuando cambia la sesión o el paciente
  const refreshClinicalData = useCallback(
    async (tokenToUse = session?.access_token, patientIdToLoad = selectedPatientId) => {
      if (!tokenToUse) return;
      setLoading(true);
      try {
        const [patientList, ehrDetail] = await Promise.all([
          ClinicalApiModel.listPatients(tokenToUse),
          ClinicalApiModel.getPatientEHR(patientIdToLoad, tokenToUse),
        ]);
        setPatients(patientList);
        setCurrentPatient(ehrDetail);

        // Si el rol tiene permiso de auditoría (Auditor, Médico Urgencia o Teleconsultor), cargar cadena SHA-256
        try {
          const audit = await ClinicalApiModel.verifyAuditChain(tokenToUse);
          setAuditReport(audit);
        } catch {
          setAuditReport(null);
        }
      } catch (err) {
        notify('error', 'Error al sincronizar HCE FHIR R4', err.message);
      } finally {
        setLoading(false);
      }
    },
    [session, selectedPatientId, notify]
  );

  useEffect(() => {
    if (session?.access_token && !isOfflineTunnel) {
      refreshClinicalData(session.access_token, selectedPatientId);
    }
  }, [session, selectedPatientId, isOfflineTunnel, refreshClinicalData]);

  // Comando: Login con Rol (RBAC)
  const loginWithCredentials = async (username, password, deviceNode) => {
    setAuthError(null);
    setLoading(true);
    try {
      const tokenResp = await ClinicalApiModel.login(username, password, deviceNode);
      setSession(tokenResp);
      if (tokenResp.user.role === 'AUDITOR_FORENSE') {
        setActiveTab('AUDITORIA');
      } else if (tokenResp.user.role === 'MEDICO_TELECONSULTOR') {
        setActiveTab('TELECONSULTA');
      } else {
        setActiveTab('URGENCIA');
      }
      notify(
        'success',
        `Sesión autenticada (${tokenResp.user.role})`,
        `Bienvenido/a ${tokenResp.user.full_name}. Credencial JWT activa (15 min) + Token Offline (72h).`
      );
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setSession(null);
    setCurrentPatient(null);
    setAuditReport(null);
    setNotification(null);
  };

  // Comando: Registrar Signos Vitales / Triage (con soporte Offline Store-and-Forward ADR-02 / ADR-04)
  const submitVitalSigns = async (vitalsForm) => {
    if (!session) return;
    const payload = {
      idempotency_key: vitalsForm.idempotency_key || `outbox-${generateUUID()}`,
      episode_code: 'URG-2026-0084',
      heart_rate_bpm: Number(vitalsForm.heart_rate_bpm),
      spo2_percent: Number(vitalsForm.spo2_percent),
      systolic_bp: Number(vitalsForm.systolic_bp),
      diastolic_bp: Number(vitalsForm.diastolic_bp),
      temperature_c: Number(vitalsForm.temperature_c),
      glasgow_score: Number(vitalsForm.glasgow_score || 15),
      origin_node: isOfflineTunnel
        ? `${session.user.facility} [Encolado Offline Outbox]`
        : session.user.facility,
      clinical_notes: vitalsForm.clinical_notes || '',
    };

    if (isOfflineTunnel) {
      const updatedQueue = enqueueOutboxTransaction({
        idempotencyKey: payload.idempotency_key,
        type: 'VITAL_SIGNS',
        patientId: selectedPatientId,
        payload,
      });
      setOutboxQueue(updatedQueue);
      setEpisodeState('ENCOLADO_OUTBOX');
      notify(
        'warning',
        'Sin cobertura celular — Almacenado en Outbox Local (ADR-02 / ADR-04)',
        `Registro firmado con clave de idempotencia ${payload.idempotency_key.slice(0, 18)}... Se drenará automáticamente al salir del túnel.`
      );
      return;
    }

    try {
      setEpisodeState('TRANSMITIENDO');
      const created = await ClinicalApiModel.recordVitalSigns(
        selectedPatientId,
        payload,
        session.access_token
      );
      setEpisodeState('CONFIRMADO_EN_SERVIDOR');
      notify(
        created.is_critical ? 'critical' : 'success',
        `Triage registrado: ${created.triage_category}`,
        created.clinical_alerts
      );
      await refreshClinicalData();
    } catch (err) {
      setEpisodeState('BORRADOR');
      notify('error', 'Rechazo de validación o permisos en Triage', err.message);
    }
  };

  // Comando: Drenar la Cola Store-and-Forward al recuperar conectividad (ADR-02 / ADR-04)
  const drainOutboxQueue = useCallback(async () => {
    const queue = getOutboxQueue();
    if (!session || queue.length === 0) return;

    setEpisodeState('TRANSMITIENDO');
    let drainedCount = 0;
    for (const item of queue) {
      try {
        if (item.type === 'VITAL_SIGNS') {
          await ClinicalApiModel.recordVitalSigns(
            item.patientId,
            item.payload,
            session.access_token
          );
        }
        clearOutboxTransaction(item.idempotencyKey);
        drainedCount += 1;
      } catch (err) {
        notify('error', 'Error drenando transacción Outbox', err.message);
      }
    }
    setOutboxQueue(getOutboxQueue());
    setEpisodeState('CONFIRMADO_EN_SERVIDOR');
    if (drainedCount > 0) {
      notify(
        'success',
        `Sincronización Store-and-Forward completada (${drainedCount} eventos)`,
        'La cola Outbox local fue drenada con verificación de idempotencia UUID sin duplicar registros clínicos.'
      );
      await refreshClinicalData();
    }
  }, [session, notify, refreshClinicalData]);

  // Conmutar Modo Túnel (Offline / Online) y drenar automáticamente al volver a Online
  const toggleOfflineTunnel = async () => {
    const nextOffline = !isOfflineTunnel;
    setIsOfflineTunnel(nextOffline);
    if (nextOffline) {
      setEpisodeState(outboxQueue.length > 0 ? 'ENCOLADO_OUTBOX' : 'BORRADOR');
      notify(
        'warning',
        'Modo Túnel / Sombra Celular Activado (Offline-First ADR-02)',
        'Las capturas de signos vitales se persistirán localmente en la cola transaccional Outbox con UUID de idempotencia.'
      );
    } else {
      await drainOutboxQueue();
    }
  };

  // Comando: Actualizar campo mutable con Control de Concurrencia Optimista (ADR-05)
  const updateMutableField = async (fieldName, newValue, expectedVersionOverride = null) => {
    if (!session || !currentPatient) return;
    const expectedVersion =
      expectedVersionOverride !== null ? Number(expectedVersionOverride) : currentPatient.version;

    try {
      const result = await ClinicalApiModel.updateMutableField(
        currentPatient.id,
        {
          field_name: fieldName,
          new_value: newValue,
          expected_version: expectedVersion,
          origin_node: session.user.facility,
        },
        session.access_token
      );

      if (result.status === 'CONFLICT_QUEUED') {
        notify(
          'critical',
          'CONFLICTO DE SINCRONIZACIÓN DETECTADO (ADR-05)',
          result.message
        );
      } else {
        notify('success', `Campo '${fieldName}' actualizado (v${result.new_version})`, result.message);
      }
      await refreshClinicalData();
    } catch (err) {
      notify('error', 'Error al actualizar expediente mutable', err.message);
    }
  };

  // Comando: Resolver Conflicto en Cola de Arbitraje Clínico (ADR-05)
  const resolveClinicalConflict = async (conflictId, chosenValue, resolutionNotes) => {
    if (!session) return;
    try {
      const res = await ClinicalApiModel.resolveConflict(
        conflictId,
        { chosen_value: chosenValue, resolution_notes: resolutionNotes },
        session.access_token
      );
      notify(
        'success',
        `Arbitraje Clínico ADR-05 Resuelto (Nueva v${res.patient_version})`,
        `Se aplicó el valor conciliado: "${res.chosen_value}" y se firmó en el Ledger de Auditoría.`
      );
      await refreshClinicalData();
    } catch (err) {
      notify('error', 'No se pudo resolver el arbitraje clínico', err.message);
    }
  };

  // Comando: Emitir Orden Médica o Directiva de Teleconsulta (ADR-03)
  const submitMedicalOrder = async (orderForm) => {
    if (!session || !currentPatient) return;
    try {
      const created = await ClinicalApiModel.createMedicalOrder(
        currentPatient.id,
        {
          idempotency_key: `order-${generateUUID()}`,
          episode_code: 'URG-2026-0084',
          order_type: orderForm.order_type,
          medication_or_action: orderForm.medication_or_action,
          dosage_and_route: orderForm.dosage_and_route,
          clinical_justification: orderForm.clinical_justification,
          teleconsultation_room_id:
            orderForm.order_type === 'TELECONSULTA' ? 'SFU-SALA-MOVIL-07-URG' : null,
        },
        session.access_token
      );
      notify(
        'success',
        `Orden Médica [${created.order_type}] Firmada`,
        `${created.medication_or_action} — ${created.dosage_and_route}`
      );
      await refreshClinicalData();
    } catch (err) {
      notify('critical', 'Orden Rechazada por Regla de Seguridad / RBAC', err.message);
      // Refrescar también el ledger de auditoría porque el rechazo se registra forensemente
      await refreshClinicalData();
    }
  };

  // Estado semántico derivado en el ViewModel (ADR-01): última lectura de signos vitales
  const latestVitals =
    currentPatient?.vital_signs?.length > 0
      ? currentPatient.vital_signs[currentPatient.vital_signs.length - 1]
      : null;

  const pendingConflicts =
    currentPatient?.conflicts?.filter((c) => c.status === 'PENDIENTE') || [];

  return {
    // Estado
    session,
    demoUsers,
    authError,
    highContrastAAA,
    isOfflineTunnel,
    outboxQueue,
    episodeState,
    patients,
    selectedPatientId,
    currentPatient,
    latestVitals,
    pendingConflicts,
    auditReport,
    activeTab,
    loading,
    notification,

    // Comandos del ViewModel
    setHighContrastAAA,
    setSelectedPatientId,
    setActiveTab,
    setNotification,
    loginWithCredentials,
    logout,
    toggleOfflineTunnel,
    submitVitalSigns,
    drainOutboxQueue,
    updateMutableField,
    resolveClinicalConflict,
    submitMedicalOrder,
    refreshClinicalData,
  };
}
