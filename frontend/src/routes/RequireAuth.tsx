import { Navigate } from 'react-router-dom';
import { AppBootScreen } from '../components/AppBootScreen';
import { useAuth } from '../features/auth/authContext';
import { hasAnyPermission } from '../lib/permissions';
import { moduleReadPermissions } from '../lib/modulePermissions';
import { AppLayout } from '../layout/AppLayout';
import type { PageKey } from '../types/navigation';

export function RequireAuth() {
  const { isAuthenticated, isBootstrapping } = useAuth();
  if (isBootstrapping) return <AppBootScreen />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <AppLayout />;
}

/** Redirige al dashboard si el rol del usuario no tiene permiso de lectura del módulo. */
export function RequireModule({ module, children }: { module: PageKey; children: React.ReactNode }) {
  const { user } = useAuth();
  const required = moduleReadPermissions[module];
  if (required.length > 0 && !hasAnyPermission(user, required)) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}
