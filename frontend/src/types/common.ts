export type ID = string;
export type MoneyValue = string | number;
export type DateTimeString = string;
export type DateString = string;

export type ApiErrorPayload = {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
    correlation_id?: string | null;
  };
  detail?: unknown;
};

export type HealthResponse = {
  status: string;
  service?: string;
  version?: string;
};

export type ReadinessResponse = {
  status: string;
  database?: string;
};
