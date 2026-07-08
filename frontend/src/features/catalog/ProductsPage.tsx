import { DataState } from '../../components/DataState';
import { StatusBadge } from '../../components/StatusBadge';
import { api } from '../../lib/api';
import { money } from '../../lib/format';
import { useApiResource } from '../../lib/useApiResource';

export function ProductsPage() {
  const products = useApiResource(api.products);
  const items = products.data?.items ?? products.data?.productos ?? [];
  return (
    <section className="page-stack">
      <div className="page-header"><div><p className="eyebrow">Catálogo</p><h1>Productos</h1><p className="muted">Productos demo para compras, ventas e inventario.</p></div></div>
      <DataState loading={products.loading} error={products.error}>
        <div className="card-grid">{items.map((product) => <article className="product-card" key={product.id}><StatusBadge>{product.tipo_producto}</StatusBadge><h2>{product.nombre}</h2><p>{product.descripcion ?? 'Sin descripción'}</p><div className="split"><span>{product.sku}</span><strong>{money(product.precio_venta)}</strong></div></article>)}</div>
      </DataState>
    </section>
  );
}
