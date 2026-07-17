import type { OrdenLaboratorio } from '../types/lab';
import { apiRequest } from './http/httpClient';

export const labService = {
  orders: () => apiRequest<OrdenLaboratorio[]>('/api/v1/laboratorio/ordenes'),
};
