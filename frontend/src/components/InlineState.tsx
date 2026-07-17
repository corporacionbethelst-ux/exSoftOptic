import type { ReactNode } from 'react';

type InlineStateProps = {
  loading: boolean;
  error?: string | null;
  empty?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  children: ReactNode;
};

export function InlineState({ loading, error, empty, emptyTitle = 'Sin información', emptyDescription, children }: InlineStateProps) {
  if (loading) return <div className="inline-state muted">Cargando…</div>;
  if (error) return <div className="inline-state error">{error}</div>;
  if (empty) {
    return (
      <div className="empty-state">
        <strong>{emptyTitle}</strong>
        {emptyDescription ? <span>{emptyDescription}</span> : null}
      </div>
    );
  }
  return <>{children}</>;
}
