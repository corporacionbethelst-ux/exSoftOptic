import type { DateTimeString, ID, MoneyValue } from './common';

export type KardexMovimiento = {
  id: ID;
  tipo_movimiento: string;
  origen: string;
  referencia?: string | null;
  cantidad: MoneyValue;
  costo_total: MoneyValue;
  saldo_cantidad: MoneyValue;
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
