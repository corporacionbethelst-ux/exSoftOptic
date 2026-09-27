import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '../layout/AppLayout';
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
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'users', element: <UsersPage /> },
      { path: 'products', element: <ProductsPage /> },
      { path: 'inventory', element: <InventoryPage /> },
      { path: 'sales', element: <SalesPage /> },
      { path: 'sales/:saleId', element: <SaleDetailPage /> },
      { path: 'purchases', element: <PurchasesPage /> },
      { path: 'crm', element: <CrmPage /> },
      { path: 'patients', element: <PatientsPage /> },
      { path: 'patients/:patientId', element: <PatientDetailPage /> },
      { path: 'lab', element: <LabPage /> },
      { path: 'lab/:orderId', element: <LabOrderDetailPage /> },
      { path: 'finance', element: <FinancePage /> },
      { path: 'billing', element: <BillingPage /> },
      { path: 'reports', element: <ReportsPage /> },
      { path: 'operations', element: <OperationsPage /> },
      { path: 'admin', element: <AdminPage /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);
