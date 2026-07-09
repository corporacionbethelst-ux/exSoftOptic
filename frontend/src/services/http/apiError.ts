import type { ApiErrorPayload } from '../../types/common';

export class ApiError extends Error {
  status: number;
  payload: ApiErrorPayload | null;

  constructor(status: number, payload: ApiErrorPayload | null, fallback: string) {
    super(payload?.error?.message ?? fallback);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }
}
