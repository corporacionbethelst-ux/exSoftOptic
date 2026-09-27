import type { Usuario } from '../types/auth';

/**
 * Semántica idéntica al backend (app/api/deps.py::require_permissions):
 * - "*" otorga todos los permisos.
 * - "modulo.*" otorga cualquier permiso del módulo (prefijo antes del primer punto).
 * - SUPER_ADMIN / ADMIN_SUCURSAL tienen acceso total (igual que el backend).
 */
const FULL_ACCESS_ROLES = ['SUPER_ADMIN', 'ADMIN_SUCURSAL'];

export function hasPermission(user: Usuario | null, permission: string): boolean {
  if (!user) return false;
  const rolNombre = user.rol?.nombre ?? '';
  if (FULL_ACCESS_ROLES.includes(rolNombre)) return true;
  const perms = user.rol?.permisos ?? [];
  if (perms.includes('*')) return true;
  if (perms.includes(permission)) return true;
  const modulo = permission.split('.')[0];
  return perms.includes(`${modulo}.*`);
}

export function hasAnyPermission(user: Usuario | null, permissions: string[]): boolean {
  return permissions.some((permission) => hasPermission(user, permission));
}
