import { ProductsPage } from '../features/catalog/ProductsPage';
import { PurchasesPage } from '../features/purchases/PurchasesPage';
import { BillingPage } from '../features/billing/BillingPage';
import { CrmPage } from '../features/crm/CrmPage';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { FinancePage } from '../features/finance/FinancePage';
import { InventoryPage } from '../features/inventory/InventoryPage';
import { LabPage } from '../features/lab/LabPage';
import { PatientsPage } from '../features/patients/PatientsPage';
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
    case 'patients':
      return <PatientsPage />;
    case 'lab':
      return <LabPage />;
    case 'finance':
      return <FinancePage />;
    case 'billing':
      return <BillingPage />;
    default:
      return <DashboardPage />;
  }
}
