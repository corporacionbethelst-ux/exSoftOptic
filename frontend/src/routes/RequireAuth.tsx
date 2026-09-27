import { Navigate } from 'react-router-dom';
import { AppBootScreen } from '../components/AppBootScreen';
import { useAuth } from '../features/auth/authContext';
import { AppLayout } from '../layout/AppLayout';

export function RequireAuth() {
  const { isAuthenticated, isBootstrapping } = useAuth();
  if (isBootstrapping) return <AppBootScreen />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <AppLayout />;
}
