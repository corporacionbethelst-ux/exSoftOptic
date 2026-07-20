import type { DateTimeString, ID, MoneyValue } from './common';

export type VentaLinea = {
  id: ID;
  producto_id: ID;
  descripcion: string;
  cantidad: MoneyValue;
  precio_unitario: MoneyValue;
  descuento: MoneyValue;
  importe: MoneyValue;
};

export type VentaPago = {
  id: ID;
  metodo_pago: string;
  monto: MoneyValue;
  referencia?: string | null;
  fecha: DateTimeString;
};

export type Venta = {
  id: ID;
  empresa_id?: ID;
  sucursal_id: ID;
  cliente_id: ID;
  paciente_id?: ID | null;
  receta_id?: ID | null;
  folio: string;
  estado: string;
  subtotal: MoneyValue;
  impuestos: MoneyValue;
  total: MoneyValue;
  costo_total?: MoneyValue;
  created_at?: DateTimeString;
  fecha?: DateTimeString;
  lineas?: VentaLinea[];
  pagos?: VentaPago[];
};

export type VentaLineaPayload = {
  producto_id: ID;
  descripcion?: string | null;
  cantidad: number;
  precio_unitario: number;
  descuento: number;
};

export type VentaPayload = {
  sucursal_id: ID;
  cliente?: {
    nombre: string;
    email?: string | null;
    telefono?: string | null;
    rfc?: string | null;
    codigo_postal?: string | null;
    regimen_fiscal?: string | null;
  };
  folio: string;
  impuestos: number;
  lineas: VentaLineaPayload[];
  pagos: Array<{
    metodo_pago: string;
    monto: number;
    referencia?: string | null;
  }>;
};

export type VentaConfirmarPayload = {
  cuenta_cobro: string;
  cuenta_ingresos: string;
  cuenta_costo_ventas: string;
  cuenta_inventario: string;
};

export type DevolucionVentaPayload = {
  folio: string;
  motivo: string;
  lineas: Array<{
    venta_linea_id: ID;
    cantidad: number;
  }>;
  cuenta_cobro: string;
  cuenta_ingresos: string;
  cuenta_costo_ventas: string;
  cuenta_inventario: string;
};
