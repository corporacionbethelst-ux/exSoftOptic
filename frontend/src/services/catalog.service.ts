import type { ProductoListResponse } from '../types/catalog';
import { apiRequest } from './http/httpClient';

export const catalogService = {
  products: () => apiRequest<ProductoListResponse>('/api/v1/productos/?page=1&per_page=20'),
};
