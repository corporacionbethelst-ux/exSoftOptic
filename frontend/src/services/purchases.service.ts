import type { ID } from '../types/common';
import type { OrdenCompra, OrdenCompraPayload, RecepcionCompra, RecepcionCompraPayload, SolicitudCompra, SolicitudCompraPayload } from '../types/purchases';
import { apiRequest } from './http/httpClient';

export type PurchaseListParams = {
  skip?: number;
  limit?: number;
};

function purchaseQuery(params: PurchaseListParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 20));
  return query.toString();
}

export const purchasesService = {
  listOrders: (params?: PurchaseListParams) => apiRequest<OrdenCompra[]>(`/api/v1/compras/ordenes?${purchaseQuery(params)}`),
  getOrder: (id: ID) => apiRequest<OrdenCompra>(`/api/v1/compras/ordenes/${id}`),
  createOrder: (payload: OrdenCompraPayload) => apiRequest<OrdenCompra>('/api/v1/compras/ordenes', { method: 'POST', body: JSON.stringify(payload) }),
  approveOrder: (id: ID) => apiRequest<OrdenCompra>(`/api/v1/compras/ordenes/${id}/aprobar`, { method: 'POST' }),
  receiveOrder: (id: ID, payload: RecepcionCompraPayload) =>
    apiRequest<RecepcionCompra>(`/api/v1/compras/ordenes/${id}/recepciones`, {
      method: 'POST',
      body: JSON.stringify(payload),
      headers: { 'Idempotency-Key': `purchase-receipt-${id}-${payload.folio}` },
    }),
  generateStockRequisition: (payload: SolicitudCompraPayload) =>
    apiRequest<SolicitudCompra>('/api/v1/compras/solicitudes/generar-stock-minimo', { method: 'POST', body: JSON.stringify(payload) }),
};
