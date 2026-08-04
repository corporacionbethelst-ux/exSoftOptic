import type { LoginRequest, LoginResponse, RefreshTokenResponse, Usuario } from '../types/auth';
import { apiRequest } from './http/httpClient';

export const authService = {
  login: (payload: LoginRequest) =>
    apiRequest<LoginResponse>('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  refresh: (refreshToken: string) =>
    apiRequest<RefreshTokenResponse>('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
      skipAuthRefresh: true,
    }),
  logout: () => apiRequest<{ message: string }>('/api/v1/auth/logout', { method: 'POST', skipAuthRefresh: true }),
  me: () => apiRequest<Usuario>('/api/v1/auth/me'),
};
