export function DataState({ loading, error, children }: { loading: boolean; error?: string | null; children: React.ReactNode }) {
  if (loading) return <div className="panel placeholder">Cargando datos…</div>;
  if (error) return <div className="panel alert error">{error}</div>;
  return <>{children}</>;
}
