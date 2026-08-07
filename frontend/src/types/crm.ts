import type { DateTimeString, ID } from './common';

export type CitaEstado = 'PROGRAMADA' | 'CONFIRMADA' | 'EN_PROCESO' | 'COMPLETADA' | 'CANCELADA' | 'NO_ASISTIO';

export type CitaOptica = {
  id: ID;
  empresa_id: ID;
  sucursal_id: ID;
  cliente_id: ID;
  paciente_id?: ID | null;
  optometrista_id?: ID | null;
  folio: string;
  fecha_inicio: DateTimeString;
  fecha_fin: DateTimeString;
  tipo: string;
  motivo?: string | null;
  observaciones?: string | null;
  estado: CitaEstado;
  created_at: DateTimeString;
};

export type CitaOpticaPayload = {
  sucursal_id: ID;
  cliente_id: ID;
  paciente_id?: ID | null;
  optometrista_id?: ID | null;
  folio: string;
  fecha_inicio: DateTimeString;
  fecha_fin: DateTimeString;
  tipo: string;
  motivo?: string | null;
  observaciones?: string | null;
};

export type RecordatorioCliente = {
  id: ID;
  empresa_id: ID;
  cliente_id: ID;
  paciente_id?: ID | null;
  cita_id?: ID | null;
  tipo: string;
  canal: string;
  programado_para: DateTimeString;
  mensaje: string;
  estado: string;
  created_at: DateTimeString;
};

export type RecordatorioClientePayload = {
  cliente_id: ID;
  paciente_id?: ID | null;
  cita_id?: ID | null;
  tipo: string;
  canal: string;
  programado_para: DateTimeString;
  mensaje: string;
};
