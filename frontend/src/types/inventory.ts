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
