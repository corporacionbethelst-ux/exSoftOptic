import type { ReactNode } from 'react';
import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { api, clearStoredTokens, getStoredTokens, LoginResponse, storeTokens, Usuario } from '../../lib/api';

type AuthContextValue = {
  user: Usuario | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<LoginResponse | null>(() => getStoredTokens());

  const login = useCallback(async (username: string, password: string) => {
    const response = await api.login({ username, password });
    storeTokens(response);
    setSession(response);
  }, []);

  const logout = useCallback(() => {
    clearStoredTokens();
    setSession(null);
  }, []);

  const value = useMemo(
    () => ({ user: session?.user ?? null, isAuthenticated: Boolean(session?.access_token), login, logout }),
    [login, logout, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return value;
}
