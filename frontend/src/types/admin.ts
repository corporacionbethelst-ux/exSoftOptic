import type { DateString, DateTimeString, ID, MoneyValue } from './common';

export type Impuesto = { id: ID; empresa_id: ID; codigo: string; nombre: string; tipo: string; tasa: MoneyValue; cuenta_contable_codigo?: string | null; es_retencion: boolean; created_at: DateTimeString };
export type ImpuestoPayload = Omit<Impuesto, 'id' | 'empresa_id' | 'created_at'>;
export type SerieFolio = { id: ID; empresa_id: ID; sucursal_id?: ID | null; documento: string; serie: string; folio_actual: MoneyValue; formato: string; created_at: DateTimeString };
export type SerieFolioPayload = Omit<SerieFolio, 'id' | 'empresa_id' | 'created_at'>;
export type TipoCambio = { id: ID; empresa_id: ID; moneda_origen: string; moneda_destino: string; fecha: DateString; tasa: MoneyValue; fuente?: string | null; created_at: DateTimeString };
export type TipoCambioPayload = Omit<TipoCambio, 'id' | 'empresa_id' | 'created_at'>;
export type ReglaContable = { id: ID; empresa_id: ID; evento: string; descripcion: string; cuentas: Record<string, unknown>; condiciones: Record<string, unknown>; created_at: DateTimeString };
export type ReglaContablePayload = Omit<ReglaContable, 'id' | 'empresa_id' | 'created_at'>;
export type Empleado = { id: ID; empresa_id: ID; sucursal_id?: ID | null; numero_empleado: string; nombre: string; email?: string | null; rfc?: string | null; curp?: string | null; nss?: string | null; fecha_ingreso: DateString; salario_diario: MoneyValue; estado: string };
export type EmpleadoPayload = Omit<Empleado, 'id' | 'empresa_id' | 'estado'>;
export type NominaRecibo = { id: ID; empleado_id: ID; dias_pagados: MoneyValue; percepciones: MoneyValue; deducciones: MoneyValue; neto: MoneyValue; estado: string };
export type NominaPeriodo = { id: ID; empresa_id: ID; folio: string; fecha_inicio: DateString; fecha_fin: DateString; estado: string; total_percepciones: MoneyValue; total_deducciones: MoneyValue; total_neto: MoneyValue; asiento_id?: ID | null; observaciones?: string | null; recibos?: NominaRecibo[] };
export type NominaPeriodoPayload = { folio: string; fecha_inicio: DateString; fecha_fin: DateString; observaciones?: string | null };
export type NominaConfirmarPayload = { cuenta_gasto_sueldos: string; cuenta_bancos: string; cuenta_retenciones: string };
