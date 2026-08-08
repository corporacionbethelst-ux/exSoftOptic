import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { useApiResource } from '../../hooks/useApiResource';
import { operationsService } from '../../services';

function jsonOrEmpty(value: string) { return value.trim() ? JSON.parse(value) as Record<string, unknown> : {}; }
function statusTone(status: string): 'success' | 'warning' | 'danger' | 'neutral' { return status === 'PUBLISHED' ? 'success' : status === 'FAILED' ? 'danger' : status === 'PROCESSING' ? 'warning' : 'neutral'; }

export function OperationsPage() {
  const [limit, setLimit] = useState(100);
  const [saving, setSaving] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [eventForm, setEventForm] = useState(() => ({ aggregate_type: 'ManualCheck', aggregate_id: `manual-${Date.now()}`, event_type: 'manual.healthcheck.requested', payload: '{"source":"operations"}', headers: '{}', idempotency_key: '', max_attempts: '5' }));
  const [failureForm, setFailureForm] = useState({ error: 'Fallo operativo registrado desde consola', retry_delay_seconds: '60' });

  const readiness = useApiResource(useCallback(() => operationsService.readiness(), []));
  const metrics = useApiResource(useCallback(() => operationsService.metrics(), []));
  const pending = useApiResource(useCallback(() => operationsService.pendingOutbox({ limit }), [limit]));
  const pendingEvents = pending.data ?? [];
  const metricsEntries = useMemo(() => Object.entries(metrics.data ?? {}).slice(0, 10), [metrics.data]);

  async function withOperation(label: string, operation: () => Promise<unknown>) {
    setSaving(label); setError(null); setMessage(null);
    try { const result = await operation(); setMessage(typeof result === 'object' ? `Operación ${label} completada.` : String(result)); await Promise.all([readiness.reload(), metrics.reload(), pending.reload()]); }
    catch (caught) { setError(caught instanceof Error ? caught.message : `No se pudo completar ${label}`); }
    finally { setSaving(null); }
  }

  async function refresh(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await Promise.all([readiness.reload(), metrics.reload(), pending.reload()]); }
  async function createEvent(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('crear evento', () => operationsService.createOutboxEvent({ aggregate_type: eventForm.aggregate_type, aggregate_id: eventForm.aggregate_id, event_type: eventForm.event_type, payload: jsonOrEmpty(eventForm.payload), headers: jsonOrEmpty(eventForm.headers), idempotency_key: eventForm.idempotency_key.trim() || null, max_attempts: Number(eventForm.max_attempts) })); }

  return <section className="page-stack">
    <PageHeader eyebrow="Operación" title="Centro operativo" description="Monitorea readiness, métricas runtime y cola outbox; permite operar eventos pendientes de forma controlada." />
    {message ? <div className="alert success">{message}</div> : null}{error ? <div className="alert error">{error}</div> : null}
    <form className="toolbar" onSubmit={refresh}><input type="number" min={1} max={500} value={limit} onChange={(event) => setLimit(Number(event.target.value))} /><button>Actualizar operación</button><button type="button" className="secondary" disabled={saving === 'dispatch'} onClick={() => void withOperation('dispatch', () => operationsService.dispatchOutbox(limit))}>Despachar outbox</button><button type="button" className="secondary" disabled={saving === 'cleanup'} onClick={() => void withOperation('cleanup', () => operationsService.cleanupIdempotency(500))}>Limpiar idempotency</button></form>

    <div className="metrics-grid"><MetricCard label="Readiness" value={readiness.data?.status ?? '—'} hint={readiness.data?.database ?? 'Sin verificación'} /><MetricCard label="Outbox pendiente" value={pendingEvents.length} hint={`Límite ${limit}`} /><MetricCard label="Métricas runtime" value={metricsEntries.length} hint="Snapshot protegido" /></div>

    <div className="module-grid two-columns">
      <SectionPanel title="Crear evento outbox"><form className="crud-form" onSubmit={createEvent}><div className="form-row"><label>Aggregate<input value={eventForm.aggregate_type} onChange={(event) => setEventForm({ ...eventForm, aggregate_type: event.target.value })} /></label><label>ID agregado<input value={eventForm.aggregate_id} onChange={(event) => setEventForm({ ...eventForm, aggregate_id: event.target.value })} /></label></div><label>Tipo evento<input value={eventForm.event_type} onChange={(event) => setEventForm({ ...eventForm, event_type: event.target.value })} /></label><label>Payload JSON<textarea value={eventForm.payload} onChange={(event) => setEventForm({ ...eventForm, payload: event.target.value })} /></label><label>Headers JSON<textarea value={eventForm.headers} onChange={(event) => setEventForm({ ...eventForm, headers: event.target.value })} /></label><div className="form-row"><label>Idempotency key<input value={eventForm.idempotency_key} onChange={(event) => setEventForm({ ...eventForm, idempotency_key: event.target.value })} /></label><label>Máx. intentos<input type="number" min={1} max={50} value={eventForm.max_attempts} onChange={(event) => setEventForm({ ...eventForm, max_attempts: event.target.value })} /></label></div><button disabled={saving === 'crear evento'}>Crear evento</button></form></SectionPanel>
      <SectionPanel title="Métricas runtime"><InlineState loading={metrics.loading} error={metrics.error} empty={metricsEntries.length === 0} emptyTitle="Sin métricas" emptyDescription="No se recibió snapshot runtime."><div className="alert-list">{metricsEntries.map(([key, value]) => <div className="alert-item" key={key}><strong>{key}</strong><span>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span></div>)}</div></InlineState></SectionPanel>
    </div>

    <SectionPanel title="Eventos outbox pendientes"><InlineState loading={pending.loading} error={pending.error} empty={pendingEvents.length === 0} emptyTitle="Sin eventos pendientes" emptyDescription="La cola operativa está despejada."><div className="toolbar"><input placeholder="Error al marcar fallido" value={failureForm.error} onChange={(event) => setFailureForm({ ...failureForm, error: event.target.value })} /><input type="number" min={0} max={86400} value={failureForm.retry_delay_seconds} onChange={(event) => setFailureForm({ ...failureForm, retry_delay_seconds: event.target.value })} /></div><div className="table-wrap compact-table"><table><thead><tr><th>Evento</th><th>Agregado</th><th>Estado</th><th>Intentos</th><th>Disponible</th><th>Acciones</th></tr></thead><tbody>{pendingEvents.map((event) => <tr key={event.id}><td>{event.event_type}</td><td>{event.aggregate_type} · {event.aggregate_id}</td><td><StatusBadge tone={statusTone(event.status)}>{event.status}</StatusBadge></td><td>{event.attempts}/{event.max_attempts}</td><td>{new Date(event.available_at).toLocaleString()}</td><td><button className="secondary" disabled={saving === event.id} onClick={() => void withOperation(event.id, () => operationsService.markProcessing(event.id))}>Processing</button><button className="secondary" disabled={saving === event.id} onClick={() => void withOperation(event.id, () => operationsService.markPublished(event.id))}>Publicado</button><button className="secondary danger" disabled={saving === event.id} onClick={() => void withOperation(event.id, () => operationsService.markFailed(event.id, { error: failureForm.error, retry_delay_seconds: Number(failureForm.retry_delay_seconds) }))}>Fallido</button></td></tr>)}</tbody></table></div></InlineState></SectionPanel>
  </section>;
}
