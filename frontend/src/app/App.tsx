import { AppBootScreen } from '../components/AppBootScreen';
import { LoginPage } from '../features/auth/LoginPage';
import { useAuth } from '../features/auth/AuthContext';
import { AppLayout } from '../layout/AppLayout';

export function App() {
  const { isAuthenticated, isBootstrapping } = useAuth();

  if (isBootstrapping) return <AppBootScreen />;

  return isAuthenticated ? <AppLayout /> : <LoginPage />;
}
