export function money(value: number | string | null | undefined) {
  const amount = Number(value ?? 0);
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(amount);
}

export function dateTime(value?: string | null) {
  if (!value) return '—';
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
}

export function number(value: number | string | null | undefined) {
  return new Intl.NumberFormat('es-MX', { maximumFractionDigits: 2 }).format(Number(value ?? 0));
}
