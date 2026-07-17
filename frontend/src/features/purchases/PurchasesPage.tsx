import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { catalogService, inventoryService, purchasesService } from '../../services';
import type { Producto } from '../../types/catalog';
import type { OrdenCompra, OrdenCompraLineaPayload, OrdenCompraPayload, RecepcionCompraPayload } from '../../types/purchases';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';
import { useAuth } from '../auth/AuthContext';

const DEFAULT_RECEIPT_ACCOUNTS = {
  cuenta_inventario: '115.01',
  cuenta_cxp: '201.01',
};

function emptyPurchaseLine(products: Producto[]): OrdenCompraLineaPayload {
  const product = products[0];
  return {
    producto_id: product?.id ?? '',
    descripcion: product?.nombre ?? '',
    cantidad: 1,
    costo_unitario: Number(product?.costo_estandar ?? 0),
  };
}

function statusTone(status: string): 'success' | 'warning' | 'danger' | 'neutral' {
  if (status === 'RECIBIDA') return 'success';
  if (status === 'APROBADA' || status === 'PARCIAL') return 'warning';
  return 'neutral';
}

export function PurchasesPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [sucursalId, setSucursalId] = useState(user?.sucursal_id ?? '');
  const [folio, setFolio] = useState(() => `OC-${Date.now()}`);
  const [proveedorNombre, setProveedorNombre] = useState('Proveedor demo');
  const [proveedorEmail, setProveedorEmail] = useState('proveedor.demo@example.com');
  const [proveedorTelefono, setProveedorTelefono] = useState('555-0100');
  const [lineas, setLineas] = useState<OrdenCompraLineaPayload[]>([]);
  const [pendingApproval, setPendingApproval] = useState<OrdenCompra | null>(null);
  const [pendingReceipt, setPendingReceipt] = useState<OrdenCompra | null>(null);
  const [receiptFolio, setReceiptFolio] = useState(() => `REC-${Date.now()}`);
  const [requisitionFolio, setRequisitionFolio] = useState(() => `SOL-${Date.now()}`);
  const [operationMessage, setOperationMessage] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [processing, setProcessing] = useState(false);
  const skip = (page - 1) * pageSize;

  const loadOrders = useCallback(() => purchasesService.listOrders({ skip, limit: pageSize }), [pageSize, skip]);
  const loadProducts = useCallback(() => catalogService.products({ limit: 100 }), []);
  const loadAlerts = useCallback(() => inventoryService.stockAlerts({ sucursal_id: sucursalId || undefined, limit: 20 }), [sucursalId]);
  const orders = useApiResource(loadOrders);
  const products = useApiResource(loadProducts);
  const alerts = useApiResource(loadAlerts, Boolean(sucursalId));
  const orderItems = orders.data ?? [];
  const productItems = products.data?.items ?? products.data?.productos ?? [];
  const subtotal = useMemo(() => lineas.reduce((total, line) => total + line.cantidad * line.costo_unitario, 0), [lineas]);
  const impuestos = useMemo(() => Number((subtotal * 0.16).toFixed(2)), [subtotal]);
  const total = useMemo(() => Number((subtotal + impuestos).toFixed(2)), [subtotal, impuestos]);

  function addLine() {
    setLineas((current) => [...current, emptyPurchaseLine(productItems)]);
  }

  function updateLine(index: number, patch: Partial<OrdenCompraLineaPayload>) {
    setLineas((current) => current.map((line, lineIndex) => (lineIndex === index ? { ...line, ...patch } : line)));
  }

  function selectProduct(index: number, productId: string) {
    const product = productItems.find((item) => item.id === productId);
    updateLine(index, {
      producto_id: productId,
      descripcion: product?.nombre ?? '',
      costo_unitario: Number(product?.costo_estandar ?? 0),
    });
  }

  async function submitOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    setOperationMessage(null);
    try {
      const payload: OrdenCompraPayload = {
        sucursal_id: sucursalId,
        proveedor: {
          nombre: proveedorNombre,
          email: proveedorEmail || null,
          telefono: proveedorTelefono || null,
        },
        folio,
        impuestos,
        lineas,
      };
      await purchasesService.createOrder(payload);
      setOperationMessage('Orden de compra creada correctamente. Puedes aprobarla desde el listado.');
      setFolio(`OC-${Date.now()}`);
      setLineas([]);
      await orders.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo crear la orden de compra');
    } finally {
      setSaving(false);
    }
  }

  async function approveOrder() {
    if (!pendingApproval) return;
    setProcessing(true);
    setFormError(null);
    try {
      await purchasesService.approveOrder(pendingApproval.id);
      setPendingApproval(null);
      setOperationMessage('Orden aprobada correctamente. Ya puede registrarse recepción.');
      await orders.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo aprobar la orden');
    } finally {
      setProcessing(false);
    }
  }

  async function receiveOrder() {
    if (!pendingReceipt) return;
    const receivableLines = pendingReceipt.lineas
      .map((line) => ({ line, pendiente: Number(line.cantidad) - Number(line.cantidad_recibida) }))
      .filter(({ pendiente }) => pendiente > 0);
    if (receivableLines.length === 0) return;
    setProcessing(true);
    setFormError(null);
    try {
      const payload: RecepcionCompraPayload = {
        folio: receiptFolio,
        lineas: receivableLines.map(({ line, pendiente }) => ({ orden_linea_id: line.id, cantidad: pendiente })),
        ...DEFAULT_RECEIPT_ACCOUNTS,
      };
      await purchasesService.receiveOrder(pendingReceipt.id, payload);
      setPendingReceipt(null);
      setReceiptFolio(`REC-${Date.now()}`);
      setOperationMessage('Recepción registrada correctamente. El inventario y el asiento contable fueron actualizados.');
      await orders.reload();
      await alerts.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo registrar la recepción');
    } finally {
      setProcessing(false);
    }
  }

  async function generateRequisition() {
    if (!sucursalId) return;
    setProcessing(true);
    setFormError(null);
    try {
      await purchasesService.generateStockRequisition({
        sucursal_id: sucursalId,
        folio: requisitionFolio,
        observaciones: 'Solicitud generada desde panel de compras por alertas de stock mínimo',
      });
      setRequisitionFolio(`SOL-${Date.now()}`);
      setOperationMessage('Solicitud de compra generada desde stock mínimo.');
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo generar la solicitud de compra');
    } finally {
      setProcessing(false);
    }
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Abastecimiento"
        title="Compras"
        description="Fase completa de compras: órdenes, aprobación, recepción contra inventario y reposición sugerida por stock mínimo."
      />

      <SectionPanel title="Órdenes de compra" footer={<span className="muted compact">{orderItems.length} en esta página</span>}>
        <InlineState loading={orders.loading} error={orders.error} empty={orderItems.length === 0} emptyTitle="Sin órdenes" emptyDescription="Crea una orden de compra o ejecuta make seed-demo.">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Folio</th><th>Estado</th><th>Líneas</th><th>Subtotal</th><th>Impuestos</th><th>Total</th><th>Acciones</th></tr></thead>
              <tbody>
                {orderItems.map((order) => (
                  <tr key={order.id}>
                    <td>{order.folio}</td>
                    <td><StatusBadge tone={statusTone(order.estado)}>{order.estado}</StatusBadge></td>
                    <td>{order.lineas.length}</td>
                    <td>{money(order.subtotal)}</td>
                    <td>{money(order.impuestos)}</td>
                    <td>{money(order.total)}</td>
                    <td className="action-cell">
                      <button className="secondary-button" disabled={order.estado !== 'BORRADOR'} onClick={() => setPendingApproval(order)}>Aprobar</button>
                      <button className="secondary-button" disabled={!['APROBADA', 'PARCIAL'].includes(order.estado)} onClick={() => setPendingReceipt(order)}>Recibir</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={page}
            pageSize={pageSize}
            total={Math.max(orderItems.length + skip, page * pageSize)}
            onPageChange={setPage}
            onPageSizeChange={(nextPageSize) => {
              setPage(1);
              setPageSize(nextPageSize);
            }}
          />
        </InlineState>
      </SectionPanel>

      <div className="module-grid">
        <SectionPanel title="Nueva orden" description="Orden de compra con proveedor inline y líneas de producto.">
          {operationMessage ? <div className="alert success wide-field">{operationMessage}</div> : null}
          <form className="crud-form" onSubmit={(event) => void submitOrder(event)}>
            <label>Folio<input value={folio} onChange={(event) => setFolio(event.target.value)} required /></label>
            <label>Sucursal ID<input value={sucursalId} onChange={(event) => setSucursalId(event.target.value)} required /></label>
            <label>Proveedor<input value={proveedorNombre} onChange={(event) => setProveedorNombre(event.target.value)} required /></label>
            <label>Email proveedor<input type="email" value={proveedorEmail} onChange={(event) => setProveedorEmail(event.target.value)} /></label>
            <label>Teléfono proveedor<input value={proveedorTelefono} onChange={(event) => setProveedorTelefono(event.target.value)} /></label>

            <div className="wide-field line-editor">
              <div className="split"><strong>Líneas</strong><button className="secondary-button" type="button" onClick={addLine}>Agregar línea</button></div>
              <InlineState loading={products.loading} error={products.error} empty={lineas.length === 0} emptyTitle="Sin líneas" emptyDescription="Agrega productos a la orden de compra.">
                {lineas.map((line, index) => (
                  <div className="line-row purchase-line-row" key={`${line.producto_id}-${index}`}>
                    <select value={line.producto_id} onChange={(event) => selectProduct(index, event.target.value)} required>
                      <option value="">Producto</option>
                      {productItems.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.nombre}</option>)}
                    </select>
                    <input type="number" min="0.001" step="0.001" value={line.cantidad} onChange={(event) => updateLine(index, { cantidad: Number(event.target.value) })} />
                    <input type="number" min="0" step="0.01" value={line.costo_unitario} onChange={(event) => updateLine(index, { costo_unitario: Number(event.target.value) })} />
                    <button className="danger-button" type="button" onClick={() => setLineas((current) => current.filter((_, lineIndex) => lineIndex !== index))}>Quitar</button>
                  </div>
                ))}
              </InlineState>
            </div>

            <div className="wide-field totals-card">
              <span>Subtotal: <strong>{money(subtotal)}</strong></span>
              <span>IVA estimado: <strong>{money(impuestos)}</strong></span>
              <span>Total: <strong>{money(total)}</strong></span>
            </div>
            {formError ? <div className="alert error wide-field">{formError}</div> : null}
            <div className="form-actions wide-field">
              <button className="primary-button" disabled={saving || lineas.length === 0}>{saving ? 'Guardando…' : 'Crear orden'}</button>
            </div>
          </form>
        </SectionPanel>

        <SectionPanel title="Reposición sugerida" description="Alertas de stock mínimo y generación rápida de solicitud de compra.">
          <div className="form-stack">
            <label>Sucursal para alertas<input value={sucursalId} onChange={(event) => setSucursalId(event.target.value)} /></label>
            <label>Folio solicitud<input value={requisitionFolio} onChange={(event) => setRequisitionFolio(event.target.value)} /></label>
            <button className="secondary-button" disabled={processing || !sucursalId} onClick={() => void generateRequisition()}>Generar solicitud por stock mínimo</button>
          </div>
          <InlineState loading={alerts.loading} error={alerts.error} empty={(alerts.data ?? []).length === 0} emptyTitle="Sin alertas" emptyDescription="No hay productos bajo stock mínimo para esta sucursal.">
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
      </div>

      <ConfirmDialog open={Boolean(pendingApproval)} title="Aprobar orden" description="La orden quedará lista para recibir mercancía contra inventario." confirmLabel="Aprobar" busy={processing} onConfirm={() => void approveOrder()} onCancel={() => setPendingApproval(null)}>
        <strong>{pendingApproval?.folio}</strong>
      </ConfirmDialog>

      <ConfirmDialog open={Boolean(pendingReceipt)} title="Registrar recepción" description="Se recibirán todas las cantidades pendientes de la orden y se actualizará inventario." confirmLabel="Recibir mercancía" busy={processing} onConfirm={() => void receiveOrder()} onCancel={() => setPendingReceipt(null)}>
        <div className="form-stack">
          <label>Folio recepción<input value={receiptFolio} onChange={(event) => setReceiptFolio(event.target.value)} /></label>
          <div className="table-wrap compact-table">
            <table>
              <thead><tr><th>Producto</th><th>Pendiente</th><th>Costo</th></tr></thead>
              <tbody>
                {pendingReceipt?.lineas.map((line) => (
                  <tr key={line.id}><td>{line.descripcion}</td><td>{Number(line.cantidad) - Number(line.cantidad_recibida)}</td><td>{money(line.costo_unitario)}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </ConfirmDialog>
    </section>
  );
}
