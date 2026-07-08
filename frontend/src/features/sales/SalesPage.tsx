import { DataState } from '../../components/DataState';
import { StatusBadge } from '../../components/StatusBadge';
import { salesService } from '../../services';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

export function SalesPage() {
  const sales = useApiResource(salesService.list);
  return (
    <section className="page-stack">
      <div className="page-header"><div><p className="eyebrow">Operación</p><h1>Ventas</h1><p className="muted">Ventas confirmadas y borradores creados en backend.</p></div></div>
      <DataState loading={sales.loading} error={sales.error}>
        <div className="panel table-wrap"><table><thead><tr><th>Folio</th><th>Estado</th><th>Líneas</th><th>Total</th></tr></thead><tbody>{(sales.data ?? []).map((sale) => <tr key={sale.id}><td>{sale.folio}</td><td><StatusBadge tone={sale.estado === 'CONFIRMADA' ? 'success' : 'warning'}>{sale.estado}</StatusBadge></td><td>{sale.lineas?.length ?? 0}</td><td>{money(sale.total)}</td></tr>)}</tbody></table></div>
      </DataState>
    </section>
  );
}
