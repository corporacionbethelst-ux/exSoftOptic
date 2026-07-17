import type { ID } from '../types/common';
import type { InventarioAlerta, KardexMovimiento } from '../types/inventory';
import { apiRequest } from './http/httpClient';

export type InventoryAlertParams = {
  sucursal_id?: ID;
  skip?: number;
  limit?: number;
};

function alertQuery(params: InventoryAlertParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 100));
  if (params.sucursal_id) query.set('sucursal_id', params.sucursal_id);
  return query.toString();
}

export const inventoryService = {
  kardex: () => apiRequest<KardexMovimiento[]>('/api/v1/inventario/kardex'),
  stockAlerts: (params?: InventoryAlertParams) => apiRequest<InventarioAlerta[]>(`/api/v1/inventario/alertas/stock-minimo?${alertQuery(params)}`),
};
