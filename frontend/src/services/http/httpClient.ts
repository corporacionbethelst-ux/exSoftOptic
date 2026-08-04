import { env } from '../../config/env';
import type { RefreshTokenResponse } from '../../types/auth';
import type { ApiErrorPayload } from '../../types/common';
import { clearStoredTokens, getStoredTokens, storeTokens } from '../storage/tokenStorage';
import { ApiError } from './apiError';

type ApiRequestOptions = RequestInit & { skipAuthRefresh?: boolean };

let refreshPromise: Promise<boolean> | null = null;

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

async function refreshAccessToken(): Promise<boolean> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const session = getStoredTokens();
    if (!session?.refresh_token) return false;

    const response = await fetch(`${env.apiBaseUrl}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: session.refresh_token }),
    });
    if (!response.ok) return false;

    const tokens = await parseJson<RefreshTokenResponse>(response);
    storeTokens({ ...session, ...tokens, user: session.user });
    globalThis.dispatchEvent(new Event('exsoftoptic:auth-refreshed'));
    return true;
  })()
    .catch(() => false)
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { skipAuthRefresh = false, ...requestOptions } = options;
  const tokens = getStoredTokens();
  const headers = new Headers(requestOptions.headers);
  if (!headers.has('Content-Type') && requestOptions.body) {
    headers.set('Content-Type', 'application/json');
  }
  if (tokens?.access_token) {
    headers.set('Authorization', `Bearer ${tokens.access_token}`);
  }

  const response = await fetch(`${env.apiBaseUrl}${path}`, { ...requestOptions, headers });
  if (response.status === 401 && !skipAuthRefresh && tokens?.refresh_token) {
    if (await refreshAccessToken()) {
      return apiRequest<T>(path, { ...requestOptions, skipAuthRefresh: true });
    }
    clearStoredTokens();
    globalThis.dispatchEvent(new Event('exsoftoptic:auth-expired'));
  }
  if (!response.ok) {
    const payload = await parseJson<ApiErrorPayload>(response).catch(() => null);
    throw new ApiError(response.status, payload, `HTTP ${response.status}`);
  }
  return parseJson<T>(response);
}
