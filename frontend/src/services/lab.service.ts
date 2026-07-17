import type { ID } from '../types/common';
import type { ConsumoMaterialLaboratorio, ConsumoMaterialPayload, ControlCalidadPayload, OrdenLaboratorio, OrdenLaboratorioFromVentaPayload } from '../types/lab';
import { apiRequest } from './http/httpClient';

export type LabListParams = {
  skip?: number;
  limit?: number;
};

function labQuery(params: LabListParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 50));
  return query.toString();
}

export const labService = {
  orders: (params?: LabListParams) => apiRequest<OrdenLaboratorio[]>(`/api/v1/laboratorio/ordenes?${labQuery(params)}`),
  order: (id: ID) => apiRequest<OrdenLaboratorio>(`/api/v1/laboratorio/ordenes/${id}`),
  createFromSale: (saleId: ID, payload: OrdenLaboratorioFromVentaPayload) =>
    apiRequest<OrdenLaboratorio>(`/api/v1/laboratorio/ordenes/from-venta/${saleId}`, { method: 'POST', body: JSON.stringify(payload) }),
  start: (id: ID) => apiRequest<OrdenLaboratorio>(`/api/v1/laboratorio/ordenes/${id}/iniciar`, { method: 'POST' }),
  completeStage: (orderId: ID, stageId: ID, observaciones?: string | null) =>
    apiRequest<OrdenLaboratorio>(`/api/v1/laboratorio/ordenes/${orderId}/etapas/${stageId}/completar`, { method: 'POST', body: JSON.stringify({ observaciones }) }),
  registerConsumption: (orderId: ID, payload: ConsumoMaterialPayload) =>
    apiRequest<ConsumoMaterialLaboratorio>(`/api/v1/laboratorio/ordenes/${orderId}/consumos`, { method: 'POST', body: JSON.stringify(payload) }),
  qualityControl: (orderId: ID, payload: ControlCalidadPayload) =>
    apiRequest<OrdenLaboratorio>(`/api/v1/laboratorio/ordenes/${orderId}/control-calidad`, { method: 'POST', body: JSON.stringify(payload) }),
  deliver: (id: ID) => apiRequest<OrdenLaboratorio>(`/api/v1/laboratorio/ordenes/${id}/entregar`, { method: 'POST' }),
};
