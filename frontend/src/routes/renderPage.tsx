import { ProductsPage } from '../features/catalog/ProductsPage';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { LabPage } from '../features/lab/LabPage';
import { SalesPage } from '../features/sales/SalesPage';
import { UsersPage } from '../features/users/UsersPage';
import type { PageKey } from '../types/navigation';

export function renderPage(activePage: PageKey) {
  switch (activePage) {
    case 'users':
      return <UsersPage />;
    case 'products':
      return <ProductsPage />;
    case 'sales':
      return <SalesPage />;
    case 'lab':
      return <LabPage />;
    default:
      return <DashboardPage />;
  }
}
