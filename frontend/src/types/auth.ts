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

export type UsuarioPayload = {
  username: string;
  email: string;
  nombre_completo: string;
  telefono?: string | null;
  password: string;
  rol_id: ID;
  sucursal_id?: ID | null;
};

export type UsuarioUpdatePayload = Partial<Omit<UsuarioPayload, 'username' | 'password'>> & {
  esta_activo?: boolean;
};

export type Rol = {
  id: ID;
  nombre: string;
  descripcion?: string | null;
  nivel_acceso: number;
  es_sistema: boolean;
  permisos: string[];
  esta_activo: boolean;
  created_at: DateTimeString;
};

export type RolPayload = {
  nombre: string;
  descripcion?: string | null;
  nivel_acceso: number;
  permisos: string[];
};

export type LoginResponse = {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: Usuario;
};

export type RefreshTokenResponse = Omit<LoginResponse, 'user'>;

export type PaginatedUsers = {
  total: number;
  page: number;
  per_page: number;
  users: Usuario[];
};
