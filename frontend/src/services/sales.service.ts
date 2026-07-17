import type { ID } from '../types/common';
import type { DevolucionVentaPayload, Venta, VentaConfirmarPayload, VentaPayload } from '../types/sales';
import { apiRequest } from './http/httpClient';

export type SalesListParams = {
  skip?: number;
  limit?: number;
};

function salesQuery(params: SalesListParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 20));
  return query.toString();
}

export const salesService = {
  list: (params?: SalesListParams) => apiRequest<Venta[]>(`/api/v1/ventas/?${salesQuery(params)}`),
  get: (id: ID) => apiRequest<Venta>(`/api/v1/ventas/${id}`),
  create: (payload: VentaPayload) => apiRequest<Venta>('/api/v1/ventas/', { method: 'POST', body: JSON.stringify(payload) }),
  confirm: (id: ID, payload: VentaConfirmarPayload) =>
    apiRequest<Venta>(`/api/v1/ventas/${id}/confirmar`, { method: 'POST', body: JSON.stringify(payload) }),
  returnSale: (id: ID, payload: DevolucionVentaPayload) =>
    apiRequest<unknown>(`/api/v1/ventas/${id}/devoluciones`, { method: 'POST', body: JSON.stringify(payload) }),
};
