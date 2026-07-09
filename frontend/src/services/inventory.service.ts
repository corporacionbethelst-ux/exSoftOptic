import type { KardexMovimiento } from '../types/inventory';
import { apiRequest } from './http/httpClient';

export const inventoryService = {
  kardex: () => apiRequest<KardexMovimiento[]>('/api/v1/inventario/kardex'),
};
