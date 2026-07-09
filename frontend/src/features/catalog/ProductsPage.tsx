import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { catalogService } from '../../services';
import type { Producto, ProductoPayload } from '../../types/catalog';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

const DEFAULT_FORM: ProductoPayload = {
  sku: '',
  codigo_barras: '',
  nombre: '',
  descripcion: '',
  tipo_producto: 'ARMAZON',
  unidad_medida: 'PIEZA',
  costo_estandar: 0,
  precio_venta: 0,
  stock_minimo: 0,
  requiere_receta: false,
  requiere_lote: false,
  requiere_serie: false,
  es_servicio: false,
};

function productToForm(product: Producto): ProductoPayload {
  return {
    sku: product.sku,
    codigo_barras: product.codigo_barras ?? '',
    nombre: product.nombre,
    descripcion: product.descripcion ?? '',
    tipo_producto: product.tipo_producto,
    unidad_medida: product.unidad_medida ?? 'PIEZA',
    costo_estandar: Number(product.costo_estandar ?? 0),
    precio_venta: Number(product.precio_venta ?? 0),
    stock_minimo: Number(product.stock_minimo ?? 0),
    requiere_receta: Boolean(product.requiere_receta),
    requiere_lote: Boolean(product.requiere_lote),
    requiere_serie: Boolean(product.requiere_serie),
    es_servicio: Boolean(product.es_servicio),
  };
}

export function ProductsPage() {
  const [search, setSearch] = useState('');
  const [editingProduct, setEditingProduct] = useState<Producto | null>(null);
  const [form, setForm] = useState<ProductoPayload>(DEFAULT_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const loadProducts = useCallback(() => catalogService.products({ search }), [search]);
  const products = useApiResource(loadProducts);
  const items = products.data?.items ?? products.data?.productos ?? [];
  const isEditing = Boolean(editingProduct);

  const totalLabel = useMemo(() => `${products.data?.total ?? items.length} productos`, [items.length, products.data?.total]);

  function openCreate() {
    setEditingProduct(null);
    setForm(DEFAULT_FORM);
    setFormError(null);
  }

  function openEdit(product: Producto) {
    setEditingProduct(product);
    setForm(productToForm(product));
    setFormError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      if (editingProduct) {
        await catalogService.updateProduct(editingProduct.id, form);
      } else {
        await catalogService.createProduct(form);
      }
      setEditingProduct(null);
      setForm(DEFAULT_FORM);
      await products.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo guardar el producto');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(product: Producto) {
    if (!window.confirm(`¿Eliminar ${product.nombre}?`)) return;
    await catalogService.deleteProduct(product.id);
    await products.reload();
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Catálogo"
        title="Productos"
        description="CRUD base de productos para compras, ventas e inventario."
        actions={<button className="primary-button" onClick={openCreate}>Nuevo producto</button>}
      />

      <SectionPanel title="Gestión de catálogo" footer={<span className="muted compact">{totalLabel}</span>}>
        <div className="toolbar-row">
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por nombre o SKU" />
          <button className="secondary-button" onClick={() => void products.reload()}>Buscar</button>
        </div>
        <InlineState loading={products.loading} error={products.error} empty={items.length === 0} emptyTitle="Sin productos" emptyDescription="Crea el primer producto o ejecuta make seed-demo.">
          <div className="table-wrap">
            <table>
              <thead><tr><th>SKU</th><th>Nombre</th><th>Tipo</th><th>Precio</th><th>Receta</th><th>Acciones</th></tr></thead>
              <tbody>
                {items.map((product) => (
                  <tr key={product.id}>
                    <td>{product.sku}</td>
                    <td>{product.nombre}</td>
                    <td><StatusBadge>{product.tipo_producto}</StatusBadge></td>
                    <td>{money(product.precio_venta)}</td>
                    <td>{product.requiere_receta ? 'Sí' : 'No'}</td>
                    <td className="action-cell">
                      <button className="secondary-button" onClick={() => openEdit(product)}>Editar</button>
                      <button className="danger-button" onClick={() => void handleDelete(product)}>Eliminar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </InlineState>
      </SectionPanel>

      <SectionPanel title={isEditing ? 'Editar producto' : 'Nuevo producto'} description="Campos mínimos para operar catálogo, venta e inventario.">
        <form className="crud-form" onSubmit={(event) => void handleSubmit(event)}>
          <label>SKU<input value={form.sku} onChange={(event) => setForm({ ...form, sku: event.target.value })} required /></label>
          <label>Nombre<input value={form.nombre} onChange={(event) => setForm({ ...form, nombre: event.target.value })} required /></label>
          <label>Tipo
            <select value={form.tipo_producto} onChange={(event) => setForm({ ...form, tipo_producto: event.target.value, es_servicio: event.target.value === 'SERVICIO' })}>
              <option value="ARMAZON">Armazón</option>
              <option value="LENTE">Lente</option>
              <option value="SERVICIO">Servicio</option>
              <option value="ACCESORIO">Accesorio</option>
            </select>
          </label>
          <label>Unidad<input value={form.unidad_medida} onChange={(event) => setForm({ ...form, unidad_medida: event.target.value })} /></label>
          <label>Costo<input type="number" min="0" step="0.01" value={form.costo_estandar} onChange={(event) => setForm({ ...form, costo_estandar: Number(event.target.value) })} /></label>
          <label>Precio venta<input type="number" min="0" step="0.01" value={form.precio_venta} onChange={(event) => setForm({ ...form, precio_venta: Number(event.target.value) })} /></label>
          <label>Stock mínimo<input type="number" min="0" step="1" value={form.stock_minimo} onChange={(event) => setForm({ ...form, stock_minimo: Number(event.target.value) })} /></label>
          <label className="wide-field">Descripción<input value={form.descripcion ?? ''} onChange={(event) => setForm({ ...form, descripcion: event.target.value })} /></label>
          <label className="check-field"><input type="checkbox" checked={form.requiere_receta} onChange={(event) => setForm({ ...form, requiere_receta: event.target.checked })} /> Requiere receta</label>
          <label className="check-field"><input type="checkbox" checked={form.requiere_lote} onChange={(event) => setForm({ ...form, requiere_lote: event.target.checked })} /> Control por lote</label>
          {formError ? <div className="alert error wide-field">{formError}</div> : null}
          <div className="form-actions wide-field">
            <button className="primary-button" disabled={saving}>{saving ? 'Guardando…' : isEditing ? 'Actualizar' : 'Crear producto'}</button>
            <button className="secondary-button" type="button" onClick={openCreate}>Limpiar</button>
          </div>
        </form>
      </SectionPanel>
    </section>
  );
}
