import { LoginPage } from '../features/auth/LoginPage';
import { useAuth } from '../features/auth/AuthContext';
import { AppLayout } from '../layout/AppLayout';

export function App() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <AppLayout /> : <LoginPage />;
}
