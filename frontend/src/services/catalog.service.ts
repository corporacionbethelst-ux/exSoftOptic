import type { ID } from '../types/common';
import type { Producto, ProductoListResponse, ProductoPayload } from '../types/catalog';
import { apiRequest } from './http/httpClient';

export type ProductListParams = {
  skip?: number;
  limit?: number;
  search?: string;
};

function productQuery(params: ProductListParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 20));
  if (params.search?.trim()) query.set('search', params.search.trim());
  return query.toString();
}

export const catalogService = {
  products: (params?: ProductListParams) => apiRequest<ProductoListResponse>(`/api/v1/productos/?${productQuery(params)}`),
  product: (id: ID) => apiRequest<Producto>(`/api/v1/productos/${id}`),
  createProduct: (payload: ProductoPayload) =>
    apiRequest<Producto>('/api/v1/productos/', { method: 'POST', body: JSON.stringify(payload) }),
  updateProduct: (id: ID, payload: Partial<ProductoPayload>) =>
    apiRequest<Producto>(`/api/v1/productos/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),
  deleteProduct: (id: ID) => apiRequest<{ message: string }>(`/api/v1/productos/${id}`, { method: 'DELETE' }),
};
