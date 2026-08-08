import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { FlaskConical } from 'lucide-react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { catalogService, labService, salesService } from '../../services';
import type { ControlCalidadPayload } from '../../types/lab';
import { dateTime } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

const PAGE_SIZE = 50;
const QC_RESULTS: ControlCalidadPayload['resultado'][] = ['APROBADO', 'RETRABAJO', 'RECHAZADO'];

function tone(status: string): 'success' | 'warning' | 'danger' | 'neutral' {
  if (status === 'ENTREGADA' || status === 'LISTA_ENTREGA') return 'success';
  if (status === 'RECHAZADA') return 'danger';
  if (['EN_PROCESO', 'CONTROL_CALIDAD', 'PENDIENTE'].includes(status)) return 'warning';
  return 'neutral';
}

function localDateTime(offsetDays = 3) {
  const date = new Date(Date.now() + offsetDays * 86_400_000);
  date.setSeconds(0, 0);
  return date.toISOString().slice(0, 16);
}

function toIso(value: string) {
  return value ? new Date(value).toISOString() : null;
}

export function LabPage() {
  const [page, setPage] = useState(1);
  const [selectedOrderId, setSelectedOrderId] = useState('');
  const [saleId, setSaleId] = useState('');
  const [folio, setFolio] = useState(() => `LAB-${Date.now()}`);
  const [prioridad, setPrioridad] = useState('NORMAL');
  const [fechaPrometida, setFechaPrometida] = useState(() => localDateTime(3));
  const [createNotes, setCreateNotes] = useState('Orden generada desde frontend');
  const [productId, setProductId] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [consumptionNotes, setConsumptionNotes] = useState('Material consumido en laboratorio');
  const [stageNotes, setStageNotes] = useState('Etapa completada desde el panel');
  const [qcResult, setQcResult] = useState<ControlCalidadPayload['resultado']>('APROBADO');
  const [qcReason, setQcReason] = useState('');
  const [qcNotes, setQcNotes] = useState('Control de calidad registrado');
  const [saving, setSaving] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const skip = (page - 1) * PAGE_SIZE;

  const loadOrders = useCallback(() => labService.orders({ skip, limit: PAGE_SIZE }), [skip]);
  const orders = useApiResource(loadOrders);
  const sales = useApiResource(() => salesService.list({ skip: 0, limit: 100 }));
  const products = useApiResource(() => catalogService.products({ skip: 0, limit: 100 }));
  const orderItems = useMemo(() => orders.data ?? [], [orders.data]);
  const saleItems = sales.data ?? [];
  const productItems = products.data?.items ?? products.data?.productos ?? [];
  const selectedOrder = useMemo(() => orderItems.find((order) => order.id === selectedOrderId) ?? orderItems[0], [orderItems, selectedOrderId]);
  const activeStage = selectedOrder?.etapas?.find((stage) => stage.estado === 'EN_PROCESO');
  const confirmedSales = saleItems.filter((sale) => sale.estado === 'CONFIRMADA' && sale.paciente_id);

  async function withOperation(label: string, operation: () => Promise<unknown>) {
    setSaving(label); setError(null); setMessage(null);
    try {
      await operation();
      setMessage('Operación de laboratorio completada correctamente.');
      await orders.reload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'No se pudo completar la operación');
    } finally {
      setSaving(null);
    }
  }

  async function submitCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!saleId) { setError('Selecciona una venta confirmada con paciente.'); return; }
    await withOperation('crear', async () => {
      const created = await labService.createFromSale(saleId, { folio, prioridad, fecha_prometida: toIso(fechaPrometida), observaciones: createNotes || null });
      setSelectedOrderId(created.id);
      setFolio(`LAB-${Date.now()}`);
    });
  }

  async function submitConsumption(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedOrder || !productId) { setError('Selecciona orden y producto para consumir material.'); return; }
    await withOperation('consumo', () => labService.registerConsumption(selectedOrder.id, { producto_id: productId, cantidad: Number(quantity), observaciones: consumptionNotes || null }));
  }

  async function submitQuality(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedOrder) { setError('Selecciona una orden para control de calidad.'); return; }
    await withOperation('calidad', () => labService.qualityControl(selectedOrder.id, { resultado: qcResult, motivo_rechazo: qcReason || null, observaciones: qcNotes || null }));
  }

  return (
    <section className="page-stack">
      <PageHeader eyebrow="Laboratorio" title="Órdenes, etapas y calidad" description="Fase laboratorio completa: creación desde ventas confirmadas, inicio, avance de etapas, consumo de materiales, control de calidad y entrega." />
      {message ? <div className="alert success">{message}</div> : null}
      {error ? <div className="alert error">{error}</div> : null}

      <div className="module-grid two-columns">
        <SectionPanel title={<><FlaskConical size={18} /> Trabajos activos</>} footer={<Pagination page={page} pageSize={PAGE_SIZE} total={orderItems.length} onPageChange={setPage} onPageSizeChange={() => undefined} />}>
          <InlineState loading={orders.loading} error={orders.error} empty={orderItems.length === 0} emptyTitle="Sin órdenes de laboratorio" emptyDescription="Crea una orden desde una venta confirmada con paciente o ejecuta el seed demo.">
            <div className="table-wrap compact-table">
              <table><thead><tr><th>Folio</th><th>Prioridad</th><th>Prometida</th><th>Progreso</th><th>Estado</th></tr></thead><tbody>{orderItems.map((order) => {
                const done = order.etapas?.filter((stage) => stage.estado === 'COMPLETADA').length ?? 0;
                const total = order.etapas?.length ?? 0;
                return <tr key={order.id} className={order.id === selectedOrder?.id ? 'selected-row' : undefined} onClick={() => setSelectedOrderId(order.id)}><td><strong>{order.folio}</strong><br /><span className="compact-id">{order.id}</span></td><td>{order.prioridad}</td><td>{dateTime(order.fecha_prometida)}</td><td>{done}/{total}</td><td><StatusBadge tone={tone(order.estado)}>{order.estado}</StatusBadge></td></tr>;
              })}</tbody></table>
            </div>
          </InlineState>
        </SectionPanel>

        <SectionPanel title="Crear orden desde venta" footer={<span className="muted compact">Ventas confirmadas con paciente</span>}>
          <form className="crud-form" onSubmit={submitCreate}>
            <label>Venta<select value={saleId} onChange={(event) => setSaleId(event.target.value)}><option value="">Selecciona venta</option>{confirmedSales.map((sale) => <option key={sale.id} value={sale.id}>{sale.folio} · {sale.total}</option>)}</select></label>
            <label>Folio<input required value={folio} onChange={(event) => setFolio(event.target.value)} /></label>
            <div className="form-row"><label>Prioridad<select value={prioridad} onChange={(event) => setPrioridad(event.target.value)}><option>NORMAL</option><option>ALTA</option><option>URGENTE</option></select></label><label>Prometida<input type="datetime-local" value={fechaPrometida} onChange={(event) => setFechaPrometida(event.target.value)} /></label></div>
            <label>Observaciones<textarea value={createNotes} onChange={(event) => setCreateNotes(event.target.value)} /></label>
            <button type="submit" disabled={saving === 'crear'}>{saving === 'crear' ? 'Creando…' : 'Crear orden'}</button>
          </form>
        </SectionPanel>
      </div>

      <SectionPanel title="Detalle y flujo operativo" footer={<span className="muted compact">{selectedOrder ? selectedOrder.folio : 'Selecciona una orden'}</span>}>
        {selectedOrder ? <div className="lab-detail-grid">
          <div className="status-timeline">{selectedOrder.etapas?.map((stage) => <div key={stage.id} className={`timeline-step ${stage.estado.toLowerCase()}`}><strong>{stage.etapa}</strong><span>{stage.estado}</span><small>{stage.fecha_inicio ? `Inicio: ${dateTime(stage.fecha_inicio)}` : 'Pendiente'}</small><small>{stage.fecha_fin ? `Fin: ${dateTime(stage.fecha_fin)}` : stage.observaciones ?? ''}</small></div>)}</div>
          <div className="action-panel">
            <button className="secondary" disabled={selectedOrder.estado !== 'PENDIENTE' || saving === 'iniciar'} onClick={() => void withOperation('iniciar', () => labService.start(selectedOrder.id))}>Iniciar orden</button>
            <button className="secondary" disabled={!activeStage || saving === 'etapa'} onClick={() => void withOperation('etapa', () => labService.completeStage(selectedOrder.id, activeStage?.id ?? '', stageNotes || null))}>Completar etapa activa</button>
            <button className="secondary" disabled={selectedOrder.estado !== 'LISTA_ENTREGA' || saving === 'entregar'} onClick={() => void withOperation('entregar', () => labService.deliver(selectedOrder.id))}>Entregar orden</button>
            <label>Notas de etapa<textarea value={stageNotes} onChange={(event) => setStageNotes(event.target.value)} /></label>
          </div>
        </div> : <p className="muted">Selecciona una orden para visualizar etapas y acciones.</p>}
      </SectionPanel>

      <div className="module-grid two-columns">
        <SectionPanel title="Consumo de material" footer={<span className="muted compact">Requiere orden EN_PROCESO</span>}>
          <form className="crud-form" onSubmit={submitConsumption}>
            <label>Producto<select value={productId} onChange={(event) => setProductId(event.target.value)}><option value="">Selecciona producto</option>{productItems.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.nombre}</option>)}</select></label>
            <label>Cantidad<input type="number" min="0.01" step="0.01" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></label>
            <label>Observaciones<textarea value={consumptionNotes} onChange={(event) => setConsumptionNotes(event.target.value)} /></label>
            <button type="submit" disabled={!selectedOrder || selectedOrder.estado !== 'EN_PROCESO' || saving === 'consumo'}>{saving === 'consumo' ? 'Registrando…' : 'Registrar consumo'}</button>
          </form>
        </SectionPanel>

        <SectionPanel title="Control de calidad" footer={<span className="muted compact">Aprueba, rechaza o manda a retrabajo</span>}>
          <form className="crud-form" onSubmit={submitQuality}>
            <label>Resultado<select value={qcResult} onChange={(event) => setQcResult(event.target.value as ControlCalidadPayload['resultado'])}>{QC_RESULTS.map((result) => <option key={result}>{result}</option>)}</select></label>
            <label>Motivo rechazo/retrabajo<input value={qcReason} onChange={(event) => setQcReason(event.target.value)} /></label>
            <label>Observaciones<textarea value={qcNotes} onChange={(event) => setQcNotes(event.target.value)} /></label>
            <button type="submit" disabled={!selectedOrder || !['CONTROL_CALIDAD', 'EN_PROCESO'].includes(selectedOrder.estado) || saving === 'calidad'}>{saving === 'calidad' ? 'Registrando…' : 'Registrar calidad'}</button>
          </form>
        </SectionPanel>
      </div>

      <SectionPanel title="Historial de consumos y calidad">
        <div className="module-grid two-columns"><div className="table-wrap compact-table"><table><thead><tr><th>Producto</th><th>Cantidad</th><th>Costo</th><th>Obs.</th></tr></thead><tbody>{selectedOrder?.consumos?.map((item) => <tr key={item.id}><td className="compact-id">{item.producto_id}</td><td>{item.cantidad}</td><td>{item.costo_total}</td><td>{item.observaciones ?? '—'}</td></tr>)}</tbody></table></div><div className="table-wrap compact-table"><table><thead><tr><th>Resultado</th><th>Fecha</th><th>Motivo</th><th>Obs.</th></tr></thead><tbody>{selectedOrder?.controles_calidad?.map((item) => <tr key={item.id}><td><StatusBadge tone={item.resultado === 'APROBADO' ? 'success' : item.resultado === 'RECHAZADO' ? 'danger' : 'warning'}>{item.resultado}</StatusBadge></td><td>{dateTime(item.fecha)}</td><td>{item.motivo_rechazo ?? '—'}</td><td>{item.observaciones ?? '—'}</td></tr>)}</tbody></table></div></div>
      </SectionPanel>
    </section>
  );
}
