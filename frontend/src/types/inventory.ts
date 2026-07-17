import type { DateTimeString, ID, MoneyValue } from './common';

export type KardexMovimiento = {
  id: ID;
  empresa_id?: ID;
  sucursal_id?: ID;
  producto_id?: ID;
  tipo_movimiento: string;
  origen: string;
  referencia?: string | null;
  cantidad: MoneyValue;
  costo_unitario?: MoneyValue;
  costo_total: MoneyValue;
  saldo_cantidad: MoneyValue;
  saldo_valor?: MoneyValue;
  created_at?: DateTimeString;
};


export type InventarioAlerta = {
  producto_id: ID;
  sucursal_id: ID;
  sku: string;
  nombre: string;
  tipo_alerta: string;
  severidad: string;
  cantidad_actual: MoneyValue;
  stock_minimo: MoneyValue;
  punto_reorden?: MoneyValue | null;
  valor_total: MoneyValue;
  mensaje: string;
};


export type InventarioEntradaPayload = {
  sucursal_id: ID;
  producto_id: ID;
  cantidad: number;
  costo_unitario: number;
  origen: string;
  referencia?: string | null;
  lote?: string | null;
  numero_serie?: string | null;
  fecha_caducidad?: string | null;
};

export type InventarioSalidaPayload = {
  sucursal_id: ID;
  producto_id: ID;
  cantidad: number;
  origen: string;
  referencia?: string | null;
};
