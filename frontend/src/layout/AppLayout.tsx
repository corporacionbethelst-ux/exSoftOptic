import { useState } from 'react';
import { navigationItems } from '../routes/navigation';
import { renderPage } from '../routes/renderPage';
import type { PageKey } from '../types/navigation';
import { useAuth } from '../features/auth/authContext';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppLayout() {
  const { user, logout } = useAuth();
  const [activePage, setActivePage] = useState<PageKey>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  function selectPage(page: PageKey) {
    setActivePage(page);
    setSidebarOpen(false);
  }

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} items={navigationItems} open={sidebarOpen} onSelect={selectPage} />
      <div className="content-shell">
        <Topbar user={user} onMenuClick={() => setSidebarOpen((value) => !value)} onLogout={logout} />
        <main className="main-content">{renderPage(activePage)}</main>
      </div>
    </div>
  );
}
