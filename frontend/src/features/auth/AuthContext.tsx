import type { ReactNode } from 'react';
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { LoginResponse, Usuario } from '../../types/auth';
import { authService } from '../../services';
import { clearStoredTokens, getStoredTokens, storeTokens } from '../../services/storage/tokenStorage';

type AuthContextValue = {
  user: Usuario | null;
  isAuthenticated: boolean;
  isBootstrapping: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<LoginResponse | null>(() => getStoredTokens());
  const [isBootstrapping, setIsBootstrapping] = useState(() => Boolean(getStoredTokens()?.access_token));

  useEffect(() => {
    let mounted = true;
    const storedSession = getStoredTokens();

    if (!storedSession?.access_token) {
      setIsBootstrapping(false);
      return;
    }

    authService
      .me()
      .then((user) => {
        if (!mounted) return;
        const hydratedSession = { ...storedSession, user };
        storeTokens(hydratedSession);
        setSession(hydratedSession);
      })
      .catch(() => {
        clearStoredTokens();
        if (mounted) setSession(null);
      })
      .finally(() => {
        if (mounted) setIsBootstrapping(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const response = await authService.login({ username, password });
    storeTokens(response);
    setSession(response);
  }, []);

  const logout = useCallback(() => {
    clearStoredTokens();
    setSession(null);
  }, []);

  const value = useMemo(
    () => ({ user: session?.user ?? null, isAuthenticated: Boolean(session?.access_token), isBootstrapping, login, logout }),
    [isBootstrapping, login, logout, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return value;
}
