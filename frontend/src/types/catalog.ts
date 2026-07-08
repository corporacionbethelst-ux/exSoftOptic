import type { ID, MoneyValue } from './common';

export type Producto = {
  id: ID;
  sku: string;
  codigo_barras?: string | null;
  nombre: string;
  descripcion?: string | null;
  tipo_producto: string;
  precio_venta: MoneyValue;
  costo_estandar: MoneyValue;
  stock_minimo?: MoneyValue;
  requiere_receta?: boolean;
  es_servicio?: boolean;
};

export type ProductoListResponse = {
  items?: Producto[];
  productos?: Producto[];
  total?: number;
  page?: number;
  per_page?: number;
};
