import type { BalanceGeneral, BalanzaComprobacion, EstadoResultados, InventarioValuado, LibroDiario, MargenVentas, AuditoriaEvento, AuditoriaVerificacion, RuntimeMetrics } from '../types/reports';
import { apiRequest } from './http/httpClient';

type DateRange = { fecha_inicio?: string; fecha_fin?: string };
function rangeQuery(params: DateRange = {}) { const q = new URLSearchParams(); if (params.fecha_inicio) q.set('fecha_inicio', params.fecha_inicio); if (params.fecha_fin) q.set('fecha_fin', params.fecha_fin); return q.toString(); }

export const reportsService = {
  trialBalance: (params?: DateRange) => apiRequest<BalanzaComprobacion>(`/api/v1/reportes/contabilidad/balanza?${rangeQuery(params)}`),
  journal: (params?: DateRange) => apiRequest<LibroDiario>(`/api/v1/reportes/contabilidad/diario?${rangeQuery(params)}`),
  incomeStatement: (params?: DateRange) => apiRequest<EstadoResultados>(`/api/v1/reportes/contabilidad/estado-resultados?${rangeQuery(params)}`),
  balanceSheet: (fecha_fin?: string) => apiRequest<BalanceGeneral>(`/api/v1/reportes/contabilidad/balance-general?${fecha_fin ? `fecha_fin=${fecha_fin}` : ''}`),
  inventoryValuation: () => apiRequest<InventarioValuado>('/api/v1/reportes/inventario/valuado'),
  salesMargins: (params?: DateRange) => apiRequest<MargenVentas>(`/api/v1/reportes/ventas/margenes?${rangeQuery(params)}`),
  auditEvents: (limit = 100) => apiRequest<AuditoriaEvento[]>(`/api/v1/auditoria/?limit=${limit}`),
  verifyAuditChain: () => apiRequest<AuditoriaVerificacion>('/api/v1/auditoria/verificar-cadena'),
  metrics: () => apiRequest<RuntimeMetrics>('/api/v1/observabilidad/metrics'),
  cleanupIdempotency: (limit = 500) => apiRequest<{ deleted: number; limit: number }>(`/api/v1/observabilidad/maintenance/idempotency/cleanup?limit=${limit}`, { method: 'POST' }),
};
