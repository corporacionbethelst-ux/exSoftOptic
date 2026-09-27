import { LogOut, Menu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { Usuario } from '../types/auth';

type TopbarProps = {
  user: Usuario | null;
  onMenuClick: () => void;
  onLogout: () => Promise<void>;
};

export function Topbar({ user, onMenuClick, onLogout }: TopbarProps) {
  const navigate = useNavigate();
  const handleLogout = async () => {
    await onLogout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="topbar">
      <button className="icon-button mobile-only" onClick={onMenuClick}><Menu size={20} /></button>
      <div><strong>{user?.nombre_completo}</strong><span>{user?.email}{user?.rol?.nombre ? ` · ${user.rol.nombre}` : ''}</span></div>
      <button className="secondary-button" onClick={() => void handleLogout()}><LogOut size={16} /> Salir</button>
    </header>
  );
}
