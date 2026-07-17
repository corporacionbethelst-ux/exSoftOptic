import type { ID } from '../types/common';
import type { InventarioAlerta, InventarioEntradaPayload, InventarioSalidaPayload, KardexMovimiento } from '../types/inventory';
import { apiRequest } from './http/httpClient';

export type InventoryKardexParams = {
  producto_id?: ID;
  skip?: number;
  limit?: number;
};

export type InventoryAlertParams = {
  sucursal_id?: ID;
  skip?: number;
  limit?: number;
};

function kardexQuery(params: InventoryKardexParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 50));
  if (params.producto_id) query.set('producto_id', params.producto_id);
  return query.toString();
}

function alertQuery(params: InventoryAlertParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 100));
  if (params.sucursal_id) query.set('sucursal_id', params.sucursal_id);
  return query.toString();
}

export const inventoryService = {
  kardex: (params?: InventoryKardexParams) => apiRequest<KardexMovimiento[]>(`/api/v1/inventario/kardex?${kardexQuery(params)}`),
  entrada: (payload: InventarioEntradaPayload) => apiRequest<KardexMovimiento>('/api/v1/inventario/entradas', { method: 'POST', body: JSON.stringify(payload) }),
  salida: (payload: InventarioSalidaPayload) => apiRequest<KardexMovimiento>('/api/v1/inventario/salidas', { method: 'POST', body: JSON.stringify(payload) }),
  stockAlerts: (params?: InventoryAlertParams) => apiRequest<InventarioAlerta[]>(`/api/v1/inventario/alertas/stock-minimo?${alertQuery(params)}`),
};
