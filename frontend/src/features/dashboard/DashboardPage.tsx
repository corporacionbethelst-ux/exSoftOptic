import { Activity, Boxes, FlaskConical, ShoppingCart, Users } from 'lucide-react';
import { EmptyState } from '../../components/EmptyState';
import { InlineState } from '../../components/InlineState';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
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

  const productItems = products.data?.items ?? products.data?.productos ?? [];
  const salesItems = sales.data ?? [];
  const labItems = lab.data ?? [];
  const kardexItems = kardex.data ?? [];
  const userItems = users.data?.users ?? [];
  const salesTotal = salesItems.reduce((total, sale) => total + Number(sale.total ?? 0), 0);

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Inicio"
        title="Dashboard operativo"
        description="Resumen conectado a los endpoints del backend y al seed demo. Cada panel se carga de forma independiente."
        actions={<StatusBadge tone="success">Backend conectado</StatusBadge>}
      />

      <div className="metric-grid">
        <MetricCard label="Usuarios" value={users.loading ? '…' : users.data?.total ?? 0} hint={users.error ?? 'Equipo activo'} />
        <MetricCard label="Productos" value={products.loading ? '…' : productItems.length} hint={products.error ?? 'Catálogo demo'} />
        <MetricCard label="Ventas" value={sales.loading ? '…' : salesItems.length} hint={sales.error ?? money(salesTotal)} />
        <MetricCard label="Órdenes Lab" value={lab.loading ? '…' : labItems.length} hint={lab.error ?? 'En proceso'} />
      </div>

      <div className="panel-grid">
        <SectionPanel title={<><ShoppingCart size={18} /> Últimas ventas</>}>
          <InlineState loading={sales.loading} error={sales.error} empty={salesItems.length === 0} emptyTitle="Sin ventas" emptyDescription="Ejecuta make seed-demo para poblar ventas demo.">
            <div className="list-stack">
              {salesItems.slice(0, 5).map((sale) => (
                <div className="row-card" key={sale.id}>
                  <div><strong>{sale.folio}</strong><span>{sale.estado}</span></div>
                  <b>{money(sale.total)}</b>
                </div>
              ))}
            </div>
          </InlineState>
        </SectionPanel>

        <SectionPanel title={<><Boxes size={18} /> Productos guía</>}>
          <InlineState loading={products.loading} error={products.error} empty={productItems.length === 0} emptyTitle="Sin productos" emptyDescription="El catálogo demo todavía no tiene productos visibles.">
            <div className="list-stack">
              {productItems.slice(0, 5).map((product) => (
                <div className="row-card" key={product.id}>
                  <div><strong>{product.nombre}</strong><span>{product.sku}</span></div>
                  <b>{money(product.precio_venta)}</b>
                </div>
              ))}
            </div>
          </InlineState>
        </SectionPanel>

        <SectionPanel title={<><FlaskConical size={18} /> Laboratorio</>}>
          <InlineState loading={lab.loading} error={lab.error} empty={labItems.length === 0} emptyTitle="Sin órdenes" emptyDescription="Aún no hay órdenes de laboratorio para mostrar.">
            <div className="list-stack">
              {labItems.slice(0, 5).map((order) => (
                <div className="row-card" key={order.id}>
                  <div><strong>{order.folio}</strong><span>{order.prioridad}</span></div>
                  <StatusBadge tone={order.estado === 'EN_PROCESO' ? 'warning' : 'neutral'}>{order.estado}</StatusBadge>
                </div>
              ))}
            </div>
          </InlineState>
        </SectionPanel>

        <SectionPanel title={<><Activity size={18} /> Kardex reciente</>}>
          <InlineState loading={kardex.loading} error={kardex.error} empty={kardexItems.length === 0} emptyTitle="Sin movimientos" emptyDescription="El inventario todavía no tiene kardex reciente.">
            <div className="list-stack">
              {kardexItems.slice(0, 5).map((movement) => (
                <div className="row-card" key={movement.id}>
                  <div><strong>{movement.tipo_movimiento}</strong><span>{movement.origen}</span></div>
                  <b>{movement.cantidad}</b>
                </div>
              ))}
            </div>
          </InlineState>
        </SectionPanel>

        <SectionPanel className="wide" title={<><Users size={18} /> Usuarios</>}>
          <InlineState loading={users.loading} error={users.error} empty={userItems.length === 0} emptyTitle="Sin usuarios" emptyDescription="No hay usuarios visibles con los filtros actuales.">
            <div className="table-wrap">
              <table>
                <thead><tr><th>Usuario</th><th>Email</th><th>Estado</th></tr></thead>
                <tbody>{userItems.slice(0, 6).map((user) => <tr key={user.id}><td>{user.nombre_completo}</td><td>{user.email}</td><td><StatusBadge tone={user.esta_activo ? 'success' : 'danger'}>{user.esta_activo ? 'Activo' : 'Inactivo'}</StatusBadge></td></tr>)}</tbody>
              </table>
            </div>
          </InlineState>
        </SectionPanel>
      </div>

      {users.error || products.error || sales.error || lab.error || kardex.error ? (
        <EmptyState title="Hay paneles con errores" description="El dashboard continúa mostrando la información disponible; revisa el panel específico para ver qué endpoint falló." />
      ) : null}
    </section>
  );
}
