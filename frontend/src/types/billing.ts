import type { DateString, DateTimeString, ID, MoneyValue } from './common';

export type FacturaLinea = { id: ID; producto_id: ID; descripcion: string; cantidad: MoneyValue; precio_unitario: MoneyValue; descuento: MoneyValue; importe: MoneyValue };
export type FacturaEvento = { id: ID; tipo_evento: string; descripcion: string; fecha: DateTimeString };
export type Factura = { id: ID; empresa_id: ID; sucursal_id: ID; venta_id: ID; cliente_id: ID; folio: string; estado: string; moneda: string; subtotal: MoneyValue; impuestos: MoneyValue; total: MoneyValue; proveedor: string; uuid_fiscal?: string | null; xml_url?: string | null; pdf_url?: string | null; error?: string | null; fecha_timbrado?: DateTimeString | null; lineas?: FacturaLinea[]; eventos?: FacturaEvento[] };
export type FacturaEmitirPayload = { venta_id: ID; folio: string; proveedor: string; moneda: string };
export type FacturaCancelarPayload = { motivo: string };

export type ReclamacionGarantia = { id: ID; garantia_id: ID; folio: string; motivo: string; estado: string; resolucion?: string | null; fecha_cierre?: DateTimeString | null };
export type EventoGarantia = { id: ID; tipo_evento: string; descripcion: string; fecha: DateTimeString };
export type Garantia = { id: ID; empresa_id: ID; sucursal_id: ID; venta_id: ID; orden_laboratorio_id?: ID | null; paciente_id?: ID | null; folio: string; tipo: 'ARMAZON' | 'LENTE' | 'TRATAMIENTO' | 'SERVICIO'; estado: string; fecha_inicio: DateString; fecha_fin: DateString; descripcion?: string | null; condiciones?: string | null; reclamaciones?: ReclamacionGarantia[]; eventos?: EventoGarantia[] };
export type GarantiaPayload = { venta_id: ID; orden_laboratorio_id?: ID | null; folio: string; tipo: Garantia['tipo']; fecha_inicio: DateString; fecha_fin: DateString; descripcion?: string | null; condiciones?: string | null };
export type GarantiaFromOrdenPayload = Omit<GarantiaPayload, 'venta_id' | 'orden_laboratorio_id'>;
export type ReclamacionGarantiaPayload = { folio: string; motivo: string };
export type ResolverReclamacionPayload = { estado: 'APROBADA' | 'RECHAZADA' | 'CERRADA'; resolucion: string };
