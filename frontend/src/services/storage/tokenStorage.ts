import type { LoginResponse } from '../../types/auth';

const TOKEN_STORAGE_KEY = 'exsoftoptic.tokens';

export function getStoredTokens(): LoginResponse | null {
  const raw = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as LoginResponse;
  } catch {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    return null;
  }
}

export function storeTokens(tokens: LoginResponse) {
  localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
}

export function clearStoredTokens() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}
