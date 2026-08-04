import type { ReactNode } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import type { LoginResponse } from '../../types/auth';
import { authService } from '../../services';
import { clearStoredTokens, getStoredTokens, storeTokens } from '../../services/storage/tokenStorage';
import { AuthContext } from './authContext';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<LoginResponse | null>(() => getStoredTokens());
  const [isBootstrapping, setIsBootstrapping] = useState(() => Boolean(getStoredTokens()?.access_token));

  useEffect(() => {
    let mounted = true;
    const storedSession = getStoredTokens();

    if (!storedSession?.access_token) {
      queueMicrotask(() => {
        if (mounted) setIsBootstrapping(false);
      });
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

  useEffect(() => {
    const expireSession = () => setSession(null);
    globalThis.addEventListener('exsoftoptic:auth-expired', expireSession);
    return () => globalThis.removeEventListener('exsoftoptic:auth-expired', expireSession);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const response = await authService.login({ username, password });
    storeTokens(response);
    setSession(response);
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      clearStoredTokens();
      setSession(null);
    }
  }, []);

  const value = useMemo(
    () => ({ user: session?.user ?? null, isAuthenticated: Boolean(session?.access_token), isBootstrapping, login, logout }),
    [isBootstrapping, login, logout, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
