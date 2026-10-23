/**
 * CAPA MODEL (MVVM — ADR-01 y ADR-02)
 * Responsabilidad:
 * - Gestiona el transporte HTTP/REST siguiendo contratos FHIR R4 (ADR-08).
 * - Implementa la Cola Transaccional de Salida (Transactional Outbox / Store-and-Forward ADR-02 y ADR-04)
 *   para almacenar eventos firmados con UUID de idempotencia cuando la ambulancia entra en modo Offline
 *   (túneles, zonas sin cobertura celular) y drenarlos automáticamente al restablecer la red.
 */

const OUTBOX_STORAGE_KEY = 'hce_caso5_transactional_outbox_v2';

export function getOutboxQueue() {
  try {
    const raw = localStorage.getItem(OUTBOX_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function enqueueOutboxTransaction(transaction) {
  const queue = getOutboxQueue();
  const item = {
    ...transaction,
    queuedAt: new Date().toISOString(),
    sequenceNumber: queue.length + 1,
  };
  queue.push(item);
  localStorage.setItem(OUTBOX_STORAGE_KEY, JSON.stringify(queue));
  return queue;
}

export function clearOutboxTransaction(idempotencyKey) {
  const queue = getOutboxQueue().filter((tx) => tx.idempotencyKey !== idempotencyKey);
  localStorage.setItem(OUTBOX_STORAGE_KEY, JSON.stringify(queue));
  return queue;
}

async function requestJson(url, options = {}, token = null) {
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errorMsg = data.detail || `Error HTTP ${response.status}`;
    const err = new Error(errorMsg);
    err.status = response.status;
    err.payload = data;
    throw err;
  }
  return data;
}

export const ClinicalApiModel = {
  getDemoUsers: () => requestJson('/api/v1/auth/demo-users'),

  login: (username, password, deviceNode) =>
    requestJson('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password, device_node: deviceNode }),
    }),

  listPatients: (token) => requestJson('/api/v1/fhir/patients', {}, token),

  getPatientEHR: (patientId, token) =>
    requestJson(`/api/v1/fhir/patients/${patientId}`, {}, token),

  recordVitalSigns: (patientId, payload, token) =>
    requestJson(
      `/api/v1/fhir/patients/${patientId}/vital-signs`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      token
    ),

  updateMutableField: (patientId, payload, token) =>
    requestJson(
      `/api/v1/fhir/patients/${patientId}/mutable-fields`,
      {
        method: 'PUT',
        body: JSON.stringify(payload),
      },
      token
    ),

  resolveConflict: (conflictId, payload, token) =>
    requestJson(
      `/api/v1/fhir/conflicts/${conflictId}/resolve`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      token
    ),

  createMedicalOrder: (patientId, payload, token) =>
    requestJson(
      `/api/v1/fhir/patients/${patientId}/orders`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      token
    ),

  verifyAuditChain: (token) =>
    requestJson('/api/v1/audit/verify-chain', {}, token),
};
