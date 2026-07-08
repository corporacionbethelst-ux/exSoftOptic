export function StatusBadge({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'success' | 'warning' | 'danger' | 'neutral' }) {
  return <span className={`status-badge ${tone}`}>{children}</span>;
}
