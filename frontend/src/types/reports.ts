import type { ID, MoneyValue } from './common';

export type BalanzaCuenta = { cuenta_id: ID; codigo: string; nombre: string; tipo: string; naturaleza: string; debe: MoneyValue; haber: MoneyValue; saldo: MoneyValue };
export type BalanzaComprobacion = { empresa_id: ID; total_debe: MoneyValue; total_haber: MoneyValue; cuentas: BalanzaCuenta[] };
export type InventarioValuadoItem = { producto_id: ID; sucursal_id: ID; sku: string; producto: string; cantidad: MoneyValue; costo_promedio: MoneyValue; valor_total: MoneyValue };
export type InventarioValuado = { empresa_id: ID; total_valor: MoneyValue; items: InventarioValuadoItem[] };
export type MargenVentasItem = { venta_id: ID; folio: string; total: MoneyValue; costo_total: MoneyValue; margen: MoneyValue; margen_porcentaje: MoneyValue };
export type MargenVentas = { empresa_id: ID; total_ventas: MoneyValue; total_costo: MoneyValue; margen_total: MoneyValue; margen_porcentaje: MoneyValue; ventas: MargenVentasItem[] };
export type LibroDiarioLinea = { asiento_id: ID; fecha: string; origen: string; referencia?: string | null; cuenta_codigo: string; cuenta_nombre: string; descripcion?: string | null; debe: MoneyValue; haber: MoneyValue };
export type LibroDiario = { empresa_id: ID; total_debe: MoneyValue; total_haber: MoneyValue; lineas: LibroDiarioLinea[] };
export type EstadoResultados = { empresa_id: ID; ingresos: MoneyValue; costos: MoneyValue; gastos: MoneyValue; utilidad_bruta: MoneyValue; utilidad_operativa: MoneyValue; cuentas: Array<{ cuenta_id: ID; codigo: string; nombre: string; tipo: string; saldo: MoneyValue }> };
export type BalanceGeneral = { empresa_id: ID; activos: MoneyValue; pasivos: MoneyValue; capital: MoneyValue; comprobacion: MoneyValue; cuentas: Array<{ cuenta_id: ID; codigo: string; nombre: string; tipo: string; saldo: MoneyValue }> };
export type AuditoriaEvento = { id: ID; empresa_id: ID; usuario_id?: ID | null; accion: string; entidad?: string | null; entidad_id?: ID | null; payload?: unknown; created_at: string; hash_actual?: string | null; hash_anterior?: string | null };
export type AuditoriaVerificacion = { valid: boolean; total_events: number; first_invalid_sequence?: number | null; reason?: string | null; last_hash?: string | null };
export type RuntimeMetrics = Record<string, unknown>;
