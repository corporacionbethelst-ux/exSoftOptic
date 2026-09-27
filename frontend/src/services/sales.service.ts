import type { ID } from '../types/common';
import type { DevolucionVentaPayload, Venta, VentaConfirmarPayload, VentaPayload } from '../types/sales';
import { apiRequest } from './http/httpClient';

export const SALES_MAX_LIMIT = 200;

export type SalesListParams = {
  skip?: number;
  /** Límite por petición; el backend lo acota a 200 (max). */
  limit?: number;
};

function salesQuery(params: SalesListParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 20));
  return query.toString();
}

/**
 * Paginación eficiente para agregaciones de cliente (dashboard KPIs):
 * recorre páginas de `limit` hasta agotar resultados o alcanzar `maxTotal`.
 */
async function fetchAllPages<T>(fetchPage: (skip: number) => Promise<T[]>, { limit = SALES_MAX_LIMIT, maxTotal = 1000 } = {}): Promise<T[]> {
  const collected: T[] = [];
  for (let skip = 0; skip < maxTotal; skip += limit) {
    const page = await fetchPage(skip);
    collected.push(...page);
    if (page.length < limit) break;
  }
  return collected;
}

export const salesService = {
  list: (params?: SalesListParams) => apiRequest<Venta[]>(`/api/v1/ventas/?${salesQuery(params)}`),
  /** Ventas recientes (orden descendente por fecha en backend) para KPIs de día/semana. */
  recent: (limit = SALES_MAX_LIMIT) => apiRequest<Venta[]>(`/api/v1/ventas/?skip=0&limit=${limit}`),
  /** Todas las ventas hasta `maxTotal` usando paginación eficiente (agregaciones cliente). */
  all: (maxTotal = 1000) => fetchAllPages((skip) => salesService.list({ skip, limit: SALES_MAX_LIMIT }), { maxTotal }),
  get: (id: ID) => apiRequest<Venta>(`/api/v1/ventas/${id}`),
  create: (payload: VentaPayload) => apiRequest<Venta>('/api/v1/ventas/', { method: 'POST', body: JSON.stringify(payload) }),
  confirm: (id: ID, payload: VentaConfirmarPayload) =>
    apiRequest<Venta>(`/api/v1/ventas/${id}/confirmar`, { method: 'POST', body: JSON.stringify(payload) }),
  returnSale: (id: ID, payload: DevolucionVentaPayload) =>
    apiRequest<unknown>(`/api/v1/ventas/${id}/devoluciones`, { method: 'POST', body: JSON.stringify(payload) }),
};
