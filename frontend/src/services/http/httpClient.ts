import { env } from '../../config/env';
import type { ApiErrorPayload } from '../../types/common';
import { getStoredTokens } from '../storage/tokenStorage';
import { ApiError } from './apiError';

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const tokens = getStoredTokens();
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }
  if (tokens?.access_token) {
    headers.set('Authorization', `Bearer ${tokens.access_token}`);
  }

  const response = await fetch(`${env.apiBaseUrl}${path}`, { ...options, headers });
  if (!response.ok) {
    const payload = await parseJson<ApiErrorPayload>(response).catch(() => null);
    throw new ApiError(response.status, payload, `HTTP ${response.status}`);
  }
  return parseJson<T>(response);
}
