import { RouterProvider } from 'react-router-dom';
import { AuthProvider } from '../features/auth/AuthContext';
import { router } from '../routes/router';

export function AppProviders() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
}
