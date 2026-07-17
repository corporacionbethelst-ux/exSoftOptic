import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { catalogService, inventoryService } from '../../services';
import type { Producto } from '../../types/catalog';
import type { InventarioEntradaPayload, InventarioSalidaPayload } from '../../types/inventory';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';
import { useAuth } from '../auth/authContext';

function movementTone(type: string): 'success' | 'warning' | 'danger' | 'neutral' {
  if (type === 'ENTRADA') return 'success';
  if (type === 'SALIDA') return 'danger';
  return 'neutral';
}

function currentProduct(products: Producto[], productId: string) {
  return products.find((product) => product.id === productId);
}

export function InventoryPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [sucursalId, setSucursalId] = useState(user?.sucursal_id ?? '');
  const [entryProductId, setEntryProductId] = useState('');
  const [entryQty, setEntryQty] = useState(1);
  const [entryCost, setEntryCost] = useState(0);
  const [entryReference, setEntryReference] = useState(() => `AJ-ENT-${Date.now()}`);
  const [entryBatch, setEntryBatch] = useState('');
  const [exitProductId, setExitProductId] = useState('');
  const [exitQty, setExitQty] = useState(1);
  const [exitReference, setExitReference] = useState(() => `AJ-SAL-${Date.now()}`);
  const [operationMessage, setOperationMessage] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [savingEntry, setSavingEntry] = useState(false);
  const [savingExit, setSavingExit] = useState(false);
  const skip = (page - 1) * pageSize;

  const loadKardex = useCallback(() => inventoryService.kardex({ producto_id: selectedProductId || undefined, skip, limit: pageSize }), [pageSize, selectedProductId, skip]);
  const loadProducts = useCallback(() => catalogService.products({ limit: 150 }), []);
  const loadAlerts = useCallback(() => inventoryService.stockAlerts({ sucursal_id: sucursalId || undefined, limit: 50 }), [sucursalId]);
  const kardex = useApiResource(loadKardex);
  const products = useApiResource(loadProducts);
  const alerts = useApiResource(loadAlerts, Boolean(sucursalId));
  const movements = useMemo(() => kardex.data ?? [], [kardex.data]);
  const productItems = useMemo(() => products.data?.items ?? products.data?.productos ?? [], [products.data]);
  const totalEntradas = useMemo(() => movements.filter((item) => item.tipo_movimiento === 'ENTRADA').reduce((total, item) => total + Number(item.cantidad), 0), [movements]);
  const totalSalidas = useMemo(() => movements.filter((item) => item.tipo_movimiento === 'SALIDA').reduce((total, item) => total + Number(item.cantidad), 0), [movements]);
  const lastBalance = movements[0]?.saldo_cantidad ?? 0;

  function selectEntryProduct(productId: string) {
    setEntryProductId(productId);
    setEntryCost(Number(currentProduct(productItems, productId)?.costo_estandar ?? 0));
  }

  async function submitEntry(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingEntry(true);
    setFormError(null);
    setOperationMessage(null);
    try {
      const payload: InventarioEntradaPayload = {
        sucursal_id: sucursalId,
        producto_id: entryProductId,
        cantidad: entryQty,
        costo_unitario: entryCost,
        origen: 'AJUSTE_MANUAL',
        referencia: entryReference || null,
        lote: entryBatch || null,
      };
      await inventoryService.entrada(payload);
      setOperationMessage('Entrada registrada correctamente en kardex e inventario.');
      setEntryReference(`AJ-ENT-${Date.now()}`);
      setEntryBatch('');
      await kardex.reload();
      await alerts.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo registrar la entrada');
    } finally {
      setSavingEntry(false);
    }
  }

  async function submitExit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingExit(true);
    setFormError(null);
    setOperationMessage(null);
    try {
      const payload: InventarioSalidaPayload = {
        sucursal_id: sucursalId,
        producto_id: exitProductId,
        cantidad: exitQty,
        origen: 'AJUSTE_MANUAL',
        referencia: exitReference || null,
      };
      await inventoryService.salida(payload);
      setOperationMessage('Salida PEPS registrada correctamente en kardex e inventario.');
      setExitReference(`AJ-SAL-${Date.now()}`);
      await kardex.reload();
      await alerts.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo registrar la salida');
    } finally {
      setSavingExit(false);
    }
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Inventario"
        title="Kardex y ajustes"
        description="Fase de inventario: consulta de kardex, alertas de stock mínimo, entradas manuales y salidas PEPS controladas."
      />

      <div className="metric-grid">
        <article className="metric-card"><span>Movimientos página</span><strong>{movements.length}</strong><small>Kardex filtrado</small></article>
        <article className="metric-card"><span>Entradas página</span><strong>{totalEntradas}</strong><small>Unidades entrantes</small></article>
        <article className="metric-card"><span>Salidas página</span><strong>{totalSalidas}</strong><small>Unidades salientes</small></article>
        <article className="metric-card"><span>Último saldo</span><strong>{lastBalance}</strong><small>Producto filtrado o último movimiento</small></article>
      </div>

      <SectionPanel title="Kardex" description="Consulta movimientos recientes o filtra por producto.">
        <div className="toolbar-row">
          <select value={selectedProductId} onChange={(event) => { setPage(1); setSelectedProductId(event.target.value); }}>
            <option value="">Todos los productos</option>
            {productItems.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.nombre}</option>)}
          </select>
          <button className="secondary-button" onClick={() => void kardex.reload()}>Actualizar</button>
        </div>
        <InlineState loading={kardex.loading || products.loading} error={kardex.error ?? products.error} empty={movements.length === 0} emptyTitle="Sin movimientos" emptyDescription="Registra compras, ventas o ajustes para alimentar el kardex.">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Fecha</th><th>Tipo</th><th>Origen</th><th>Referencia</th><th>Cantidad</th><th>Costo</th><th>Saldo</th><th>Valor saldo</th></tr></thead>
              <tbody>
                {movements.map((movement) => (
                  <tr key={movement.id}>
                    <td>{movement.created_at ? new Date(movement.created_at).toLocaleString() : '—'}</td>
                    <td><StatusBadge tone={movementTone(movement.tipo_movimiento)}>{movement.tipo_movimiento}</StatusBadge></td>
                    <td>{movement.origen}</td>
                    <td>{movement.referencia ?? '—'}</td>
                    <td>{movement.cantidad}</td>
                    <td>{money(movement.costo_unitario ?? 0)}</td>
                    <td>{movement.saldo_cantidad}</td>
                    <td>{money(movement.saldo_valor ?? 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={page}
            pageSize={pageSize}
            total={Math.max(movements.length + skip, page * pageSize)}
            onPageChange={setPage}
            onPageSizeChange={(nextPageSize) => {
              setPage(1);
              setPageSize(nextPageSize);
            }}
          />
        </InlineState>
      </SectionPanel>

      <div className="module-grid">
        <SectionPanel title="Entrada manual" description="Ajuste controlado para carga inicial, corrección o recepción extraordinaria.">
          {operationMessage ? <div className="alert success wide-field">{operationMessage}</div> : null}
          <form className="crud-form" onSubmit={(event) => void submitEntry(event)}>
            <label>Sucursal ID<input value={sucursalId} onChange={(event) => setSucursalId(event.target.value)} required /></label>
            <label>Producto<select value={entryProductId} onChange={(event) => selectEntryProduct(event.target.value)} required><option value="">Producto</option>{productItems.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.nombre}</option>)}</select></label>
            <label>Cantidad<input type="number" min="0.001" step="0.001" value={entryQty} onChange={(event) => setEntryQty(Number(event.target.value))} required /></label>
            <label>Costo unitario<input type="number" min="0" step="0.01" value={entryCost} onChange={(event) => setEntryCost(Number(event.target.value))} required /></label>
            <label>Referencia<input value={entryReference} onChange={(event) => setEntryReference(event.target.value)} /></label>
            <label>Lote<input value={entryBatch} onChange={(event) => setEntryBatch(event.target.value)} /></label>
            {formError ? <div className="alert error wide-field">{formError}</div> : null}
            <div className="form-actions wide-field"><button className="primary-button" disabled={savingEntry}>{savingEntry ? 'Registrando…' : 'Registrar entrada'}</button></div>
          </form>
        </SectionPanel>

        <SectionPanel title="Salida manual" description="Salida PEPS para ajustes, mermas o consumo interno con trazabilidad.">
          <form className="crud-form" onSubmit={(event) => void submitExit(event)}>
            <label>Sucursal ID<input value={sucursalId} onChange={(event) => setSucursalId(event.target.value)} required /></label>
            <label>Producto<select value={exitProductId} onChange={(event) => setExitProductId(event.target.value)} required><option value="">Producto</option>{productItems.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.nombre}</option>)}</select></label>
            <label>Cantidad<input type="number" min="0.001" step="0.001" value={exitQty} onChange={(event) => setExitQty(Number(event.target.value))} required /></label>
            <label>Referencia<input value={exitReference} onChange={(event) => setExitReference(event.target.value)} /></label>
            <div className="form-actions wide-field"><button className="danger-button" disabled={savingExit}>{savingExit ? 'Registrando…' : 'Registrar salida'}</button></div>
          </form>
        </SectionPanel>
      </div>

      <SectionPanel title="Alertas de stock mínimo" description="Productos que requieren reposición por sucursal.">
        <InlineState loading={alerts.loading} error={alerts.error} empty={(alerts.data ?? []).length === 0} emptyTitle="Sin alertas" emptyDescription="No hay productos bajo mínimo para la sucursal seleccionada.">
          <div className="alert-list">
            {(alerts.data ?? []).map((alert) => (
              <div className="alert-item" key={`${alert.sucursal_id}-${alert.producto_id}`}>
                <strong>{alert.sku} · {alert.nombre}</strong>
                <span>{alert.mensaje}</span>
                <small>Actual: {alert.cantidad_actual} · Mínimo: {alert.stock_minimo} · Valor: {money(alert.valor_total)}</small>
              </div>
            ))}
          </div>
        </InlineState>
      </SectionPanel>
    </section>
  );
}
