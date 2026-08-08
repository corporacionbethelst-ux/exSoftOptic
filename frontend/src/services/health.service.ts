import type { HealthResponse, ReadinessResponse } from '../types/common';
import { apiRequest } from './http/httpClient';

export const healthService = {
  health: () => apiRequest<HealthResponse>('/health'),
  ready: () => apiRequest<ReadinessResponse>('/ready'),
};
