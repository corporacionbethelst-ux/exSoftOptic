import type { LoginRequest, LoginResponse, Usuario } from '../types/auth';
import { apiRequest } from './http/httpClient';

export const authService = {
  login: (payload: LoginRequest) =>
    apiRequest<LoginResponse>('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  me: () => apiRequest<Usuario>('/api/v1/auth/me'),
};
