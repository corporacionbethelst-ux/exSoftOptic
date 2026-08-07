import type { DateString, DateTimeString, ID, MoneyValue } from './common';

export type CuentaContable = { id: ID; empresa_id: ID; codigo: string; nombre: string; tipo: string; naturaleza: 'DEUDORA' | 'ACREEDORA'; padre_id?: ID | null; acepta_movimientos: boolean };
export type CuentaContablePayload = Omit<CuentaContable, 'id' | 'empresa_id'>;
export type LineaAsiento = { id: ID; cuenta_id: ID; descripcion?: string | null; debe: MoneyValue; haber: MoneyValue };
export type AsientoContable = { id: ID; empresa_id: ID; fecha: DateString; descripcion: string; origen: string; referencia?: string | null; moneda: string; estado: string; lineas?: LineaAsiento[] };
export type PeriodoContable = { id: ID; empresa_id: ID; codigo: string; nombre: string; fecha_inicio: DateString; fecha_fin: DateString; estado: string; created_at: DateTimeString };
export type PeriodoContablePayload = { codigo: string; nombre: string; fecha_inicio: DateString; fecha_fin: DateString };
export type CuentaBancaria = { id: ID; empresa_id: ID; cuenta_contable_id: ID; banco: string; numero_cuenta: string; moneda: string; estado: string };
export type CuentaBancariaPayload = { cuenta_contable_id: ID; banco: string; numero_cuenta: string; moneda: string };
export type MovimientoBancario = { id: ID; empresa_id: ID; cuenta_bancaria_id: ID; fecha: DateString; referencia: string; descripcion?: string | null; monto: MoneyValue; tipo: 'CARGO' | 'ABONO'; asiento_id?: ID | null; estado: string; conciliado_en?: DateTimeString | null };
export type MovimientoBancarioPayload = { cuenta_bancaria_id: ID; fecha: DateString; referencia: string; descripcion?: string | null; monto: number; tipo: 'CARGO' | 'ABONO' };
export type ConciliacionPayload = { movimiento_id: ID; asiento_id: ID; observaciones?: string | null };
export type CentroCosto = { id: ID; empresa_id: ID; codigo: string; nombre: string; descripcion?: string | null; estado: string };
export type CentroCostoPayload = { codigo: string; nombre: string; descripcion?: string | null };
export type PresupuestoPayload = { centro_costo_id: ID; folio: string; nombre: string; fecha_inicio: DateString; fecha_fin: DateString; observaciones?: string | null; lineas: Array<{ cuenta_codigo: string; monto: number }> };
export type Presupuesto = { id: ID; empresa_id: ID; centro_costo_id: ID; folio: string; nombre: string; fecha_inicio: DateString; fecha_fin: DateString; estado: string; observaciones?: string | null; lineas?: Array<{ id: ID; cuenta_codigo: string; monto: MoneyValue; monto_comprometido: MoneyValue; monto_ejercido: MoneyValue }> };
export type ComprometerPresupuestoPayload = { presupuesto_id: ID; cuenta_codigo: string; monto: number };
