import { Boxes, CalendarDays, ClipboardList, FlaskConical, LayoutDashboard, PackageSearch, ShoppingCart, Users } from 'lucide-react';
import type { NavigationItem } from '../types/navigation';

export const navigationItems: NavigationItem[] = [
  { key: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18} /> },
  { key: 'users', label: 'Usuarios', icon: <Users size={18} /> },
  { key: 'products', label: 'Productos', icon: <Boxes size={18} /> },
  { key: 'inventory', label: 'Inventario', icon: <PackageSearch size={18} /> },
  { key: 'sales', label: 'Ventas', icon: <ShoppingCart size={18} /> },
  { key: 'purchases', label: 'Compras', icon: <ClipboardList size={18} /> },
  { key: 'crm', label: 'CRM', icon: <CalendarDays size={18} /> },
  { key: 'lab', label: 'Laboratorio', icon: <FlaskConical size={18} /> },
];
