import type { DateTimeString, ID, MoneyValue } from './common';

export type VentaLinea = {
  id: ID;
  descripcion: string;
  cantidad: MoneyValue;
  importe: MoneyValue;
};

export type Venta = {
  id: ID;
  folio: string;
  estado: string;
  subtotal: MoneyValue;
  impuestos: MoneyValue;
  total: MoneyValue;
  created_at?: DateTimeString;
  fecha?: DateTimeString;
  lineas?: VentaLinea[];
};
