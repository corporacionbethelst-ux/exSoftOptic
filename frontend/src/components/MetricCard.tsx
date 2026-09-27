import type { ReactNode } from 'react';

export type MetricTone = 'neutral' | 'success' | 'warning' | 'danger';

export function MetricCard({ label, value, hint, tone = 'neutral', icon }: { label: string; value: string | number; hint?: ReactNode; tone?: MetricTone; icon?: ReactNode }) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <span>{icon}{label}</span>
      <strong>{value}</strong>
      {hint ? <small>{hint}</small> : null}
    </article>
  );
}
