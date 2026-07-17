import { ProductsPage } from '../features/catalog/ProductsPage';
import { PurchasesPage } from '../features/purchases/PurchasesPage';
import { CrmPage } from '../features/crm/CrmPage';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { InventoryPage } from '../features/inventory/InventoryPage';
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
    case 'inventory':
      return <InventoryPage />;
    case 'sales':
      return <SalesPage />;
    case 'purchases':
      return <PurchasesPage />;
    case 'crm':
      return <CrmPage />;
    case 'lab':
      return <LabPage />;
    default:
      return <DashboardPage />;
  }
}
