import type { NavigationItem, PageKey } from '../types/navigation';

type SidebarProps = {
  activePage: PageKey;
  items: NavigationItem[];
  open: boolean;
  onSelect: (page: PageKey) => void;
};

export function Sidebar({ activePage, items, open, onSelect }: SidebarProps) {
  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="sidebar-brand">
        <div className="brand-dot">EO</div>
        <div><strong>ExSoftOptic</strong><span>Óptica Demo</span></div>
      </div>
      <nav>
        {items.map((item) => (
          <button key={item.key} className={activePage === item.key ? 'active' : ''} onClick={() => onSelect(item.key)}>
            {item.icon}{item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
