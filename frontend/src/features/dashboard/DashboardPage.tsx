import { Activity, Boxes, FlaskConical, ShoppingCart, Users } from 'lucide-react';
import { DataState } from '../../components/DataState';
import { MetricCard } from '../../components/MetricCard';
import { StatusBadge } from '../../components/StatusBadge';
import { catalogService, inventoryService, labService, salesService, usersService } from '../../services';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

export function DashboardPage() {
  const users = useApiResource(usersService.list);
  const products = useApiResource(catalogService.products);
  const sales = useApiResource(salesService.list);
  const lab = useApiResource(labService.orders);
  const kardex = useApiResource(inventoryService.kardex);
  const isLoading = users.loading || products.loading || sales.loading || lab.loading || kardex.loading;
  const error = users.error ?? products.error ?? sales.error ?? lab.error ?? kardex.error;
  const productItems = products.data?.items ?? products.data?.productos ?? [];
  const salesTotal = (sales.data ?? []).reduce((total, sale) => total + Number(sale.total ?? 0), 0);

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Inicio</p>
          <h1>Dashboard operativo</h1>
          <p className="muted">Resumen conectado a los endpoints del backend y al seed demo.</p>
        </div>
        <StatusBadge tone="success">Backend conectado</StatusBadge>
      </div>
      <DataState loading={isLoading} error={error}>
        <div className="metric-grid">
          <MetricCard label="Usuarios" value={users.data?.total ?? 0} hint="Equipo activo" />
          <MetricCard label="Productos" value={productItems.length} hint="Catálogo demo" />
          <MetricCard label="Ventas" value={sales.data?.length ?? 0} hint={money(salesTotal)} />
          <MetricCard label="Órdenes Lab" value={lab.data?.length ?? 0} hint="En proceso" />
        </div>
        <div className="panel-grid">
          <article className="panel">
            <h2><ShoppingCart size={18} /> Últimas ventas</h2>
            <div className="list-stack">
              {(sales.data ?? []).slice(0, 5).map((sale) => (
                <div className="row-card" key={sale.id}>
                  <div><strong>{sale.folio}</strong><span>{sale.estado}</span></div>
                  <b>{money(sale.total)}</b>
                </div>
              ))}
            </div>
          </article>
          <article className="panel">
            <h2><Boxes size={18} /> Productos guía</h2>
            <div className="list-stack">
              {productItems.slice(0, 5).map((product) => (
                <div className="row-card" key={product.id}>
                  <div><strong>{product.nombre}</strong><span>{product.sku}</span></div>
                  <b>{money(product.precio_venta)}</b>
                </div>
              ))}
            </div>
          </article>
          <article className="panel">
            <h2><FlaskConical size={18} /> Laboratorio</h2>
            <div className="list-stack">
              {(lab.data ?? []).slice(0, 5).map((order) => (
                <div className="row-card" key={order.id}>
                  <div><strong>{order.folio}</strong><span>{order.prioridad}</span></div>
                  <StatusBadge tone={order.estado === 'EN_PROCESO' ? 'warning' : 'neutral'}>{order.estado}</StatusBadge>
                </div>
              ))}
            </div>
          </article>
          <article className="panel">
            <h2><Activity size={18} /> Kardex reciente</h2>
            <div className="list-stack">
              {(kardex.data ?? []).slice(0, 5).map((movement) => (
                <div className="row-card" key={movement.id}>
                  <div><strong>{movement.tipo_movimiento}</strong><span>{movement.origen}</span></div>
                  <b>{movement.cantidad}</b>
                </div>
              ))}
            </div>
          </article>
          <article className="panel wide">
            <h2><Users size={18} /> Usuarios</h2>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Usuario</th><th>Email</th><th>Estado</th></tr></thead>
                <tbody>{(users.data?.users ?? []).slice(0, 6).map((user) => <tr key={user.id}><td>{user.nombre_completo}</td><td>{user.email}</td><td><StatusBadge tone={user.esta_activo ? 'success' : 'danger'}>{user.esta_activo ? 'Activo' : 'Inactivo'}</StatusBadge></td></tr>)}</tbody>
              </table>
            </div>
          </article>
        </div>
      </DataState>
    </section>
  );
}
