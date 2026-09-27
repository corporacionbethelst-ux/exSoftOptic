import { Navigate, createBrowserRouter } from 'react-router-dom';
import { LoginPage } from '../features/auth/LoginPage';
import { RequireAuth, RequireModule } from './RequireAuth';
import { AdminPage } from '../features/admin/AdminPage';
import { BillingPage } from '../features/billing/BillingPage';
import { CrmPage } from '../features/crm/CrmPage';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { FinancePage } from '../features/finance/FinancePage';
import { InventoryPage } from '../features/inventory/InventoryPage';
import { LabPage } from '../features/lab/LabPage';
import { LabOrderDetailPage } from '../features/lab/LabOrderDetailPage';
import { OperationsPage } from '../features/operations/OperationsPage';
import { PatientDetailPage } from '../features/patients/PatientDetailPage';
import { PatientsPage } from '../features/patients/PatientsPage';
import { ProductsPage } from '../features/catalog/ProductsPage';
import { PurchasesPage } from '../features/purchases/PurchasesPage';
import { ReportsPage } from '../features/reports/ReportsPage';
import { SaleDetailPage } from '../features/sales/SaleDetailPage';
import { SalesPage } from '../features/sales/SalesPage';
import { UsersPage } from '../features/users/UsersPage';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <RequireAuth />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'dashboard', element: <RequireModule module="dashboard"><DashboardPage /></RequireModule> },
      { path: 'users', element: <RequireModule module="users"><UsersPage /></RequireModule> },
      { path: 'products', element: <RequireModule module="products"><ProductsPage /></RequireModule> },
      { path: 'inventory', element: <RequireModule module="inventory"><InventoryPage /></RequireModule> },
      { path: 'sales', element: <RequireModule module="sales"><SalesPage /></RequireModule> },
      { path: 'sales/:saleId', element: <RequireModule module="sales"><SaleDetailPage /></RequireModule> },
      { path: 'purchases', element: <RequireModule module="purchases"><PurchasesPage /></RequireModule> },
      { path: 'crm', element: <RequireModule module="crm"><CrmPage /></RequireModule> },
      { path: 'patients', element: <RequireModule module="patients"><PatientsPage /></RequireModule> },
      { path: 'patients/:patientId', element: <RequireModule module="patients"><PatientDetailPage /></RequireModule> },
      { path: 'lab', element: <RequireModule module="lab"><LabPage /></RequireModule> },
      { path: 'lab/:orderId', element: <RequireModule module="lab"><LabOrderDetailPage /></RequireModule> },
      { path: 'finance', element: <RequireModule module="finance"><FinancePage /></RequireModule> },
      { path: 'billing', element: <RequireModule module="billing"><BillingPage /></RequireModule> },
      { path: 'reports', element: <RequireModule module="reports"><ReportsPage /></RequireModule> },
      { path: 'operations', element: <RequireModule module="operations"><OperationsPage /></RequireModule> },
      { path: 'admin', element: <RequireModule module="admin"><AdminPage /></RequireModule> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);
