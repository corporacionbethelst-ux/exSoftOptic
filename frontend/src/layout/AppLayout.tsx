import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { navigationItems } from '../routes/navigation';
import { useAuth } from '../features/auth/authContext';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppLayout() {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { pathname } = useLocation();

  return (
    <div className="app-shell">
      <Sidebar activePath={pathname} items={navigationItems} open={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />
      <div className="content-shell">
        <Topbar user={user} onMenuClick={() => setSidebarOpen((value) => !value)} onLogout={logout} />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
