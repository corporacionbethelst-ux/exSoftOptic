import { useCallback, useEffect, useState } from 'react';
import { ApiError } from '../services';

export function useApiResource<T>(loader: () => Promise<T>, enabled = true) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await loader());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudieron cargar los datos');
    } finally {
      setLoading(false);
    }
  }, [loader]);

  useEffect(() => {
    if (!enabled) return;
    queueMicrotask(() => {
      void load();
    });
  }, [enabled, load]);

  return { data, loading, error, reload: load };
}
