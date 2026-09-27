import { useMemo, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { navigationItems } from '../routes/navigation';
import { moduleReadPermissions } from '../lib/modulePermissions';
import { hasAnyPermission } from '../lib/permissions';
import { useAuth } from '../features/auth/authContext';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppLayout() {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { pathname } = useLocation();
  const visibleItems = useMemo(
    () => navigationItems.filter((item) => {
      const required = moduleReadPermissions[item.key];
      return required.length === 0 || hasAnyPermission(user, required);
    }),
    [user],
  );

  return (
    <div className="app-shell">
      <Sidebar activePath={pathname} items={visibleItems} open={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />
      <div className="content-shell">
        <Topbar user={user} onMenuClick={() => setSidebarOpen((value) => !value)} onLogout={logout} />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
