import type { ReactNode } from 'react';
import { Boxes, FlaskConical, LayoutDashboard, LogOut, Menu, ShoppingCart, Users } from 'lucide-react';
import { useMemo, useState } from 'react';
import { ProductsPage } from '../features/catalog/ProductsPage';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { LabPage } from '../features/lab/LabPage';
import { SalesPage } from '../features/sales/SalesPage';
import { UsersPage } from '../features/users/UsersPage';
import { useAuth } from '../features/auth/AuthContext';
import { LoginPage } from '../features/auth/LoginPage';

type PageKey = 'dashboard' | 'users' | 'products' | 'sales' | 'lab';

const navItems: Array<{ key: PageKey; label: string; icon: ReactNode }> = [
  { key: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18} /> },
  { key: 'users', label: 'Usuarios', icon: <Users size={18} /> },
  { key: 'products', label: 'Productos', icon: <Boxes size={18} /> },
  { key: 'sales', label: 'Ventas', icon: <ShoppingCart size={18} /> },
  { key: 'lab', label: 'Laboratorio', icon: <FlaskConical size={18} /> },
];

export function App() {
  const { isAuthenticated, user, logout } = useAuth();
  const [activePage, setActivePage] = useState<PageKey>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const page = useMemo(() => {
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
  }, [activePage]);

  if (!isAuthenticated) return <LoginPage />;

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-dot">EO</div>
          <div><strong>ExSoftOptic</strong><span>Óptica Demo</span></div>
        </div>
        <nav>
          {navItems.map((item) => (
            <button key={item.key} className={activePage === item.key ? 'active' : ''} onClick={() => { setActivePage(item.key); setSidebarOpen(false); }}>
              {item.icon}{item.label}
            </button>
          ))}
        </nav>
      </aside>
      <div className="content-shell">
        <header className="topbar">
          <button className="icon-button mobile-only" onClick={() => setSidebarOpen((value) => !value)}><Menu size={20} /></button>
          <div><strong>{user?.nombre_completo}</strong><span>{user?.email}</span></div>
          <button className="secondary-button" onClick={logout}><LogOut size={16} /> Salir</button>
        </header>
        <main className="main-content">{page}</main>
      </div>
    </div>
  );
}
