import { DataState } from '../../components/DataState';
import { StatusBadge } from '../../components/StatusBadge';
import { labService } from '../../services';
import { dateTime } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

export function LabPage() {
  const orders = useApiResource(labService.orders);
  return (
    <section className="page-stack">
      <div className="page-header"><div><p className="eyebrow">Laboratorio</p><h1>Órdenes</h1><p className="muted">Seguimiento de trabajos y etapas del laboratorio óptico.</p></div></div>
      <DataState loading={orders.loading} error={orders.error}>
        <div className="panel table-wrap"><table><thead><tr><th>Folio</th><th>Prioridad</th><th>Prometida</th><th>Etapas</th><th>Estado</th></tr></thead><tbody>{(orders.data ?? []).map((order) => <tr key={order.id}><td>{order.folio}</td><td>{order.prioridad}</td><td>{dateTime(order.fecha_prometida)}</td><td>{order.etapas?.length ?? 0}</td><td><StatusBadge tone={order.estado === 'EN_PROCESO' ? 'warning' : 'neutral'}>{order.estado}</StatusBadge></td></tr>)}</tbody></table></div>
      </DataState>
    </section>
  );
}
