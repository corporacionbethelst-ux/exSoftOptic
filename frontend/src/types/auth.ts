import type { DateTimeString, ID } from './common';

export type LoginRequest = {
  username: string;
  password: string;
};

export type Usuario = {
  id: ID;
  username: string;
  email: string;
  nombre_completo: string;
  telefono?: string | null;
  rol_id: ID;
  sucursal_id?: ID | null;
  empresa_id: ID;
  esta_activo: boolean;
  email_verificado: boolean;
  ultimo_acceso?: DateTimeString | null;
  created_at: DateTimeString;
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
