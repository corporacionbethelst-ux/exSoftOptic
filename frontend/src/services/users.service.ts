import type { PaginatedUsers } from '../types/auth';
import { apiRequest } from './http/httpClient';

export const usersService = {
  list: () => apiRequest<PaginatedUsers>('/api/v1/usuarios/?page=1&per_page=20'),
};
