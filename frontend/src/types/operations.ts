import type { DateTimeString, ID } from './common';

export type RuntimeMetrics = Record<string, unknown>;
export type ReadinessStatus = { status: string; database: string };
export type MaintenanceCleanupResult = { deleted: number; limit: number };
export type DispatchResult = { processed?: number; published?: number; failed?: number; errors?: unknown[]; [key: string]: unknown };

export type OutboxEvent = {
  id: ID;
  empresa_id: ID;
  aggregate_type: string;
  aggregate_id: string;
  event_type: string;
  payload: Record<string, unknown>;
  headers: Record<string, unknown>;
  status: string;
  attempts: number;
  max_attempts: number;
  idempotency_key: string;
  available_at: DateTimeString;
  locked_at?: DateTimeString | null;
  published_at?: DateTimeString | null;
  last_error?: string | null;
  created_at: DateTimeString;
  updated_at: DateTimeString;
};

export type OutboxEventPayload = {
  aggregate_type: string;
  aggregate_id: string;
  event_type: string;
  payload: Record<string, unknown>;
  headers: Record<string, unknown>;
  idempotency_key?: string | null;
  available_at?: DateTimeString | null;
  max_attempts: number;
};

export type OutboxFailurePayload = { error: string; retry_delay_seconds: number };
