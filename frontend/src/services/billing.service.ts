import type { ID } from '../types/common';
import type { Factura, FacturaCancelarPayload, FacturaEmitirPayload, Garantia, GarantiaFromOrdenPayload, GarantiaPayload, ReclamacionGarantia, ReclamacionGarantiaPayload, ResolverReclamacionPayload } from '../types/billing';
import { apiRequest } from './http/httpClient';

type ListParams = { skip?: number; limit?: number };
function query(params: ListParams = {}) { const q = new URLSearchParams(); q.set('skip', String(params.skip ?? 0)); q.set('limit', String(params.limit ?? 50)); return q.toString(); }
function key() { return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`; }

export const billingService = {
  invoices: (params?: ListParams) => apiRequest<Factura[]>(`/api/v1/facturacion/?${query(params)}`),
  invoice: (id: ID) => apiRequest<Factura>(`/api/v1/facturacion/${id}`),
  issueInvoice: (payload: FacturaEmitirPayload) => apiRequest<Factura>('/api/v1/facturacion/emitir', { method: 'POST', headers: { 'Idempotency-Key': key() }, body: JSON.stringify(payload) }),
  cancelInvoice: (id: ID, payload: FacturaCancelarPayload) => apiRequest<Factura>(`/api/v1/facturacion/${id}/cancelar`, { method: 'POST', headers: { 'Idempotency-Key': key() }, body: JSON.stringify(payload) }),
  warranties: (params?: ListParams) => apiRequest<Garantia[]>(`/api/v1/garantias/?${query(params)}`),
  warranty: (id: ID) => apiRequest<Garantia>(`/api/v1/garantias/${id}`),
  createWarranty: (payload: GarantiaPayload) => apiRequest<Garantia>('/api/v1/garantias/', { method: 'POST', body: JSON.stringify(payload) }),
  createWarrantyFromLab: (orderId: ID, payload: GarantiaFromOrdenPayload) => apiRequest<Garantia>(`/api/v1/garantias/from-laboratorio/${orderId}`, { method: 'POST', body: JSON.stringify(payload) }),
  openClaim: (warrantyId: ID, payload: ReclamacionGarantiaPayload) => apiRequest<ReclamacionGarantia>(`/api/v1/garantias/${warrantyId}/reclamaciones`, { method: 'POST', body: JSON.stringify(payload) }),
  resolveClaim: (claimId: ID, payload: ResolverReclamacionPayload) => apiRequest<Garantia>(`/api/v1/garantias/reclamaciones/${claimId}/resolver`, { method: 'POST', body: JSON.stringify(payload) }),
};
