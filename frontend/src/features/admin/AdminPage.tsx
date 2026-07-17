import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { adminService } from '../../services';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

function today() { return new Date().toISOString().slice(0, 10); }
function firstDay() { const now = new Date(); return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`; }
function optional(value: string) { return value.trim() || null; }
function jsonOrEmpty(value: string) { return value.trim() ? JSON.parse(value) as Record<string, unknown> : {}; }
function tone(status: string): 'success' | 'warning' | 'danger' | 'neutral' { return status === 'ACTIVO' || status === 'CONFIRMADO' ? 'success' : status === 'CALCULADO' || status === 'BORRADOR' ? 'warning' : 'neutral'; }

export function AdminPage() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);
  const [selectedPayrollId, setSelectedPayrollId] = useState('');
  const [taxForm, setTaxForm] = useState({ codigo: 'IVA16', nombre: 'IVA 16%', tipo: 'IVA', tasa: '0.16', cuenta_contable_codigo: '', es_retencion: false });
  const [seriesForm, setSeriesForm] = useState({ sucursal_id: '', documento: 'VENTA', serie: 'A', folio_actual: '0', formato: '{serie}-{folio:06d}' });
  const [rateForm, setRateForm] = useState({ moneda_origen: 'USD', moneda_destino: 'MXN', fecha: today(), tasa: '17.00', fuente: 'Manual' });
  const [ruleForm, setRuleForm] = useState({ evento: 'VENTA_CONFIRMADA', descripcion: 'Regla contable para venta confirmada', cuentas: '{"ingresos":"401.01"}', condiciones: '{}' });
  const [employeeForm, setEmployeeForm] = useState({ sucursal_id: '', numero_empleado: '', nombre: '', email: '', rfc: '', curp: '', nss: '', fecha_ingreso: today(), salario_diario: '500' });
  const [periodForm, setPeriodForm] = useState(() => ({ folio: `NOM-${Date.now()}`, fecha_inicio: firstDay(), fecha_fin: today(), observaciones: 'Periodo generado desde frontend' }));
  const [confirmForm, setConfirmForm] = useState({ cuenta_gasto_sueldos: '601.01', cuenta_bancos: '102.01', cuenta_retenciones: '216.01' });

  const taxes = useApiResource(useCallback(() => adminService.taxes({ limit: 100 }), []));
  const rules = useApiResource(useCallback(() => adminService.rules({ limit: 100 }), []));
  const employees = useApiResource(useCallback(() => adminService.employees({ limit: 100 }), []));
  const periods = useApiResource(useCallback(() => adminService.payrollPeriods({ limit: 100 }), []));
  const taxItems = useMemo(() => taxes.data ?? [], [taxes.data]);
  const ruleItems = rules.data ?? [];
  const employeeItems = employees.data ?? [];
  const periodItems = periods.data ?? [];
  const selectedPayroll = periodItems.find((period) => period.id === selectedPayrollId) ?? periodItems[0];

  async function withOperation(label: string, operation: () => Promise<unknown>) {
    setSaving(label); setError(null); setMessage(null);
    try { await operation(); setMessage('Operación administrativa completada correctamente.'); await Promise.all([taxes.reload(), rules.reload(), employees.reload(), periods.reload()]); }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'No se pudo completar la operación'); }
    finally { setSaving(null); }
  }

  async function createTax(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('impuesto', () => adminService.createTax({ ...taxForm, tasa: Number(taxForm.tasa), cuenta_contable_codigo: optional(taxForm.cuenta_contable_codigo) })); }
  async function createSeries(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('serie', async () => { const payload = { ...seriesForm, sucursal_id: optional(seriesForm.sucursal_id), folio_actual: Number(seriesForm.folio_actual) }; const serie = await adminService.createSeries(payload); const next = await adminService.nextFolio(serie.documento, serie.serie); setMessage(`Serie creada. Siguiente folio: ${next.folio}`); }); }
  async function createRate(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('tipo-cambio', () => adminService.createExchangeRate({ ...rateForm, tasa: Number(rateForm.tasa), fuente: optional(rateForm.fuente) })); }
  async function createRule(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('regla', () => adminService.createRule({ evento: ruleForm.evento, descripcion: ruleForm.descripcion, cuentas: jsonOrEmpty(ruleForm.cuentas), condiciones: jsonOrEmpty(ruleForm.condiciones) })); }
  async function createEmployee(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('empleado', () => adminService.createEmployee({ ...employeeForm, sucursal_id: optional(employeeForm.sucursal_id), email: optional(employeeForm.email), rfc: optional(employeeForm.rfc), curp: optional(employeeForm.curp), nss: optional(employeeForm.nss), salario_diario: Number(employeeForm.salario_diario) })); }
  async function createPeriod(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await withOperation('periodo', async () => { const period = await adminService.createPayrollPeriod({ ...periodForm, observaciones: optional(periodForm.observaciones) }); setSelectedPayrollId(period.id); setPeriodForm((current) => ({ ...current, folio: `NOM-${Date.now()}` })); }); }

  return <section className="page-stack">
    <PageHeader eyebrow="Administración" title="Configuración y nómina" description="Fase administrativa: impuestos, series, tipo de cambio, reglas contables, empleados y periodos de nómina." />
    {message ? <div className="alert success">{message}</div> : null}{error ? <div className="alert error">{error}</div> : null}

    <div className="module-grid two-columns">
      <SectionPanel title="Impuestos"><InlineState loading={taxes.loading} error={taxes.error} empty={taxItems.length === 0} emptyTitle="Sin impuestos" emptyDescription="Configura IVA, retenciones u otros impuestos."><div className="table-wrap compact-table"><table><thead><tr><th>Código</th><th>Nombre</th><th>Tasa</th><th>Tipo</th></tr></thead><tbody>{taxItems.map((tax) => <tr key={tax.id}><td>{tax.codigo}</td><td>{tax.nombre}</td><td>{Number(tax.tasa) * 100}%</td><td>{tax.tipo}</td></tr>)}</tbody></table></div></InlineState></SectionPanel>
      <SectionPanel title="Crear impuesto"><form className="crud-form" onSubmit={createTax}><div className="form-row"><label>Código<input value={taxForm.codigo} onChange={(event) => setTaxForm({ ...taxForm, codigo: event.target.value })} /></label><label>Tasa<input type="number" step="0.0001" value={taxForm.tasa} onChange={(event) => setTaxForm({ ...taxForm, tasa: event.target.value })} /></label></div><label>Nombre<input value={taxForm.nombre} onChange={(event) => setTaxForm({ ...taxForm, nombre: event.target.value })} /></label><label>Tipo<input value={taxForm.tipo} onChange={(event) => setTaxForm({ ...taxForm, tipo: event.target.value })} /></label><label>Cuenta contable<input value={taxForm.cuenta_contable_codigo} onChange={(event) => setTaxForm({ ...taxForm, cuenta_contable_codigo: event.target.value })} /></label><button disabled={saving === 'impuesto'}>Crear impuesto</button></form></SectionPanel>
    </div>

    <div className="module-grid two-columns">
      <SectionPanel title="Series y tipo de cambio"><form className="crud-form" onSubmit={createSeries}><div className="form-row"><label>Documento<input value={seriesForm.documento} onChange={(event) => setSeriesForm({ ...seriesForm, documento: event.target.value })} /></label><label>Serie<input value={seriesForm.serie} onChange={(event) => setSeriesForm({ ...seriesForm, serie: event.target.value })} /></label></div><label>Sucursal ID opcional<input value={seriesForm.sucursal_id} onChange={(event) => setSeriesForm({ ...seriesForm, sucursal_id: event.target.value })} /></label><label>Formato<input value={seriesForm.formato} onChange={(event) => setSeriesForm({ ...seriesForm, formato: event.target.value })} /></label><button disabled={saving === 'serie'}>Crear serie y probar folio</button></form><form className="crud-form reminder-form" onSubmit={createRate}><div className="form-row"><label>Origen<input value={rateForm.moneda_origen} onChange={(event) => setRateForm({ ...rateForm, moneda_origen: event.target.value })} /></label><label>Destino<input value={rateForm.moneda_destino} onChange={(event) => setRateForm({ ...rateForm, moneda_destino: event.target.value })} /></label></div><label>Tasa<input type="number" step="0.0001" value={rateForm.tasa} onChange={(event) => setRateForm({ ...rateForm, tasa: event.target.value })} /></label><button disabled={saving === 'tipo-cambio'}>Guardar tipo de cambio</button></form></SectionPanel>
      <SectionPanel title="Reglas contables"><form className="crud-form" onSubmit={createRule}><label>Evento<input value={ruleForm.evento} onChange={(event) => setRuleForm({ ...ruleForm, evento: event.target.value })} /></label><label>Descripción<input value={ruleForm.descripcion} onChange={(event) => setRuleForm({ ...ruleForm, descripcion: event.target.value })} /></label><label>Cuentas JSON<textarea value={ruleForm.cuentas} onChange={(event) => setRuleForm({ ...ruleForm, cuentas: event.target.value })} /></label><label>Condiciones JSON<textarea value={ruleForm.condiciones} onChange={(event) => setRuleForm({ ...ruleForm, condiciones: event.target.value })} /></label><button disabled={saving === 'regla'}>Crear regla</button></form><div className="alert-list">{ruleItems.slice(0, 5).map((rule) => <div className="alert-item" key={rule.id}><strong>{rule.evento}</strong><span>{rule.descripcion}</span></div>)}</div></SectionPanel>
    </div>

    <div className="module-grid two-columns">
      <SectionPanel title="Empleados"><InlineState loading={employees.loading} error={employees.error} empty={employeeItems.length === 0} emptyTitle="Sin empleados" emptyDescription="Crea empleados activos para cálculo de nómina."><div className="table-wrap compact-table"><table><thead><tr><th>Número</th><th>Nombre</th><th>Ingreso</th><th>Salario</th><th>Estado</th></tr></thead><tbody>{employeeItems.map((employee) => <tr key={employee.id}><td>{employee.numero_empleado}</td><td>{employee.nombre}</td><td>{employee.fecha_ingreso}</td><td>{money(employee.salario_diario)}</td><td><StatusBadge tone={tone(employee.estado)}>{employee.estado}</StatusBadge></td></tr>)}</tbody></table></div></InlineState></SectionPanel>
      <SectionPanel title="Crear empleado"><form className="crud-form" onSubmit={createEmployee}><div className="form-row"><label>Número<input value={employeeForm.numero_empleado} onChange={(event) => setEmployeeForm({ ...employeeForm, numero_empleado: event.target.value })} /></label><label>Salario diario<input type="number" step="0.01" value={employeeForm.salario_diario} onChange={(event) => setEmployeeForm({ ...employeeForm, salario_diario: event.target.value })} /></label></div><label>Nombre<input value={employeeForm.nombre} onChange={(event) => setEmployeeForm({ ...employeeForm, nombre: event.target.value })} /></label><label>Email<input value={employeeForm.email} onChange={(event) => setEmployeeForm({ ...employeeForm, email: event.target.value })} /></label><label>Fecha ingreso<input type="date" value={employeeForm.fecha_ingreso} onChange={(event) => setEmployeeForm({ ...employeeForm, fecha_ingreso: event.target.value })} /></label><button disabled={saving === 'empleado'}>Crear empleado</button></form></SectionPanel>
    </div>

    <SectionPanel title="Periodos de nómina"><form className="toolbar" onSubmit={createPeriod}><input placeholder="Folio" value={periodForm.folio} onChange={(event) => setPeriodForm({ ...periodForm, folio: event.target.value })} /><input type="date" value={periodForm.fecha_inicio} onChange={(event) => setPeriodForm({ ...periodForm, fecha_inicio: event.target.value })} /><input type="date" value={periodForm.fecha_fin} onChange={(event) => setPeriodForm({ ...periodForm, fecha_fin: event.target.value })} /><button disabled={saving === 'periodo'}>Crear periodo</button></form><div className="toolbar"><input placeholder="Cuenta sueldos" value={confirmForm.cuenta_gasto_sueldos} onChange={(event) => setConfirmForm({ ...confirmForm, cuenta_gasto_sueldos: event.target.value })} /><input placeholder="Cuenta bancos" value={confirmForm.cuenta_bancos} onChange={(event) => setConfirmForm({ ...confirmForm, cuenta_bancos: event.target.value })} /><input placeholder="Cuenta retenciones" value={confirmForm.cuenta_retenciones} onChange={(event) => setConfirmForm({ ...confirmForm, cuenta_retenciones: event.target.value })} /></div><div className="table-wrap compact-table"><table><thead><tr><th>Folio</th><th>Rango</th><th>Total neto</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>{periodItems.map((period) => <tr key={period.id} className={period.id === selectedPayroll?.id ? 'selected-row' : undefined} onClick={() => setSelectedPayrollId(period.id)}><td>{period.folio}</td><td>{period.fecha_inicio} - {period.fecha_fin}</td><td>{money(period.total_neto)}</td><td><StatusBadge tone={tone(period.estado)}>{period.estado}</StatusBadge></td><td><button className="secondary" disabled={saving === 'calcular'} onClick={() => void withOperation('calcular', () => adminService.calculatePayroll(period.id))}>Calcular</button><button className="secondary" disabled={period.estado !== 'CALCULADO' || saving === 'confirmar'} onClick={() => void withOperation('confirmar', () => adminService.confirmPayroll(period.id, confirmForm))}>Confirmar</button></td></tr>)}</tbody></table></div></SectionPanel>
  </section>;
}
