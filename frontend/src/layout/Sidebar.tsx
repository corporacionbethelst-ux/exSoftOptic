import { NavLink } from 'react-router-dom';
import type { NavigationItem } from '../types/navigation';

type SidebarProps = {
  activePath: string;
  items: NavigationItem[];
  open: boolean;
  onNavigate: () => void;
};

function isActivePath(activePath: string, key: string) {
  if (key === 'dashboard') return activePath === '/' || activePath === '/dashboard';
  return activePath === `/${key}` || activePath.startsWith(`/${key}/`);
}

export function Sidebar({ activePath, items, open, onNavigate }: SidebarProps) {
  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="sidebar-brand">
        <div className="brand-dot">EO</div>
        <div><strong>ExSoftOptic</strong><span>Óptica Demo</span></div>
      </div>
      <nav>
        {items.map((item) => (
          <NavLink
            key={item.key}
            to={item.key === 'dashboard' ? '/' : `/${item.key}`}
            className={isActivePath(activePath, item.key) ? 'active' : ''}
            onClick={onNavigate}
          >
            {item.icon}{item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
