import { ArrowLeft } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { labService } from '../../services';
import { useApiResource } from '../../hooks/useApiResource';
import { dateTime } from '../../utils/format';

const LAB_STAGES = ['RECEPCION', 'ESCUEPLIDO', 'PULIDO', 'TEÑIDO', 'MONTAJE', 'CONTROL_CALIDAD'] as const;

function stageStatus(orderState: string, index: number) {
  const order = LAB_STAGES.indexOf(orderState as (typeof LAB_STAGES)[number]);
  if (orderState === 'ENTREGADA' || orderState === 'LISTA_ENTREGA') return 'COMPLETADA';
  if (orderState === 'CANCELADA' || orderState === 'RECHAZADA') return 'CANCELADA';
  if (index < order) return 'COMPLETADA';
  if (index === order) return 'EN_PROCESO';
  return 'PENDIENTE';
}

function tone(status: string): 'success' | 'warning' | 'danger' | 'neutral' {
  if (status === 'ENTREGADA' || status === 'LISTA_ENTREGA') return 'success';
  if (status === 'RECHAZADA' || status === 'CANCELADA') return 'danger';
  if (['EN_PROCESO', 'CONTROL_CALIDAD', 'PENDIENTE'].includes(status)) return 'warning';
  return 'neutral';
}

export function LabOrderDetailPage() {
  const { orderId = '' } = useParams();
  const loadOrder = () => labService.order(orderId);
  const order = useApiResource(loadOrder, Boolean(orderId));
  const data = order.data;

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Laboratorio"
        title={data ? `Orden ${data.folio}` : 'Detalle de orden'}
        description="Seguimiento de la orden: etapas del proceso óptico, consumos de material y controles de calidad."
        actions={<Link to="/lab" className="secondary-button"><ArrowLeft size={16} /> Volver a laboratorio</Link>}
      />

      <InlineState loading={order.loading} error={order.error} empty={!data} emptyTitle="Orden no encontrada">
        {data ? (
          <>
            <div className="metric-grid">
              <div className="metric-card"><span className="muted">Estado</span><strong><StatusBadge tone={tone(data.estado)}>{data.estado}</StatusBadge></strong></div>
              <div className="metric-card"><span className="muted">Prioridad</span><strong>{data.prioridad}</strong></div>
              <div className="metric-card"><span className="muted">Fecha prometida</span><strong>{dateTime(data.fecha_prometida)}</strong></div>
              <div className="metric-card"><span className="muted">Entrega</span><strong>{data.fecha_entrega ? dateTime(data.fecha_entrega) : 'Pendiente'}</strong></div>
            </div>

            <SectionPanel title="Progreso por etapa" description="Vista estimada según el estado actual de la orden.">
              <div className="status-timeline">
                {(data.etapas?.length ? data.etapas : LAB_STAGES.map((etapa, index) => ({ id: `est-${etapa}`, etapa, estado: stageStatus(data.estado, index) }))).map((stage) => (
                  <div key={stage.id} className={`timeline-step ${stage.estado.toLowerCase()}`}>
                    <strong>{stage.etapa}</strong>
                    <span>{stage.estado}</span>
                    <small>{stage.fecha_inicio ? `Inicio: ${dateTime(stage.fecha_inicio)}` : ''}</small>
                    <small>{stage.fecha_fin ? `Fin: ${dateTime(stage.fecha_fin)}` : stage.observaciones ?? ''}</small>
                  </div>
                ))}
              </div>
            </SectionPanel>

            <div className="panel-grid">
              <SectionPanel title="Consumos de material">
                {(data.consumos?.length ?? 0) === 0 ? <p className="muted">Sin consumos registrados.</p> : (
                  <div className="table-wrap">
                    <table>
                      <thead><tr><th>Producto</th><th>Cantidad</th><th>Costo total</th></tr></thead>
                      <tbody>
                        {(data.consumos ?? []).map((item) => (
                          <tr key={item.id}><td>{item.producto_id}</td><td>{item.cantidad}</td><td>{item.costo_total}</td></tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </SectionPanel>

              <SectionPanel title="Controles de calidad">
                {(data.controles_calidad?.length ?? 0) === 0 ? <p className="muted">Sin controles registrados.</p> : (
                  <div className="table-wrap">
                    <table>
                      <thead><tr><th>Resultado</th><th>Motivo</th><th>Fecha</th></tr></thead>
                      <tbody>
                        {(data.controles_calidad ?? []).map((qc) => (
                          <tr key={qc.id}>
                            <td><StatusBadge tone={qc.resultado === 'APROBADO' ? 'success' : qc.resultado === 'RETRABAJO' ? 'warning' : 'danger'}>{qc.resultado}</StatusBadge></td>
                            <td className="compact">{qc.motivo_rechazo ?? qc.observaciones ?? '—'}</td>
                            <td>{dateTime(qc.fecha)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </SectionPanel>
            </div>

            {data.venta_id ? (
              <p className="muted compact">¿Necesitas el ticket origen? <Link to={`/sales/${data.venta_id}`}>Ver venta vinculada</Link></p>
            ) : null}
          </>
        ) : null}
      </InlineState>
    </section>
  );
}
