import type { ID, MoneyValue } from './common';

export type Producto = {
  id: ID;
  sku: string;
  codigo_barras?: string | null;
  nombre: string;
  descripcion?: string | null;
  tipo_producto: string;
  unidad_medida?: string;
  precio_venta: MoneyValue;
  costo_estandar: MoneyValue;
  stock_minimo?: MoneyValue;
  requiere_receta?: boolean;
  requiere_lote?: boolean;
  requiere_serie?: boolean;
  es_servicio?: boolean;
};

export type ProductoPayload = {
  sku: string;
  codigo_barras?: string | null;
  nombre: string;
  descripcion?: string | null;
  tipo_producto: string;
  unidad_medida: string;
  costo_estandar: number;
  precio_venta: number;
  stock_minimo: number;
  requiere_receta: boolean;
  requiere_lote: boolean;
  requiere_serie: boolean;
  es_servicio: boolean;
};

export type ProductoListResponse = {
  items?: Producto[];
  productos?: Producto[];
  total?: number;
  skip?: number;
  limit?: number;
  page?: number;
  per_page?: number;
};
