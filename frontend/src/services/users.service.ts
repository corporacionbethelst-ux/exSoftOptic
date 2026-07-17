import type { ID } from '../types/common';
import type { PaginatedUsers, Rol, RolPayload, Usuario, UsuarioPayload, UsuarioUpdatePayload } from '../types/auth';
import { apiRequest } from './http/httpClient';

export type UserListParams = {
  page?: number;
  perPage?: number;
  search?: string;
  rolId?: ID;
  estaActivo?: boolean;
};

function userQuery(params: UserListParams = {}) {
  const query = new URLSearchParams();
  query.set('page', String(params.page ?? 1));
  query.set('per_page', String(params.perPage ?? 20));
  if (params.search?.trim()) query.set('search', params.search.trim());
  if (params.rolId) query.set('rol_id', params.rolId);
  if (typeof params.estaActivo === 'boolean') query.set('esta_activo', String(params.estaActivo));
  return query.toString();
}

export const usersService = {
  list: (params?: UserListParams) => apiRequest<PaginatedUsers>(`/api/v1/usuarios/?${userQuery(params)}`),
  get: (id: ID) => apiRequest<Usuario>(`/api/v1/usuarios/${id}`),
  create: (payload: UsuarioPayload) => apiRequest<Usuario>('/api/v1/usuarios/', { method: 'POST', body: JSON.stringify(payload) }),
  update: (id: ID, payload: UsuarioUpdatePayload) => apiRequest<Usuario>(`/api/v1/usuarios/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  remove: (id: ID) => apiRequest<{ message: string }>(`/api/v1/usuarios/${id}`, { method: 'DELETE' }),
  roles: () => apiRequest<Rol[]>('/api/v1/usuarios/roles'),
  createRole: (payload: RolPayload) => apiRequest<Rol>('/api/v1/usuarios/roles', { method: 'POST', body: JSON.stringify(payload) }),
};
