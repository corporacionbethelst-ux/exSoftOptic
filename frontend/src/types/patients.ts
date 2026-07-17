import type { DateString, ID, MoneyValue } from './common';

export type Cliente = {
  id: ID;
  empresa_id: ID;
  nombre: string;
  email: string | null;
  telefono: string | null;
  rfc: string | null;
  codigo_postal: string | null;
  regimen_fiscal: string | null;
};

export type ClientePayload = {
  nombre: string;
  email?: string | null;
  telefono?: string | null;
  rfc?: string | null;
  codigo_postal?: string | null;
  regimen_fiscal?: string | null;
};

export type Paciente = {
  id: ID;
  empresa_id: ID;
  cliente_id: ID;
  nombre: string;
  fecha_nacimiento: DateString | null;
  telefono: string | null;
  email: string | null;
};

export type PacientePayload = {
  cliente_id: ID;
  nombre: string;
  fecha_nacimiento?: DateString | null;
  telefono?: string | null;
  email?: string | null;
};

export type RecetaOptica = {
  id: ID;
  empresa_id: ID;
  paciente_id: ID;
  fecha: DateString;
  od_esfera: MoneyValue | null;
  od_cilindro: MoneyValue | null;
  od_eje: MoneyValue | null;
  od_adicion: MoneyValue | null;
  oi_esfera: MoneyValue | null;
  oi_cilindro: MoneyValue | null;
  oi_eje: MoneyValue | null;
  oi_adicion: MoneyValue | null;
  dnp: MoneyValue | null;
  altura: MoneyValue | null;
  observaciones: string | null;
};

export type RecetaOpticaPayload = {
  paciente_id: ID;
  fecha: DateString;
  od_esfera?: MoneyValue | null;
  od_cilindro?: MoneyValue | null;
  od_eje?: MoneyValue | null;
  od_adicion?: MoneyValue | null;
  oi_esfera?: MoneyValue | null;
  oi_cilindro?: MoneyValue | null;
  oi_eje?: MoneyValue | null;
  oi_adicion?: MoneyValue | null;
  dnp?: MoneyValue | null;
  altura?: MoneyValue | null;
  observaciones?: string | null;
};
