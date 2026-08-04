import { LogOut, Menu } from 'lucide-react';
import type { Usuario } from '../types/auth';

type TopbarProps = {
  user: Usuario | null;
  onMenuClick: () => void;
  onLogout: () => Promise<void>;
};

export function Topbar({ user, onMenuClick, onLogout }: TopbarProps) {
  return (
    <header className="topbar">
      <button className="icon-button mobile-only" onClick={onMenuClick}><Menu size={20} /></button>
      <div><strong>{user?.nombre_completo}</strong><span>{user?.email}</span></div>
      <button className="secondary-button" onClick={() => void onLogout()}><LogOut size={16} /> Salir</button>
    </header>
  );
}
