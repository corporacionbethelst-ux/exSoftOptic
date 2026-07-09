import type { Venta } from '../types/sales';
import { apiRequest } from './http/httpClient';

export const salesService = {
  list: () => apiRequest<Venta[]>('/api/v1/ventas/?skip=0&limit=20'),
};
