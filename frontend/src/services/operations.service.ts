import type { ID } from '../types/common';
import type { DispatchResult, MaintenanceCleanupResult, OutboxEvent, OutboxEventPayload, OutboxFailurePayload, ReadinessStatus, RuntimeMetrics } from '../types/operations';
import { apiRequest } from './http/httpClient';

type ListParams = { limit?: number };
function limitQuery(params: ListParams = {}) { return `limit=${params.limit ?? 100}`; }

export const operationsService = {
  readiness: () => apiRequest<ReadinessStatus>('/api/v1/observabilidad/readiness'),
  metrics: () => apiRequest<RuntimeMetrics>('/api/v1/observabilidad/metrics'),
  cleanupIdempotency: (limit = 500) => apiRequest<MaintenanceCleanupResult>(`/api/v1/observabilidad/maintenance/idempotency/cleanup?limit=${limit}`, { method: 'POST' }),
  pendingOutbox: (params?: ListParams) => apiRequest<OutboxEvent[]>(`/api/v1/outbox/events/pending?${limitQuery(params)}`),
  createOutboxEvent: (payload: OutboxEventPayload) => apiRequest<OutboxEvent>('/api/v1/outbox/events', { method: 'POST', body: JSON.stringify(payload) }),
  markProcessing: (id: ID) => apiRequest<OutboxEvent>(`/api/v1/outbox/events/${id}/processing`, { method: 'POST' }),
  markPublished: (id: ID) => apiRequest<OutboxEvent>(`/api/v1/outbox/events/${id}/published`, { method: 'POST' }),
  markFailed: (id: ID, payload: OutboxFailurePayload) => apiRequest<OutboxEvent>(`/api/v1/outbox/events/${id}/failed`, { method: 'POST', body: JSON.stringify(payload) }),
  dispatchOutbox: (limit = 100) => apiRequest<DispatchResult>(`/api/v1/outbox/events/dispatch?limit=${limit}`, { method: 'POST' }),
};
