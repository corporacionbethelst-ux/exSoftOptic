import { FlaskConical } from 'lucide-react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { labService } from '../../services';
import { dateTime } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

export function LabPage() {
  const orders = useApiResource(labService.orders);
  const orderItems = orders.data ?? [];

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Laboratorio"
        title="Órdenes"
        description="Seguimiento de trabajos, prioridades y etapas del laboratorio óptico."
      />
      <SectionPanel title={<><FlaskConical size={18} /> Trabajos activos</>} className="wide">
        <InlineState loading={orders.loading} error={orders.error} empty={orderItems.length === 0} emptyTitle="Sin órdenes de laboratorio" emptyDescription="Crea una venta confirmada con receta o ejecuta el seed demo para visualizar órdenes.">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Folio</th><th>Prioridad</th><th>Prometida</th><th>Etapas</th><th>Estado</th></tr></thead>
              <tbody>
                {orderItems.map((order) => (
                  <tr key={order.id}>
                    <td>{order.folio}</td>
                    <td>{order.prioridad}</td>
                    <td>{dateTime(order.fecha_prometida)}</td>
                    <td>{order.etapas?.length ?? 0}</td>
                    <td><StatusBadge tone={order.estado === 'EN_PROCESO' ? 'warning' : 'neutral'}>{order.estado}</StatusBadge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </InlineState>
      </SectionPanel>
    </section>
  );
}
