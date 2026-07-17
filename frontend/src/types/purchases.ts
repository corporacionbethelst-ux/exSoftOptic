import type { DateTimeString, ID, MoneyValue } from './common';

export type ProveedorPayload = {
  nombre: string;
  rfc?: string | null;
  email?: string | null;
  telefono?: string | null;
};

export type OrdenCompraLinea = {
  id: ID;
  producto_id: ID;
  descripcion: string;
  cantidad: MoneyValue;
  cantidad_recibida: MoneyValue;
  costo_unitario: MoneyValue;
  importe: MoneyValue;
};

export type OrdenCompra = {
  id: ID;
  empresa_id: ID;
  sucursal_id: ID;
  proveedor_id: ID;
  folio: string;
  fecha: DateTimeString;
  estado: string;
  subtotal: MoneyValue;
  impuestos: MoneyValue;
  total: MoneyValue;
  lineas: OrdenCompraLinea[];
};

export type OrdenCompraLineaPayload = {
  producto_id: ID;
  descripcion?: string | null;
  cantidad: number;
  costo_unitario: number;
};

export type OrdenCompraPayload = {
  sucursal_id: ID;
  proveedor?: ProveedorPayload;
  proveedor_id?: ID | null;
  folio: string;
  impuestos: number;
  lineas: OrdenCompraLineaPayload[];
};

export type RecepcionCompraLineaPayload = {
  orden_linea_id: ID;
  cantidad: number;
  lote?: string | null;
  numero_serie?: string | null;
};

export type RecepcionCompraPayload = {
  folio: string;
  lineas: RecepcionCompraLineaPayload[];
  cuenta_inventario: string;
  cuenta_cxp: string;
};

export type RecepcionCompraLinea = {
  id: ID;
  orden_linea_id: ID;
  producto_id: ID;
  cantidad: MoneyValue;
  costo_unitario: MoneyValue;
  importe: MoneyValue;
  lote?: string | null;
  numero_serie?: string | null;
};

export type RecepcionCompra = {
  id: ID;
  empresa_id: ID;
  sucursal_id: ID;
  orden_id: ID;
  asiento_id?: ID | null;
  folio: string;
  fecha: DateTimeString;
  estado: string;
  total: MoneyValue;
  lineas: RecepcionCompraLinea[];
};

export type SolicitudCompraPayload = {
  sucursal_id: ID;
  folio: string;
  observaciones?: string | null;
};

export type SolicitudCompra = {
  id: ID;
  empresa_id: ID;
  sucursal_id: ID;
  folio: string;
  origen: string;
  estado: string;
  observaciones?: string | null;
  lineas: Array<{
    id: ID;
    producto_id: ID;
    cantidad_sugerida: MoneyValue;
    costo_estimado: MoneyValue;
    motivo: string;
  }>;
};
