import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { financeService } from '../../services';
import { useApiResource } from '../../hooks/useApiResource';

function today() { return new Date().toISOString().slice(0, 10); }
function optional(value: string) { return value.trim() || null; }
function periodCode() { const now = new Date(); return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`; }
function tone(status: string): 'success' | 'warning' | 'danger' | 'neutral' { return status === 'CERRADO' || status === 'CONCILIADO' ? 'success' : status === 'PENDIENTE' || status === 'ABIERTO' ? 'warning' : 'neutral'; }

export function FinancePage() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);
  const [createdBankAccountId, setCreatedBankAccountId] = useState('');
  const [createdCostCenterId, setCreatedCostCenterId] = useState('');
  const [createdBudgetId, setCreatedBudgetId] = useState('');
  const [accountForm, setAccountForm] = useState({ codigo: '', nombre: '', tipo: 'ACTIVO', naturaleza: 'DEUDORA', acepta_movimientos: true });
  const [periodForm, setPeriodForm] = useState(() => ({ codigo: periodCode(), nombre: `Periodo ${periodCode()}`, fecha_inicio: today().slice(0, 8) + '01', fecha_fin: today() }));
  const [bankForm, setBankForm] = useState({ cuenta_contable_id: '', banco: '', numero_cuenta: '', moneda: 'MXN' });
  const [movementForm, setMovementForm] = useState(() => ({ cuenta_bancaria_id: '', fecha: today(), referencia: '', descripcion: '', monto: '0', tipo: 'ABONO' as 'CARGO' | 'ABONO' }));
  const [costCenterForm, setCostCenterForm] = useState({ codigo: '', nombre: '', descripcion: '' });
  const [budgetForm, setBudgetForm] = useState(() => ({ centro_costo_id: '', folio: `PRE-${Date.now()}`, nombre: '', fecha_inicio: today().slice(0, 8) + '01', fecha_fin: today(), cuenta_codigo: '', monto: '0', observaciones: '' }));
  const [commitForm, setCommitForm] = useState({ presupuesto_id: '', cuenta_codigo: '', monto: '0' });

  const accounts = useApiResource(useCallback(() => financeService.accounts({ limit: 200 }), []));
  const entries = useApiResource(useCallback(() => financeService.entries({ limit: 50 }), []));
  const periods = useApiResource(useCallback(() => financeService.periods({ limit: 50 }), []));
  const movements = useApiResource(useCallback(() => financeService.pendingBankMovements({ limit: 50 }), []));
  const accountItems = useMemo(() => accounts.data ?? [], [accounts.data]);
  const entryItems = entries.data ?? [];
  const periodItems = periods.data ?? [];
  const movementItems = movements.data ?? [];

  async function withOperation(label: string, operation: () => Promise<unknown>) {
    setSaving(label); setError(null); setMessage(null);
    try { await operation(); setMessage('Operación financiera completada correctamente.'); await Promise.all([accounts.reload(), entries.reload(), periods.reload(), movements.reload()]); }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'No se pudo completar la operación'); }
    finally { setSaving(null); }
  }

  async function createAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await withOperation('cuenta', async () => { const account = await financeService.createAccount({ ...accountForm, naturaleza: accountForm.naturaleza as 'DEUDORA' | 'ACREEDORA', padre_id: null }); setBankForm((current) => ({ ...current, cuenta_contable_id: account.id })); setBudgetForm((current) => ({ ...current, cuenta_codigo: account.codigo })); });
  }
  async function createPeriod(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('periodo', () => financeService.createPeriod(periodForm)); }
  async function createBankAccount(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('banco', async () => { const account = await financeService.createBankAccount(bankForm); setCreatedBankAccountId(account.id); setMovementForm((current) => ({ ...current, cuenta_bancaria_id: account.id })); }); }
  async function createMovement(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('movimiento', () => financeService.createBankMovement({ ...movementForm, descripcion: optional(movementForm.descripcion), monto: Number(movementForm.monto) })); }
  async function createCostCenter(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('centro', async () => { const center = await financeService.createCostCenter({ ...costCenterForm, descripcion: optional(costCenterForm.descripcion) }); setCreatedCostCenterId(center.id); setBudgetForm((current) => ({ ...current, centro_costo_id: center.id })); }); }
  async function createBudget(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('presupuesto', async () => { const budget = await financeService.createBudget({ centro_costo_id: budgetForm.centro_costo_id, folio: budgetForm.folio, nombre: budgetForm.nombre, fecha_inicio: budgetForm.fecha_inicio, fecha_fin: budgetForm.fecha_fin, observaciones: optional(budgetForm.observaciones), lineas: [{ cuenta_codigo: budgetForm.cuenta_codigo, monto: Number(budgetForm.monto) }] }); setCreatedBudgetId(budget.id); setCommitForm({ presupuesto_id: budget.id, cuenta_codigo: budgetForm.cuenta_codigo, monto: '0' }); }); }
  async function commitBudget(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('comprometer', () => financeService.commitBudget({ ...commitForm, monto: Number(commitForm.monto) })); }

  return <section className="page-stack">
    <PageHeader eyebrow="Finanzas" title="Contabilidad, tesorería y presupuestos" description="Fase financiera: catálogo contable, asientos, periodos, bancos, movimientos pendientes y presupuesto operativo." />
    {message ? <div className="alert success">{message}</div> : null}{error ? <div className="alert error">{error}</div> : null}

    <div className="module-grid two-columns">
      <SectionPanel title="Catálogo contable"><InlineState loading={accounts.loading} error={accounts.error} empty={accountItems.length === 0} emptyTitle="Sin cuentas" emptyDescription="Crea cuentas contables para tesorería y presupuestos."><div className="table-wrap compact-table"><table><thead><tr><th>Código</th><th>Nombre</th><th>Tipo</th><th>Naturaleza</th></tr></thead><tbody>{accountItems.map((account) => <tr key={account.id} onClick={() => { setBankForm((current) => ({ ...current, cuenta_contable_id: account.id })); setBudgetForm((current) => ({ ...current, cuenta_codigo: account.codigo })); }}><td>{account.codigo}</td><td>{account.nombre}</td><td>{account.tipo}</td><td>{account.naturaleza}</td></tr>)}</tbody></table></div></InlineState></SectionPanel>
      <SectionPanel title="Crear cuenta contable"><form className="crud-form" onSubmit={createAccount}><div className="form-row"><label>Código<input required value={accountForm.codigo} onChange={(event) => setAccountForm({ ...accountForm, codigo: event.target.value })} /></label><label>Tipo<select value={accountForm.tipo} onChange={(event) => setAccountForm({ ...accountForm, tipo: event.target.value })}><option>ACTIVO</option><option>PASIVO</option><option>CAPITAL</option><option>INGRESO</option><option>GASTO</option><option>COSTO</option></select></label></div><label>Nombre<input required value={accountForm.nombre} onChange={(event) => setAccountForm({ ...accountForm, nombre: event.target.value })} /></label><label>Naturaleza<select value={accountForm.naturaleza} onChange={(event) => setAccountForm({ ...accountForm, naturaleza: event.target.value })}><option>DEUDORA</option><option>ACREEDORA</option></select></label><button disabled={saving === 'cuenta'}>{saving === 'cuenta' ? 'Guardando…' : 'Crear cuenta'}</button></form></SectionPanel>
    </div>

    <div className="module-grid two-columns">
      <SectionPanel title="Asientos recientes"><InlineState loading={entries.loading} error={entries.error} empty={entryItems.length === 0} emptyTitle="Sin asientos" emptyDescription="Las ventas, compras, inventario, facturas y tesorería generarán asientos."><div className="table-wrap compact-table"><table><thead><tr><th>Fecha</th><th>Origen</th><th>Descripción</th><th>Estado</th><th>Líneas</th></tr></thead><tbody>{entryItems.map((entry) => <tr key={entry.id}><td>{entry.fecha}</td><td>{entry.origen}</td><td>{entry.descripcion}</td><td><StatusBadge tone={tone(entry.estado)}>{entry.estado}</StatusBadge></td><td>{entry.lineas?.length ?? 0}</td></tr>)}</tbody></table></div></InlineState></SectionPanel>
      <SectionPanel title="Periodos contables"><form className="crud-form compact-form" onSubmit={createPeriod}><div className="form-row"><label>Código<input value={periodForm.codigo} onChange={(event) => setPeriodForm({ ...periodForm, codigo: event.target.value })} /></label><label>Nombre<input value={periodForm.nombre} onChange={(event) => setPeriodForm({ ...periodForm, nombre: event.target.value })} /></label></div><div className="form-row"><label>Inicio<input type="date" value={periodForm.fecha_inicio} onChange={(event) => setPeriodForm({ ...periodForm, fecha_inicio: event.target.value })} /></label><label>Fin<input type="date" value={periodForm.fecha_fin} onChange={(event) => setPeriodForm({ ...periodForm, fecha_fin: event.target.value })} /></label></div><button disabled={saving === 'periodo'}>Crear periodo</button></form><div className="alert-list">{periodItems.map((period) => <div className="alert-item" key={period.id}><strong>{period.codigo} · {period.nombre}</strong><span>{period.fecha_inicio} - {period.fecha_fin}</span><StatusBadge tone={tone(period.estado)}>{period.estado}</StatusBadge><button className="secondary" onClick={() => void withOperation('estado-periodo', () => financeService.changePeriodStatus(period.id, period.estado === 'CERRADO' ? 'ABIERTO' : 'CERRADO'))}>{period.estado === 'CERRADO' ? 'Reabrir' : 'Cerrar'}</button></div>)}</div></SectionPanel>
    </div>

    <div className="module-grid two-columns">
      <SectionPanel title="Tesorería"><form className="crud-form" onSubmit={createBankAccount}><label>Cuenta contable<select required value={bankForm.cuenta_contable_id} onChange={(event) => setBankForm({ ...bankForm, cuenta_contable_id: event.target.value })}><option value="">Selecciona cuenta</option>{accountItems.map((account) => <option value={account.id} key={account.id}>{account.codigo} · {account.nombre}</option>)}</select></label><div className="form-row"><label>Banco<input required value={bankForm.banco} onChange={(event) => setBankForm({ ...bankForm, banco: event.target.value })} /></label><label>Cuenta<input required value={bankForm.numero_cuenta} onChange={(event) => setBankForm({ ...bankForm, numero_cuenta: event.target.value })} /></label></div><button disabled={saving === 'banco'}>Crear cuenta bancaria</button></form>{createdBankAccountId ? <p className="muted compact">Última cuenta bancaria: {createdBankAccountId}</p> : null}</SectionPanel>
      <SectionPanel title="Movimiento bancario"><form className="crud-form" onSubmit={createMovement}><label>Cuenta bancaria ID<input required value={movementForm.cuenta_bancaria_id} onChange={(event) => setMovementForm({ ...movementForm, cuenta_bancaria_id: event.target.value })} /></label><div className="form-row"><label>Fecha<input type="date" value={movementForm.fecha} onChange={(event) => setMovementForm({ ...movementForm, fecha: event.target.value })} /></label><label>Tipo<select value={movementForm.tipo} onChange={(event) => setMovementForm({ ...movementForm, tipo: event.target.value as 'CARGO' | 'ABONO' })}><option>ABONO</option><option>CARGO</option></select></label></div><label>Referencia<input required value={movementForm.referencia} onChange={(event) => setMovementForm({ ...movementForm, referencia: event.target.value })} /></label><label>Monto<input type="number" step="0.01" value={movementForm.monto} onChange={(event) => setMovementForm({ ...movementForm, monto: event.target.value })} /></label><label>Descripción<textarea value={movementForm.descripcion} onChange={(event) => setMovementForm({ ...movementForm, descripcion: event.target.value })} /></label><button disabled={saving === 'movimiento'}>Registrar movimiento</button></form></SectionPanel>
    </div>

    <SectionPanel title="Movimientos bancarios pendientes"><InlineState loading={movements.loading} error={movements.error} empty={movementItems.length === 0} emptyTitle="Sin movimientos pendientes" emptyDescription="Registra o importa movimientos para conciliación."><div className="table-wrap compact-table"><table><thead><tr><th>Fecha</th><th>Referencia</th><th>Tipo</th><th>Monto</th><th>Estado</th></tr></thead><tbody>{movementItems.map((movement) => <tr key={movement.id}><td>{movement.fecha}</td><td>{movement.referencia}</td><td>{movement.tipo}</td><td>{movement.monto}</td><td><StatusBadge tone={tone(movement.estado)}>{movement.estado}</StatusBadge></td></tr>)}</tbody></table></div></InlineState></SectionPanel>

    <div className="module-grid two-columns">
      <SectionPanel title="Centro de costo"><form className="crud-form" onSubmit={createCostCenter}><label>Código<input required value={costCenterForm.codigo} onChange={(event) => setCostCenterForm({ ...costCenterForm, codigo: event.target.value })} /></label><label>Nombre<input required value={costCenterForm.nombre} onChange={(event) => setCostCenterForm({ ...costCenterForm, nombre: event.target.value })} /></label><label>Descripción<textarea value={costCenterForm.descripcion} onChange={(event) => setCostCenterForm({ ...costCenterForm, descripcion: event.target.value })} /></label><button disabled={saving === 'centro'}>Crear centro</button></form>{createdCostCenterId ? <p className="muted compact">Último centro: {createdCostCenterId}</p> : null}</SectionPanel>
      <SectionPanel title="Presupuesto"><form className="crud-form" onSubmit={createBudget}><label>Centro costo ID<input required value={budgetForm.centro_costo_id} onChange={(event) => setBudgetForm({ ...budgetForm, centro_costo_id: event.target.value })} /></label><div className="form-row"><label>Folio<input value={budgetForm.folio} onChange={(event) => setBudgetForm({ ...budgetForm, folio: event.target.value })} /></label><label>Cuenta código<input value={budgetForm.cuenta_codigo} onChange={(event) => setBudgetForm({ ...budgetForm, cuenta_codigo: event.target.value })} /></label></div><label>Nombre<input value={budgetForm.nombre} onChange={(event) => setBudgetForm({ ...budgetForm, nombre: event.target.value })} /></label><label>Monto<input type="number" step="0.01" value={budgetForm.monto} onChange={(event) => setBudgetForm({ ...budgetForm, monto: event.target.value })} /></label><button disabled={saving === 'presupuesto'}>Crear presupuesto</button></form>{createdBudgetId ? <p className="muted compact">Último presupuesto: {createdBudgetId}</p> : null}</SectionPanel>
    </div>

    <SectionPanel title="Comprometer presupuesto"><form className="toolbar" onSubmit={commitBudget}><input placeholder="Presupuesto ID" value={commitForm.presupuesto_id} onChange={(event) => setCommitForm({ ...commitForm, presupuesto_id: event.target.value })} /><input placeholder="Cuenta código" value={commitForm.cuenta_codigo} onChange={(event) => setCommitForm({ ...commitForm, cuenta_codigo: event.target.value })} /><input type="number" step="0.01" placeholder="Monto" value={commitForm.monto} onChange={(event) => setCommitForm({ ...commitForm, monto: event.target.value })} /><button disabled={saving === 'comprometer'}>Comprometer</button></form></SectionPanel>
  </section>;
}
