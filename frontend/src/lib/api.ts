const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';
const TOKEN_STORAGE_KEY = 'exsoftoptic.tokens';

export type LoginRequest = {
  username: string;
  password: string;
};

export type Usuario = {
  id: string;
  username: string;
  email: string;
  nombre_completo: string;
  telefono?: string | null;
  rol_id: string;
  sucursal_id?: string | null;
  empresa_id: string;
  esta_activo: boolean;
  email_verificado: boolean;
  ultimo_acceso?: string | null;
  created_at: string;
};

export type LoginResponse = {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: Usuario;
};

export type PaginatedUsers = {
  total: number;
  page: number;
  per_page: number;
  users: Usuario[];
};

export type Producto = {
  id: string;
  sku: string;
  codigo_barras?: string | null;
  nombre: string;
  descripcion?: string | null;
  tipo_producto: string;
  precio_venta: string | number;
  costo_estandar: string | number;
  stock_minimo?: string | number;
  requiere_receta?: boolean;
  es_servicio?: boolean;
};

export type ProductoListResponse = {
  items?: Producto[];
  productos?: Producto[];
  total?: number;
  page?: number;
  per_page?: number;
};

export type Venta = {
  id: string;
  folio: string;
  estado: string;
  subtotal: string | number;
  impuestos: string | number;
  total: string | number;
  created_at?: string;
  fecha?: string;
  lineas?: Array<{ id: string; descripcion: string; cantidad: string | number; importe: string | number }>;
};

export type OrdenLaboratorio = {
  id: string;
  folio: string;
  estado: string;
  prioridad: string;
  fecha_prometida?: string | null;
  observaciones?: string | null;
  etapas?: Array<{ id: string; etapa: string; estado: string }>;
};

export type KardexMovimiento = {
  id: string;
  tipo_movimiento: string;
  origen: string;
  referencia?: string | null;
  cantidad: string | number;
  costo_total: string | number;
  saldo_cantidad: string | number;
  created_at?: string;
};

export type ApiErrorPayload = {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
    correlation_id?: string | null;
  };
  detail?: unknown;
};

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

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const payload = await parseJson<ApiErrorPayload>(response).catch(() => null);
    throw new ApiError(response.status, payload, `HTTP ${response.status}`);
  }
  return parseJson<T>(response);
}

export const api = {
  health: () => apiRequest<{ status: string; service?: string; version?: string }>('/health'),
  ready: () => apiRequest<{ status: string; database?: string }>('/ready'),
  login: (payload: LoginRequest) =>
    apiRequest<LoginResponse>('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  me: () => apiRequest<Usuario>('/api/v1/auth/me'),
  users: () => apiRequest<PaginatedUsers>('/api/v1/usuarios/?page=1&per_page=20'),
  products: () => apiRequest<ProductoListResponse>('/api/v1/productos/?page=1&per_page=20'),
  sales: () => apiRequest<Venta[]>('/api/v1/ventas/?skip=0&limit=20'),
  labOrders: () => apiRequest<OrdenLaboratorio[]>('/api/v1/laboratorio/ordenes'),
  kardex: () => apiRequest<KardexMovimiento[]>('/api/v1/inventario/kardex'),
};
