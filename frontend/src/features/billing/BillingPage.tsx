import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { billingService, labService, salesService } from '../../services';
import type { Garantia } from '../../types/billing';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

const PAGE_SIZE = 50;
const WARRANTY_TYPES: Garantia['tipo'][] = ['ARMAZON', 'LENTE', 'TRATAMIENTO', 'SERVICIO'];
function today() { return new Date().toISOString().slice(0, 10); }
function future(days = 365) { return new Date(Date.now() + days * 86_400_000).toISOString().slice(0, 10); }
function optional(value: string) { return value.trim() || null; }
function tone(status: string): 'success' | 'warning' | 'danger' | 'neutral' { if (['TIMBRADA', 'ACTIVA', 'APROBADA'].includes(status)) return 'success'; if (['CANCELADA', 'VENCIDA', 'RECHAZADA'].includes(status)) return 'danger'; if (['EN_RECLAMO', 'ABIERTA'].includes(status)) return 'warning'; return 'neutral'; }

export function BillingPage() {
  const [page, setPage] = useState(1);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState('');
  const [selectedWarrantyId, setSelectedWarrantyId] = useState('');
  const [selectedClaimId, setSelectedClaimId] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);
  const [invoiceForm, setInvoiceForm] = useState(() => ({ venta_id: '', folio: `FAC-${Date.now()}`, proveedor: 'MOCK', moneda: 'MXN' }));
  const [cancelReason, setCancelReason] = useState('Cancelación solicitada desde frontend');
  const [warrantyForm, setWarrantyForm] = useState(() => ({ venta_id: '', orden_laboratorio_id: '', folio: `GAR-${Date.now()}`, tipo: 'LENTE' as Garantia['tipo'], fecha_inicio: today(), fecha_fin: future(), descripcion: 'Garantía estándar', condiciones: 'Aplica por defectos de fabricación.' }));
  const [claimForm, setClaimForm] = useState(() => ({ folio: `REC-${Date.now()}`, motivo: '' }));
  const [resolutionForm, setResolutionForm] = useState({ estado: 'APROBADA' as 'APROBADA' | 'RECHAZADA' | 'CERRADA', resolucion: '' });
  const skip = (page - 1) * PAGE_SIZE;

  const invoices = useApiResource(useCallback(() => billingService.invoices({ skip, limit: PAGE_SIZE }), [skip]));
  const warranties = useApiResource(useCallback(() => billingService.warranties({ skip, limit: PAGE_SIZE }), [skip]));
  const sales = useApiResource(useCallback(() => salesService.list({ skip: 0, limit: 100 }), []));
  const labOrders = useApiResource(useCallback(() => labService.orders({ skip: 0, limit: 100 }), []));
  const invoiceItems = useMemo(() => invoices.data ?? [], [invoices.data]);
  const warrantyItems = useMemo(() => warranties.data ?? [], [warranties.data]);
  const saleItems = sales.data ?? [];
  const orderItems = labOrders.data ?? [];
  const selectedInvoice = invoiceItems.find((invoice) => invoice.id === selectedInvoiceId) ?? invoiceItems[0];
  const selectedWarranty = warrantyItems.find((warranty) => warranty.id === selectedWarrantyId) ?? warrantyItems[0];
  const claimItems = selectedWarranty?.reclamaciones ?? [];
  const confirmedSales = saleItems.filter((sale) => sale.estado === 'CONFIRMADA');
  const deliveredOrders = orderItems.filter((order) => order.estado === 'ENTREGADA');

  async function withOperation(label: string, operation: () => Promise<unknown>) {
    setSaving(label); setError(null); setMessage(null);
    try { await operation(); setMessage('Operación completada correctamente.'); await Promise.all([invoices.reload(), warranties.reload(), labOrders.reload()]); }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'No se pudo completar la operación'); }
    finally { setSaving(null); }
  }

  async function issueInvoice(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('emitir', async () => { const invoice = await billingService.issueInvoice(invoiceForm); setSelectedInvoiceId(invoice.id); setInvoiceForm((current) => ({ ...current, folio: `FAC-${Date.now()}` })); }); }
  async function cancelInvoice(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!selectedInvoice) { setError('Selecciona una factura.'); return; } await withOperation('cancelar', () => billingService.cancelInvoice(selectedInvoice.id, { motivo: cancelReason })); }
  async function createWarranty(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('garantia', async () => { const payload = { ...warrantyForm, orden_laboratorio_id: optional(warrantyForm.orden_laboratorio_id), descripcion: optional(warrantyForm.descripcion), condiciones: optional(warrantyForm.condiciones) }; const warranty = warrantyForm.orden_laboratorio_id ? await billingService.createWarrantyFromLab(warrantyForm.orden_laboratorio_id, payload) : await billingService.createWarranty(payload); setSelectedWarrantyId(warranty.id); setWarrantyForm((current) => ({ ...current, folio: `GAR-${Date.now()}` })); }); }
  async function openClaim(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!selectedWarranty) { setError('Selecciona una garantía.'); return; } await withOperation('reclamacion', async () => { const claim = await billingService.openClaim(selectedWarranty.id, claimForm); setSelectedClaimId(claim.id); setClaimForm({ folio: `REC-${Date.now()}`, motivo: '' }); }); }
  async function resolveClaim(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!selectedClaimId) { setError('Selecciona una reclamación abierta.'); return; } await withOperation('resolver', () => billingService.resolveClaim(selectedClaimId, resolutionForm)); }

  return <section className="page-stack">
    <PageHeader eyebrow="Facturación y garantías" title="Facturas, cancelaciones y postventa" description="Fase comercial final: emisión/cancelación de facturas y administración de garantías con reclamaciones." />
    {message ? <div className="alert success">{message}</div> : null}{error ? <div className="alert error">{error}</div> : null}

    <div className="module-grid two-columns">
      <SectionPanel title="Facturas" footer={<Pagination page={page} pageSize={PAGE_SIZE} total={invoiceItems.length} onPageChange={setPage} onPageSizeChange={() => undefined} />}><InlineState loading={invoices.loading} error={invoices.error} empty={invoiceItems.length === 0} emptyTitle="Sin facturas" emptyDescription="Emite una factura desde una venta confirmada."><div className="table-wrap compact-table"><table><thead><tr><th>Folio</th><th>Estado</th><th>UUID</th><th>Total</th></tr></thead><tbody>{invoiceItems.map((invoice) => <tr key={invoice.id} className={invoice.id === selectedInvoice?.id ? 'selected-row' : undefined} onClick={() => setSelectedInvoiceId(invoice.id)}><td><strong>{invoice.folio}</strong><br /><span className="compact-id">{invoice.id}</span></td><td><StatusBadge tone={tone(invoice.estado)}>{invoice.estado}</StatusBadge></td><td className="compact-id">{invoice.uuid_fiscal ?? '—'}</td><td>{money(invoice.total)}</td></tr>)}</tbody></table></div></InlineState></SectionPanel>
      <SectionPanel title="Emitir factura"><form className="crud-form" onSubmit={issueInvoice}><label>Venta<select required value={invoiceForm.venta_id} onChange={(event) => setInvoiceForm({ ...invoiceForm, venta_id: event.target.value })}><option value="">Selecciona venta</option>{confirmedSales.map((sale) => <option key={sale.id} value={sale.id}>{sale.folio} · {money(sale.total)}</option>)}</select></label><div className="form-row"><label>Folio<input required value={invoiceForm.folio} onChange={(event) => setInvoiceForm({ ...invoiceForm, folio: event.target.value })} /></label><label>Proveedor<input value={invoiceForm.proveedor} onChange={(event) => setInvoiceForm({ ...invoiceForm, proveedor: event.target.value })} /></label></div><button disabled={saving === 'emitir'}>{saving === 'emitir' ? 'Timbrando…' : 'Emitir factura'}</button></form><form className="crud-form reminder-form" onSubmit={cancelInvoice}><label>Motivo cancelación<textarea value={cancelReason} onChange={(event) => setCancelReason(event.target.value)} /></label><button className="danger" disabled={!selectedInvoice || selectedInvoice.estado !== 'TIMBRADA' || saving === 'cancelar'}>Cancelar factura seleccionada</button></form></SectionPanel>
    </div>

    <SectionPanel title="Detalle de factura" footer={<span className="muted compact">{selectedInvoice ? selectedInvoice.folio : 'Selecciona una factura'}</span>}>
      <div className="module-grid two-columns"><div className="table-wrap compact-table"><table><thead><tr><th>Producto</th><th>Descripción</th><th>Cantidad</th><th>Importe</th></tr></thead><tbody>{selectedInvoice?.lineas?.map((line) => <tr key={line.id}><td className="compact-id">{line.producto_id}</td><td>{line.descripcion}</td><td>{line.cantidad}</td><td>{money(line.importe)}</td></tr>)}</tbody></table></div><div className="alert-list">{selectedInvoice?.eventos?.map((event) => <div className="alert-item" key={event.id}><strong>{event.tipo_evento}</strong><span>{event.descripcion}</span><small>{new Date(event.fecha).toLocaleString()}</small></div>)}</div></div>
    </SectionPanel>

    <div className="module-grid two-columns">
      <SectionPanel title="Garantías"><InlineState loading={warranties.loading} error={warranties.error} empty={warrantyItems.length === 0} emptyTitle="Sin garantías" emptyDescription="Crea una garantía desde una venta confirmada o una orden entregada."><div className="table-wrap compact-table"><table><thead><tr><th>Folio</th><th>Tipo</th><th>Vigencia</th><th>Estado</th></tr></thead><tbody>{warrantyItems.map((warranty) => <tr key={warranty.id} className={warranty.id === selectedWarranty?.id ? 'selected-row' : undefined} onClick={() => setSelectedWarrantyId(warranty.id)}><td><strong>{warranty.folio}</strong><br /><span className="compact-id">{warranty.id}</span></td><td>{warranty.tipo}</td><td>{warranty.fecha_inicio} - {warranty.fecha_fin}</td><td><StatusBadge tone={tone(warranty.estado)}>{warranty.estado}</StatusBadge></td></tr>)}</tbody></table></div></InlineState></SectionPanel>
      <SectionPanel title="Crear garantía"><form className="crud-form" onSubmit={createWarranty}><label>Venta<select required value={warrantyForm.venta_id} onChange={(event) => setWarrantyForm({ ...warrantyForm, venta_id: event.target.value })}><option value="">Selecciona venta</option>{confirmedSales.map((sale) => <option key={sale.id} value={sale.id}>{sale.folio}</option>)}</select></label><label>Orden entregada opcional<select value={warrantyForm.orden_laboratorio_id} onChange={(event) => setWarrantyForm({ ...warrantyForm, orden_laboratorio_id: event.target.value })}><option value="">Sin orden</option>{deliveredOrders.map((order) => <option key={order.id} value={order.id}>{order.folio}</option>)}</select></label><div className="form-row"><label>Folio<input required value={warrantyForm.folio} onChange={(event) => setWarrantyForm({ ...warrantyForm, folio: event.target.value })} /></label><label>Tipo<select value={warrantyForm.tipo} onChange={(event) => setWarrantyForm({ ...warrantyForm, tipo: event.target.value as Garantia['tipo'] })}>{WARRANTY_TYPES.map((type) => <option key={type}>{type}</option>)}</select></label></div><div className="form-row"><label>Inicio<input type="date" value={warrantyForm.fecha_inicio} onChange={(event) => setWarrantyForm({ ...warrantyForm, fecha_inicio: event.target.value })} /></label><label>Fin<input type="date" value={warrantyForm.fecha_fin} onChange={(event) => setWarrantyForm({ ...warrantyForm, fecha_fin: event.target.value })} /></label></div><label>Descripción<textarea value={warrantyForm.descripcion} onChange={(event) => setWarrantyForm({ ...warrantyForm, descripcion: event.target.value })} /></label><button disabled={saving === 'garantia'}>Crear garantía</button></form></SectionPanel>
    </div>

    <div className="module-grid two-columns">
      <SectionPanel title="Reclamaciones"><div className="alert-list">{claimItems.map((claim) => <div className="alert-item" key={claim.id} onClick={() => setSelectedClaimId(claim.id)}><strong>{claim.folio}</strong><span>{claim.motivo}</span><StatusBadge tone={tone(claim.estado)}>{claim.estado}</StatusBadge>{claim.resolucion ? <small>{claim.resolucion}</small> : null}</div>)}</div><form className="crud-form reminder-form" onSubmit={openClaim}><label>Folio<input value={claimForm.folio} onChange={(event) => setClaimForm({ ...claimForm, folio: event.target.value })} /></label><label>Motivo<textarea required value={claimForm.motivo} onChange={(event) => setClaimForm({ ...claimForm, motivo: event.target.value })} /></label><button disabled={!selectedWarranty || saving === 'reclamacion'}>Abrir reclamación</button></form></SectionPanel>
      <SectionPanel title="Resolver reclamación"><form className="crud-form" onSubmit={resolveClaim}><label>Reclamación ID<input value={selectedClaimId} onChange={(event) => setSelectedClaimId(event.target.value)} /></label><label>Estado<select value={resolutionForm.estado} onChange={(event) => setResolutionForm({ ...resolutionForm, estado: event.target.value as 'APROBADA' | 'RECHAZADA' | 'CERRADA' })}><option>APROBADA</option><option>RECHAZADA</option><option>CERRADA</option></select></label><label>Resolución<textarea required value={resolutionForm.resolucion} onChange={(event) => setResolutionForm({ ...resolutionForm, resolucion: event.target.value })} /></label><button disabled={!selectedClaimId || saving === 'resolver'}>Resolver</button></form></SectionPanel>
    </div>
  </section>;
}
