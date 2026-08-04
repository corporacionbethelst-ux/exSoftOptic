import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { reportsService } from '../../services';
import { money, number } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

function firstDay() { const now = new Date(); return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`; }
function today() { return new Date().toISOString().slice(0, 10); }
function boolTone(value?: boolean): 'success' | 'danger' | 'neutral' { return value === true ? 'success' : value === false ? 'danger' : 'neutral'; }

export function ReportsPage() {
  const [fechaInicio, setFechaInicio] = useState(firstDay);
  const [fechaFin, setFechaFin] = useState(today);
  const [limit, setLimit] = useState(100);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const params = useMemo(() => ({ fecha_inicio: fechaInicio, fecha_fin: fechaFin }), [fechaFin, fechaInicio]);

  const trial = useApiResource(useCallback(() => reportsService.trialBalance(params), [params]));
  const income = useApiResource(useCallback(() => reportsService.incomeStatement(params), [params]));
  const balance = useApiResource(useCallback(() => reportsService.balanceSheet(fechaFin), [fechaFin]));
  const inventory = useApiResource(useCallback(() => reportsService.inventoryValuation(), []));
  const margins = useApiResource(useCallback(() => reportsService.salesMargins(params), [params]));
  const journal = useApiResource(useCallback(() => reportsService.journal(params), [params]));
  const audit = useApiResource(useCallback(() => reportsService.auditEvents(limit), [limit]));
  const chain = useApiResource(useCallback(() => reportsService.verifyAuditChain(), []));
  const metrics = useApiResource(useCallback(() => reportsService.metrics(), []));

  const topInventory = (inventory.data?.items ?? []).slice(0, 8);
  const topMargins = (margins.data?.ventas ?? []).slice(0, 8);
  const journalLines = (journal.data?.lineas ?? []).slice(0, 12);
  const auditEvents = audit.data ?? [];
  const metricsEntries = Object.entries(metrics.data ?? {}).slice(0, 12);

  async function refresh(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await Promise.all([trial.reload(), income.reload(), balance.reload(), inventory.reload(), margins.reload(), journal.reload(), audit.reload(), chain.reload(), metrics.reload()]); }
  async function cleanupIdempotency() { setError(null); setMessage(null); try { const result = await reportsService.cleanupIdempotency(); setMessage(`Limpieza idempotency completada: ${result.deleted} registros eliminados.`); await metrics.reload(); } catch (caught) { setError(caught instanceof Error ? caught.message : 'No se pudo ejecutar mantenimiento'); } }

  return <section className="page-stack">
    <PageHeader eyebrow="Reportes y operación" title="Indicadores, auditoría y observabilidad" description="Fase de reportes: contabilidad, ventas, inventario, auditoría protegida y métricas runtime." />
    {message ? <div className="alert success">{message}</div> : null}{error ? <div className="alert error">{error}</div> : null}
    <form className="toolbar" onSubmit={refresh}><input type="date" value={fechaInicio} onChange={(event) => setFechaInicio(event.target.value)} /><input type="date" value={fechaFin} onChange={(event) => setFechaFin(event.target.value)} /><input type="number" min={1} max={500} value={limit} onChange={(event) => setLimit(Number(event.target.value))} /><button>Actualizar reportes</button></form>

    <div className="metrics-grid">
      <MetricCard label="Ventas" value={money(margins.data?.total_ventas)} hint={`Margen ${number(margins.data?.margen_porcentaje)}%`} />
      <MetricCard label="Costo ventas" value={money(margins.data?.total_costo)} hint={`Margen total ${money(margins.data?.margen_total)}`} />
      <MetricCard label="Inventario valuado" value={money(inventory.data?.total_valor)} hint={`${inventory.data?.items.length ?? 0} productos/sucursal`} />
      <MetricCard label="Utilidad operativa" value={money(income.data?.utilidad_operativa)} hint={`Ingresos ${money(income.data?.ingresos)}`} />
      <MetricCard label="Activos" value={money(balance.data?.activos)} hint={`Comprobación ${money(balance.data?.comprobacion)}`} />
      <MetricCard label="Auditoría" value={chain.data?.total_events ?? 0} hint={chain.data?.valid ? 'Cadena válida' : 'Revisar cadena'} />
    </div>

    <div className="module-grid two-columns">
      <SectionPanel title="Balanza de comprobación"><InlineState loading={trial.loading} error={trial.error} empty={(trial.data?.cuentas.length ?? 0) === 0} emptyTitle="Sin balanza" emptyDescription="No hay movimientos contables en el rango."><div className="table-wrap compact-table"><table><thead><tr><th>Cuenta</th><th>Tipo</th><th>Debe</th><th>Haber</th><th>Saldo</th></tr></thead><tbody>{trial.data?.cuentas.slice(0, 12).map((account) => <tr key={account.cuenta_id}><td>{account.codigo} · {account.nombre}</td><td>{account.tipo}</td><td>{money(account.debe)}</td><td>{money(account.haber)}</td><td>{money(account.saldo)}</td></tr>)}</tbody></table></div></InlineState></SectionPanel>
      <SectionPanel title="Estado de resultados"><InlineState loading={income.loading} error={income.error} empty={(income.data?.cuentas.length ?? 0) === 0} emptyTitle="Sin estado" emptyDescription="No hay ingresos/costos/gastos para el periodo."><div className="alert-list"><div className="alert-item"><strong>Ingresos</strong><span>{money(income.data?.ingresos)}</span></div><div className="alert-item"><strong>Costos</strong><span>{money(income.data?.costos)}</span></div><div className="alert-item"><strong>Gastos</strong><span>{money(income.data?.gastos)}</span></div><div className="alert-item"><strong>Utilidad operativa</strong><span>{money(income.data?.utilidad_operativa)}</span></div></div></InlineState></SectionPanel>
    </div>

    <div className="module-grid two-columns">
      <SectionPanel title="Inventario valuado"><InlineState loading={inventory.loading} error={inventory.error} empty={topInventory.length === 0} emptyTitle="Sin inventario" emptyDescription="No hay capas/inventario valuado."><div className="table-wrap compact-table"><table><thead><tr><th>SKU</th><th>Producto</th><th>Cantidad</th><th>Valor</th></tr></thead><tbody>{topInventory.map((item) => <tr key={`${item.producto_id}-${item.sucursal_id}`}><td>{item.sku}</td><td>{item.producto}</td><td>{number(item.cantidad)}</td><td>{money(item.valor_total)}</td></tr>)}</tbody></table></div></InlineState></SectionPanel>
      <SectionPanel title="Margen de ventas"><InlineState loading={margins.loading} error={margins.error} empty={topMargins.length === 0} emptyTitle="Sin ventas" emptyDescription="No hay ventas confirmadas en el rango."><div className="table-wrap compact-table"><table><thead><tr><th>Folio</th><th>Total</th><th>Costo</th><th>Margen</th><th>%</th></tr></thead><tbody>{topMargins.map((sale) => <tr key={sale.venta_id}><td>{sale.folio}</td><td>{money(sale.total)}</td><td>{money(sale.costo_total)}</td><td>{money(sale.margen)}</td><td>{number(sale.margen_porcentaje)}%</td></tr>)}</tbody></table></div></InlineState></SectionPanel>
    </div>

    <SectionPanel title="Libro diario"><InlineState loading={journal.loading} error={journal.error} empty={journalLines.length === 0} emptyTitle="Sin diario" emptyDescription="No hay asientos en el rango."><div className="table-wrap compact-table"><table><thead><tr><th>Fecha</th><th>Origen</th><th>Cuenta</th><th>Debe</th><th>Haber</th></tr></thead><tbody>{journalLines.map((line, index) => <tr key={`${line.asiento_id}-${index}`}><td>{line.fecha}</td><td>{line.origen}</td><td>{line.cuenta_codigo} · {line.cuenta_nombre}</td><td>{money(line.debe)}</td><td>{money(line.haber)}</td></tr>)}</tbody></table></div></InlineState></SectionPanel>

    <div className="module-grid two-columns">
      <SectionPanel title="Auditoría"><InlineState loading={audit.loading} error={audit.error} empty={auditEvents.length === 0} emptyTitle="Sin eventos" emptyDescription="Aún no hay eventos auditados."><div className="alert-list">{auditEvents.slice(0, 12).map((event) => <div key={event.id} className="alert-item"><strong>{event.accion}</strong><span>{event.entidad ?? 'Entidad'} · {event.entidad_id ?? '—'}</span><small>{new Date(event.created_at).toLocaleString()}</small></div>)}</div></InlineState></SectionPanel>
      <SectionPanel title="Observabilidad"><div className="alert-list"><div className="alert-item"><strong>Cadena auditoría</strong><StatusBadge tone={boolTone(chain.data?.valid)}>{chain.data?.valid ? 'Válida' : 'Inválida / pendiente'}</StatusBadge><span>{chain.data?.reason ?? chain.data?.last_hash ?? 'Sin detalle'}</span></div>{metricsEntries.map(([key, value]) => <div className="alert-item" key={key}><strong>{key}</strong><span>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span></div>)}</div><button className="secondary" onClick={() => void cleanupIdempotency()}>Limpiar idempotency expirada</button></SectionPanel>
    </div>
  </section>;
}
