import { ArrowLeft } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { salesService } from '../../services';
import { useApiResource } from '../../hooks/useApiResource';
import { dateTime, money } from '../../utils/format';

function saleTone(estado: string): 'success' | 'warning' | 'danger' | 'neutral' {
  if (estado === 'CONFIRMADA') return 'success';
  if (estado === 'BORRADOR') return 'warning';
  if (estado === 'DEVUELTA' || estado === 'ANULADA') return 'danger';
  return 'neutral';
}

export function SaleDetailPage() {
  const { saleId = '' } = useParams();
  const loadSale = () => salesService.get(saleId);
  const sale = useApiResource(loadSale, Boolean(saleId));
  const data = sale.data;

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Ventas"
        title={data ? `Venta ${data.folio}` : 'Detalle de venta'}
        description="Consulta el ticket completo: líneas, pagos y vínculo con el expediente clínico."
        actions={<Link to="/sales" className="secondary-button"><ArrowLeft size={16} /> Volver a ventas</Link>}
      />

      <InlineState loading={sale.loading} error={sale.error} empty={!data} emptyTitle="Venta no encontrada">
        {data ? (
          <>
            <div className="metric-grid">
              <div className="metric-card"><span className="muted">Estado</span><strong><StatusBadge tone={saleTone(data.estado)}>{data.estado}</StatusBadge></strong></div>
              <div className="metric-card"><span className="muted">Total</span><strong>{money(data.total)}</strong></div>
              <div className="metric-card"><span className="muted">Expediente clínico</span><strong>{data.paciente_id ? `Paciente vinculado${data.receta_id ? ' · Receta ✓' : ' · sin receta'}` : 'Venta de mostrador'}</strong></div>
              <div className="metric-card"><span className="muted">Fecha</span><strong>{dateTime(data.fecha ?? data.created_at)}</strong></div>
            </div>

            <SectionPanel title="Líneas de la venta">
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Producto</th><th>Cantidad</th><th>Precio unitario</th><th>Descuento</th><th>Importe</th></tr></thead>
                  <tbody>
                    {(data.lineas ?? []).map((line) => (
                      <tr key={line.id}>
                        <td>{line.descripcion}</td>
                        <td>{line.cantidad}</td>
                        <td>{money(line.precio_unitario)}</td>
                        <td>{money(line.descuento)}</td>
                        <td>{money(line.importe)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </SectionPanel>

            <SectionPanel title="Pagos">
              {(data.pagos?.length ?? 0) === 0 ? <p className="muted">Sin pagos registrados (venta en borrador).</p> : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Método</th><th>Monto</th><th>Referencia</th><th>Fecha</th></tr></thead>
                    <tbody>
                      {(data.pagos ?? []).map((pago) => (
                        <tr key={pago.id}>
                          <td>{pago.metodo_pago}</td>
                          <td>{money(pago.monto)}</td>
                          <td>{pago.referencia ?? '—'}</td>
                          <td>{dateTime(pago.fecha)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </SectionPanel>

            {data.paciente_id ? (
              <p className="muted compact">
                ¿Necesitas el historial clínico?{' '}
                <Link to={`/patients/${data.paciente_id}`}>Ver expediente del paciente</Link>
              </p>
            ) : null}
          </>
        ) : null}
      </InlineState>
    </section>
  );
}
