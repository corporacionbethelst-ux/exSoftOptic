import type { ReactNode } from 'react';

export type AlertLevel = 'success' | 'warning' | 'danger' | 'neutral';

export type AlertEntry = {
  id: string;
  level: AlertLevel;
  title: ReactNode;
  description?: ReactNode;
  meta?: ReactNode;
};

type AlertListProps = {
  items: AlertEntry[];
  emptyTitle?: string;
  emptyDescription?: string;
};

const LEVEL_LABELS: Record<AlertLevel, string> = {
  success: 'OK',
  warning: 'Atención',
  danger: 'Crítico',
  neutral: 'Info',
};

/** Lista de alertas operativas con colores semánticos (verde/amarillo/rojo). */
export function AlertList({ items, emptyTitle = 'Sin alertas', emptyDescription }: AlertListProps) {
  if (items.length === 0) {
    return (
      <div className="empty-state">
        <strong>{emptyTitle}</strong>
        {emptyDescription ? <span>{emptyDescription}</span> : null}
      </div>
    );
  }
  return (
    <div className="alert-list">
      {items.map((item) => (
        <div className={`alert-item level-${item.level}`} key={item.id}>
          <div className="alert-item-head">
            <strong>{item.title}</strong>
            <span className={`status-badge ${item.level}`}>{LEVEL_LABELS[item.level]}</span>
          </div>
          {item.description ? <span>{item.description}</span> : null}
          {item.meta ? <small>{item.meta}</small> : null}
        </div>
      ))}
    </div>
  );
}
