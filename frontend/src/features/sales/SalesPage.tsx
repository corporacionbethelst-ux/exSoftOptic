import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { useAuth } from '../auth/AuthContext';
import { catalogService, salesService } from '../../services';
import type { Producto } from '../../types/catalog';
import type { Venta, VentaConfirmarPayload, VentaLineaPayload, VentaPayload } from '../../types/sales';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

const DEFAULT_CONFIRM: VentaConfirmarPayload = {
  cuenta_cobro: '102.01',
  cuenta_ingresos: '401.01',
  cuenta_costo_ventas: '501.01',
  cuenta_inventario: '115.01',
};

function emptyLine(products: Producto[]): VentaLineaPayload {
  const product = products[0];
  return {
    producto_id: product?.id ?? '',
    descripcion: product?.nombre ?? '',
    cantidad: 1,
    precio_unitario: Number(product?.precio_venta ?? 0),
    descuento: 0,
  };
}

export function SalesPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [sucursalId, setSucursalId] = useState(user?.sucursal_id ?? '');
  const [folio, setFolio] = useState(() => `VTA-${Date.now()}`);
  const [clienteNombre, setClienteNombre] = useState('Cliente mostrador');
  const [clienteEmail, setClienteEmail] = useState('cliente.demo@example.com');
  const [metodoPago, setMetodoPago] = useState('EFECTIVO');
  const [referenciaPago, setReferenciaPago] = useState('');
  const [lineas, setLineas] = useState<VentaLineaPayload[]>([]);
  const [pendingConfirm, setPendingConfirm] = useState<Venta | null>(null);
  const [pendingReturn, setPendingReturn] = useState<Venta | null>(null);
  const [returnFolio, setReturnFolio] = useState(() => `DEV-${Date.now()}`);
  const [returnReason, setReturnReason] = useState('Devolución solicitada por cliente');
  const [formError, setFormError] = useState<string | null>(null);
  const [operationMessage, setOperationMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [processing, setProcessing] = useState(false);
  const skip = (page - 1) * pageSize;

  const loadSales = useCallback(() => salesService.list({ skip, limit: pageSize }), [pageSize, skip]);
  const loadProducts = useCallback(() => catalogService.products({ limit: 100 }), []);
  const sales = useApiResource(loadSales);
  const products = useApiResource(loadProducts);
  const salesItems = sales.data ?? [];
  const productItems = products.data?.items ?? products.data?.productos ?? [];
  const subtotal = useMemo(() => lineas.reduce((total, line) => total + line.cantidad * line.precio_unitario - line.descuento, 0), [lineas]);
  const impuestos = useMemo(() => Number((subtotal * 0.16).toFixed(2)), [subtotal]);
  const total = useMemo(() => Number((subtotal + impuestos).toFixed(2)), [subtotal, impuestos]);

  function addLine() {
    setLineas((current) => [...current, emptyLine(productItems)]);
  }

  function updateLine(index: number, patch: Partial<VentaLineaPayload>) {
    setLineas((current) => current.map((line, lineIndex) => (lineIndex === index ? { ...line, ...patch } : line)));
  }

  function selectProduct(index: number, productId: string) {
    const product = productItems.find((item) => item.id === productId);
    updateLine(index, {
      producto_id: productId,
      descripcion: product?.nombre ?? '',
      precio_unitario: Number(product?.precio_venta ?? 0),
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    setOperationMessage(null);
    try {
      const payload: VentaPayload = {
        sucursal_id: sucursalId,
        cliente: { nombre: clienteNombre, email: clienteEmail || null },
        folio,
        impuestos,
        lineas,
        pagos: total > 0 ? [{ metodo_pago: metodoPago, monto: total, referencia: referenciaPago || null }] : [],
      };
      await salesService.create(payload);
      setOperationMessage('Venta creada correctamente. Ahora puedes confirmarla desde el listado.');
      setFolio(`VTA-${Date.now()}`);
      setLineas([]);
      await sales.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo crear la venta');
    } finally {
      setSaving(false);
    }
  }

  async function confirmSale() {
    if (!pendingConfirm) return;
    setProcessing(true);
    setFormError(null);
    try {
      await salesService.confirm(pendingConfirm.id, DEFAULT_CONFIRM);
      setPendingConfirm(null);
      setOperationMessage('Venta confirmada correctamente.');
      await sales.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo confirmar la venta');
    } finally {
      setProcessing(false);
    }
  }

  async function registerReturn() {
    if (!pendingReturn?.lineas?.[0]) return;
    setProcessing(true);
    setFormError(null);
    try {
      await salesService.returnSale(pendingReturn.id, {
        folio: returnFolio,
        motivo: returnReason,
        lineas: [{ venta_linea_id: pendingReturn.lineas[0].id, cantidad: 1 }],
        ...DEFAULT_CONFIRM,
      });
      setPendingReturn(null);
      setReturnFolio(`DEV-${Date.now()}`);
      setOperationMessage('Devolución registrada correctamente.');
      await sales.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo registrar la devolución');
    } finally {
      setProcessing(false);
    }
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Operación"
        title="Ventas"
        description="Fase operativa de ventas: crear borradores, agregar líneas, registrar pago, confirmar venta y preparar devoluciones."
      />

      <SectionPanel title="Listado de ventas" footer={<span className="muted compact">{salesItems.length} en esta página</span>}>
        <InlineState loading={sales.loading} error={sales.error} empty={salesItems.length === 0} emptyTitle="Sin ventas" emptyDescription="Crea una venta o ejecuta make seed-demo.">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Folio</th><th>Estado</th><th>Líneas</th><th>Subtotal</th><th>Impuestos</th><th>Total</th><th>Acciones</th></tr></thead>
              <tbody>
                {salesItems.map((sale) => (
                  <tr key={sale.id}>
                    <td>{sale.folio}</td>
                    <td><StatusBadge tone={sale.estado === 'CONFIRMADA' ? 'success' : 'warning'}>{sale.estado}</StatusBadge></td>
                    <td>{sale.lineas?.length ?? 0}</td>
                    <td>{money(sale.subtotal)}</td>
                    <td>{money(sale.impuestos)}</td>
                    <td>{money(sale.total)}</td>
                    <td className="action-cell">
                      <button className="secondary-button" disabled={sale.estado === 'CONFIRMADA'} onClick={() => setPendingConfirm(sale)}>Confirmar</button>
                      <button className="secondary-button" disabled={sale.estado !== 'CONFIRMADA'} onClick={() => setPendingReturn(sale)}>Devolver</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={page}
            pageSize={pageSize}
            total={Math.max(salesItems.length + skip, page * pageSize)}
            onPageChange={setPage}
            onPageSizeChange={(nextPageSize) => {
              setPage(1);
              setPageSize(nextPageSize);
            }}
          />
        </InlineState>
      </SectionPanel>

      <SectionPanel title="Nueva venta" description="Captura rápida para venta de mostrador usando cliente inline y productos del catálogo.">
        {operationMessage ? <div className="alert success wide-field">{operationMessage}</div> : null}
        <form className="crud-form" onSubmit={(event) => void handleSubmit(event)}>
          <label>Folio<input value={folio} onChange={(event) => setFolio(event.target.value)} required /></label>
          <label>Sucursal ID<input value={sucursalId} onChange={(event) => setSucursalId(event.target.value)} required /></label>
          <label>Cliente<input value={clienteNombre} onChange={(event) => setClienteNombre(event.target.value)} required /></label>
          <label>Email cliente<input type="email" value={clienteEmail} onChange={(event) => setClienteEmail(event.target.value)} /></label>
          <label>Método pago<input value={metodoPago} onChange={(event) => setMetodoPago(event.target.value)} required /></label>
          <label>Referencia pago<input value={referenciaPago} onChange={(event) => setReferenciaPago(event.target.value)} /></label>

          <div className="wide-field line-editor">
            <div className="split"><strong>Líneas</strong><button className="secondary-button" type="button" onClick={addLine}>Agregar línea</button></div>
            <InlineState loading={products.loading} error={products.error} empty={lineas.length === 0} emptyTitle="Sin líneas" emptyDescription="Agrega al menos un producto a la venta.">
              {lineas.map((line, index) => (
                <div className="line-row" key={`${line.producto_id}-${index}`}>
                  <select value={line.producto_id} onChange={(event) => selectProduct(index, event.target.value)} required>
                    <option value="">Producto</option>
                    {productItems.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.nombre}</option>)}
                  </select>
                  <input type="number" min="0.001" step="0.001" value={line.cantidad} onChange={(event) => updateLine(index, { cantidad: Number(event.target.value) })} />
                  <input type="number" min="0" step="0.01" value={line.precio_unitario} onChange={(event) => updateLine(index, { precio_unitario: Number(event.target.value) })} />
                  <input type="number" min="0" step="0.01" value={line.descuento} onChange={(event) => updateLine(index, { descuento: Number(event.target.value) })} />
                  <button className="danger-button" type="button" onClick={() => setLineas((current) => current.filter((_, lineIndex) => lineIndex !== index))}>Quitar</button>
                </div>
              ))}
            </InlineState>
          </div>

          <div className="wide-field totals-card">
            <span>Subtotal: <strong>{money(subtotal)}</strong></span>
            <span>IVA: <strong>{money(impuestos)}</strong></span>
            <span>Total: <strong>{money(total)}</strong></span>
          </div>
          {formError ? <div className="alert error wide-field">{formError}</div> : null}
          <div className="form-actions wide-field">
            <button className="primary-button" disabled={saving || lineas.length === 0}>{saving ? 'Guardando…' : 'Crear venta'}</button>
          </div>
        </form>
      </SectionPanel>

      <ConfirmDialog open={Boolean(pendingConfirm)} title="Confirmar venta" description="Confirmar descuenta inventario, registra contabilidad y deja la venta lista para facturación/devolución." confirmLabel="Confirmar venta" busy={processing} onConfirm={() => void confirmSale()} onCancel={() => setPendingConfirm(null)}>
        <strong>{pendingConfirm?.folio}</strong>
      </ConfirmDialog>

      <ConfirmDialog open={Boolean(pendingReturn)} title="Registrar devolución" description="La devolución se registrará sobre la primera línea de la venta para validar el flujo operativo inicial." confirmLabel="Registrar devolución" busy={processing} onConfirm={() => void registerReturn()} onCancel={() => setPendingReturn(null)}>
        <div className="form-stack">
          <label>Folio devolución<input value={returnFolio} onChange={(event) => setReturnFolio(event.target.value)} /></label>
          <label>Motivo<input value={returnReason} onChange={(event) => setReturnReason(event.target.value)} /></label>
        </div>
      </ConfirmDialog>
    </section>
  );
}
