import type { DateTimeString, ID, MoneyValue } from './common';

export type OrdenLaboratorioEtapa = {
  id: ID;
  etapa: string;
  estado: string;
  responsable_id?: ID | null;
  fecha_inicio?: DateTimeString | null;
  fecha_fin?: DateTimeString | null;
  observaciones?: string | null;
};

export type ConsumoMaterialLaboratorio = {
  id: ID;
  producto_id: ID;
  kardex_movimiento_id?: ID | null;
  cantidad: MoneyValue;
  costo_total: MoneyValue;
  observaciones?: string | null;
};

export type ControlCalidadLaboratorio = {
  id: ID;
  resultado: 'APROBADO' | 'RECHAZADO' | 'RETRABAJO';
  motivo_rechazo?: string | null;
  observaciones?: string | null;
  usuario_id?: ID | null;
  fecha: DateTimeString;
};

export type OrdenLaboratorio = {
  id: ID;
  empresa_id: ID;
  sucursal_id: ID;
  venta_id: ID;
  paciente_id: ID;
  receta_id?: ID | null;
  folio: string;
  estado: string;
  prioridad: string;
  fecha_prometida?: DateTimeString | null;
  fecha_inicio?: DateTimeString | null;
  fecha_terminada?: DateTimeString | null;
  fecha_entrega?: DateTimeString | null;
  observaciones?: string | null;
  etapas?: OrdenLaboratorioEtapa[];
  consumos?: ConsumoMaterialLaboratorio[];
  controles_calidad?: ControlCalidadLaboratorio[];
};

export type OrdenLaboratorioFromVentaPayload = {
  folio: string;
  prioridad: string;
  fecha_prometida?: DateTimeString | null;
  observaciones?: string | null;
};

export type ConsumoMaterialPayload = {
  producto_id: ID;
  cantidad: number;
  observaciones?: string | null;
};

export type ControlCalidadPayload = {
  resultado: 'APROBADO' | 'RECHAZADO' | 'RETRABAJO';
  motivo_rechazo?: string | null;
  observaciones?: string | null;
};
