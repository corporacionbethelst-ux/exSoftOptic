import type { DateString, DateTimeString, ID, MoneyValue } from './common';

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

/** Datos clínicos para crear un paciente inline junto a la venta (backend: PacienteCreate). */
export type VentaPacienteInline = {
  nombre: string;
  fecha_nacimiento?: DateString | null;
  telefono?: string | null;
  email?: string | null;
};

/** Receta óptica capturada inline en la venta (backend: RecetaOpticaCreate sin paciente_id). */
export type VentaRecetaInline = {
  fecha: DateString;
  od_esfera?: number | null;
  od_cilindro?: number | null;
  od_eje?: number | null;
  od_adicion?: number | null;
  oi_esfera?: number | null;
  oi_cilindro?: number | null;
  oi_eje?: number | null;
  oi_adicion?: number | null;
  dnp?: number | null;
  altura?: number | null;
  observaciones?: string | null;
};

export type VentaPayload = {
  sucursal_id: ID;
  cliente_id?: ID | null;
  cliente?: {
    nombre: string;
    email?: string | null;
    telefono?: string | null;
    rfc?: string | null;
    codigo_postal?: string | null;
    regimen_fiscal?: string | null;
  };
  paciente_id?: ID | null;
  paciente?: VentaPacienteInline | null;
  receta_id?: ID | null;
  receta?: VentaRecetaInline | null;
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
