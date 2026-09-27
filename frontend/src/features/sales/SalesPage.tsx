import { Link } from 'react-router-dom';
import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { useAuth } from '../auth/authContext';
import { hasPermission } from '../../lib/permissions';
import { catalogService, patientsService, salesService } from '../../services';
import type { Producto } from '../../types/catalog';
import type { Cliente, Paciente } from '../../types/patients';
import type { Venta, VentaConfirmarPayload, VentaLineaPayload, VentaPayload } from '../../types/sales';
import { money } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';
import { buildPrescriptionPayload, EMPTY_PRESCRIPTION, hasPrescriptionData, validatePrescription, type PrescriptionValues } from './prescription';
import { PrescriptionForm } from './PrescriptionForm';

const DEFAULT_CONFIRM: VentaConfirmarPayload = {
  cuenta_cobro: '102.01',
  cuenta_ingresos: '401.01',
  cuenta_costo_ventas: '501.01',
  cuenta_inventario: '115.01',
};

type PatientMode = 'walkin' | 'existing' | 'new';

function emptyLine(products: Producto[]): VentaLineaPayload {
  const product = products[0];
  return {
    producto_id: product?.id ?? '',
    descripcion: product?.nombre ?? '',
    cantidad: 1,
    precio_unitario: Number(product?.precio_venta ?? 0),
    descuento: 0,
  };
}

export function SalesPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [sucursalId, setSucursalId] = useState(user?.sucursal_id ?? '');
  const [folio, setFolio] = useState(() => `VTA-${Date.now()}`);
  const [patientMode, setPatientMode] = useState<PatientMode>('walkin');
  const [selectedClientId, setSelectedClientId] = useState('');
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [newPatient, setNewPatient] = useState({ nombre: '', fecha_nacimiento: '', telefono: '' });
  const [prescription, setPrescription] = useState<PrescriptionValues>(EMPTY_PRESCRIPTION);
  const [metodoPago, setMetodoPago] = useState('EFECTIVO');
  const [referenciaPago, setReferenciaPago] = useState('');
  const [lineas, setLineas] = useState<VentaLineaPayload[]>([]);
  const [pendingConfirm, setPendingConfirm] = useState<Venta | null>(null);
  const [pendingReturn, setPendingReturn] = useState<Venta | null>(null);
  const [returnFolio, setReturnFolio] = useState(() => `DEV-${Date.now()}`);
  const [returnReason, setReturnReason] = useState('Devolución solicitada por cliente');
  const [formError, setFormError] = useState<string | null>(null);
  const [operationMessage, setOperationMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [processing, setProcessing] = useState(false);
  const skip = (page - 1) * pageSize;

  const loadSales = useCallback(() => salesService.list({ skip, limit: pageSize }), [pageSize, skip]);
  const loadProducts = useCallback(() => catalogService.products({ limit: 100 }), []);
  const loadClients = useCallback(() => patientsService.clients({ limit: 100 }), []);
  const sales = useApiResource(loadSales);
  const products = useApiResource(loadProducts);
  const clients = useApiResource(loadClients, patientMode !== 'walkin');
  const salesItems = sales.data ?? [];
  const productItems = products.data?.items ?? products.data?.productos ?? [];
  const clientItems: Cliente[] = clients.data ?? [];
  const [clientPatients, setClientPatients] = useState<Paciente[]>([]);
  const subtotal = useMemo(() => lineas.reduce((total, line) => total + line.cantidad * line.precio_unitario - line.descuento, 0), [lineas]);
  const impuestos = useMemo(() => Number((subtotal * 0.16).toFixed(2)), [subtotal]);
  const total = useMemo(() => Number((subtotal + impuestos).toFixed(2)), [subtotal, impuestos]);
  const showPrescription = patientMode === 'existing' || patientMode === 'new';

  async function handleClientChange(clientId: string) {
    setSelectedClientId(clientId);
    setSelectedPatientId('');
    setClientPatients([]);
    if (!clientId) return;
    try {
      const list = await patientsService.patients({ cliente_id: clientId, limit: 100 });
      setClientPatients(list);
      if (list.length === 1) setSelectedPatientId(list[0].id);
    } catch {
      setClientPatients([]);
    }
  }

  function addLine() {
    setLineas((current) => [...current, emptyLine(productItems)]);
  }

  function updateLine(index: number, patch: Partial<VentaLineaPayload>) {
    setLineas((current) => current.map((line, lineIndex) => (lineIndex === index ? { ...line, ...patch } : line)));
  }

  function selectProduct(index: number, productId: string) {
    const product = productItems.find((item) => item.id === productId);
    updateLine(index, {
      producto_id: productId,
      descripcion: product?.nombre ?? '',
      precio_unitario: Number(product?.precio_venta ?? 0),
    });
  }

  function validateClinical(): string | null {
    if (patientMode === 'existing') {
      if (!selectedClientId) return 'Selecciona un cliente para la venta con paciente.';
      if (!selectedPatientId) return 'Selecciona el paciente que recibirá la atención óptica.';
      if (hasPrescriptionData(prescription)) {
        const prescriptionError = validatePrescription(prescription);
        if (prescriptionError) return prescriptionError;
      }
    }
    if (patientMode === 'new') {
      if (!selectedClientId) return 'Selecciona el cliente (titular) del nuevo paciente.';
      if (!newPatient.nombre.trim()) return 'Captura el nombre del nuevo paciente.';
      const prescriptionError = validatePrescription(prescription);
      if (prescriptionError) return prescriptionError;
    }
    return null;
  }

  function resetClinicalBlock() {
    setPatientMode('walkin');
    setSelectedClientId('');
    setSelectedPatientId('');
    setClientPatients([]);
    setNewPatient({ nombre: '', fecha_nacimiento: '', telefono: '' });
    setPrescription(EMPTY_PRESCRIPTION);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setOperationMessage(null);
    const clinicalError = validateClinical();
    if (clinicalError) {
      setFormError(clinicalError);
      return;
    }
    setSaving(true);
    try {
      let payload: VentaPayload;
      if (patientMode === 'existing') {
        payload = {
          sucursal_id: sucursalId,
          cliente_id: selectedClientId,
          paciente_id: selectedPatientId,
          receta_id: null,
          folio,
          impuestos,
          lineas,
          pagos: total > 0 ? [{ metodo_pago: metodoPago, monto: total, referencia: referenciaPago || null }] : [],
        };
        if (hasPrescriptionData(prescription)) {
          const created = await patientsService.createPrescription({
            paciente_id: selectedPatientId,
            ...buildPrescriptionPayload(prescription),
          });
          payload.receta_id = created.id;
        }
      } else if (patientMode === 'new') {
        payload = {
          sucursal_id: sucursalId,
          cliente_id: selectedClientId,
          paciente: {
            nombre: newPatient.nombre.trim(),
            fecha_nacimiento: newPatient.fecha_nacimiento || null,
            telefono: newPatient.telefono.trim() || null,
          },
          receta: buildPrescriptionPayload(prescription),
          folio,
          impuestos,
          lineas,
          pagos: total > 0 ? [{ metodo_pago: metodoPago, monto: total, referencia: referenciaPago || null }] : [],
        };
      } else {
        payload = {
          sucursal_id: sucursalId,
          cliente: { nombre: 'Cliente mostrador' },
          folio,
          impuestos,
          lineas,
          pagos: total > 0 ? [{ metodo_pago: metodoPago, monto: total, referencia: referenciaPago || null }] : [],
        };
      }
      await salesService.create(payload);
      setOperationMessage(
        patientMode === 'walkin'
          ? 'Venta creada correctamente. Ahora puedes confirmarla desde el listado.'
          : 'Venta creada con expediente clínico (paciente y receta) vinculado al ticket.',
      );
      setFolio(`VTA-${Date.now()}`);
      setLineas([]);
      resetClinicalBlock();
      await sales.reload();
      if (patientMode !== 'walkin') await clients.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo crear la venta');
    } finally {
      setSaving(false);
    }
  }

  async function confirmSale() {
    if (!pendingConfirm) return;
    setProcessing(true);
    setFormError(null);
    try {
      await salesService.confirm(pendingConfirm.id, DEFAULT_CONFIRM);
      setPendingConfirm(null);
      setOperationMessage('Venta confirmada correctamente.');
      await sales.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo confirmar la venta');
    } finally {
      setProcessing(false);
    }
  }

  async function registerReturn() {
    if (!pendingReturn?.lineas?.[0]) return;
    setProcessing(true);
    setFormError(null);
    try {
      await salesService.returnSale(pendingReturn.id, {
        folio: returnFolio,
        motivo: returnReason,
        lineas: [{ venta_linea_id: pendingReturn.lineas[0].id, cantidad: 1 }],
        ...DEFAULT_CONFIRM,
      });
      setPendingReturn(null);
      setReturnFolio(`DEV-${Date.now()}`);
      setOperationMessage('Devolución registrada correctamente.');
      await sales.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo registrar la devolución');
    } finally {
      setProcessing(false);
    }
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Operación"
        title="Ventas"
        description="Punto de venta con expediente clínico: crear borradores vinculados a paciente/receta, confirmar venta y registrar devoluciones."
      />

      <SectionPanel title="Listado de ventas" footer={<span className="muted compact">{salesItems.length} en esta página</span>}>
        <InlineState loading={sales.loading} error={sales.error} empty={salesItems.length === 0} emptyTitle="Sin ventas" emptyDescription="Crea una venta o ejecuta make seed-demo.">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Folio</th><th>Estado</th><th>Paciente / Receta</th><th>Líneas</th><th>Subtotal</th><th>Impuestos</th><th>Total</th><th>Acciones</th></tr></thead>
              <tbody>
                {salesItems.map((sale) => (
                  <tr key={sale.id}>
                    <td><Link to={`/sales/${sale.id}`} className="row-link">{sale.folio}</Link></td>
                    <td><StatusBadge tone={sale.estado === 'CONFIRMADA' ? 'success' : 'warning'}>{sale.estado}</StatusBadge></td>
                    <td className="compact">
                      {sale.paciente_id ? `Paciente ✓${sale.receta_id ? ' · Receta ✓' : ' · sin receta'}` : 'Mostrador'}
                    </td>
                    <td>{sale.lineas?.length ?? 0}</td>
                    <td>{money(sale.subtotal)}</td>
                    <td>{money(sale.impuestos)}</td>
                    <td>{money(sale.total)}</td>
                    <td className="action-cell">
                      {hasPermission(user, 'ventas.confirmar') ? <button className="secondary-button" disabled={sale.estado === 'CONFIRMADA'} onClick={() => setPendingConfirm(sale)}>Confirmar</button> : null}
                      {hasPermission(user, 'ventas.devolver') ? <button className="secondary-button" disabled={sale.estado !== 'CONFIRMADA'} onClick={() => setPendingReturn(sale)}>Devolver</button> : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={page}
            pageSize={pageSize}
            total={Math.max(salesItems.length + skip, page * pageSize)}
            onPageChange={setPage}
            onPageSizeChange={(nextPageSize) => {
              setPage(1);
              setPageSize(nextPageSize);
            }}
          />
        </InlineState>
      </SectionPanel>

      <SectionPanel title="Nueva venta" description="Punto de venta con expediente clínico: vincula paciente y receta óptica, o usa venta rápida de mostrador.">
        {operationMessage ? <div className="alert success wide-field">{operationMessage}</div> : null}
        <form className="crud-form" onSubmit={(event) => void handleSubmit(event)}>
          <div className="wide-field patient-mode">
            <label className="check-field"><input type="radio" name="patientMode" checked={patientMode === 'walkin'} onChange={() => setPatientMode('walkin')} /> Venta de mostrador (sin paciente)</label>
            <label className="check-field"><input type="radio" name="patientMode" checked={patientMode === 'existing'} onChange={() => setPatientMode('existing')} /> Paciente existente</label>
            <label className="check-field"><input type="radio" name="patientMode" checked={patientMode === 'new'} onChange={() => setPatientMode('new')} /> Nuevo paciente + receta</label>
          </div>

          {patientMode !== 'walkin' ? (
            <>
              <label>Cliente titular
                <select value={selectedClientId} onChange={(event) => void handleClientChange(event.target.value)} required>
                  <option value="">{clients.loading ? 'Cargando clientes…' : 'Selecciona un cliente'}</option>
                  {clientItems.map((client) => <option key={client.id} value={client.id}>{client.nombre}{client.telefono ? ` · ${client.telefono}` : ''}</option>)}
                </select>
              </label>
              {clients.error ? <div className="alert error wide-field">No se pudieron cargar los clientes: {clients.error}</div> : null}
            </>
          ) : null}

          {patientMode === 'existing' ? (
            <label>Paciente
              <select value={selectedPatientId} onChange={(event) => setSelectedPatientId(event.target.value)} required disabled={!selectedClientId}>
                <option value="">{selectedClientId ? (clientPatients.length ? 'Selecciona un paciente' : 'Este cliente aún no tiene pacientes registrados') : 'Selecciona primero un cliente'}</option>
                {clientPatients.map((patient) => <option key={patient.id} value={patient.id}>{patient.nombre}{patient.fecha_nacimiento ? ` · nac. ${patient.fecha_nacimiento}` : ''}</option>)}
              </select>
            </label>
          ) : null}

          {patientMode === 'new' ? (
            <>
              <label>Nombre del paciente
                <input value={newPatient.nombre} onChange={(event) => setNewPatient((current) => ({ ...current, nombre: event.target.value }))} placeholder="Nombre completo" required />
              </label>
              <label>Fecha nacimiento
                <input type="date" max={new Date().toISOString().slice(0, 10)} value={newPatient.fecha_nacimiento} onChange={(event) => setNewPatient((current) => ({ ...current, fecha_nacimiento: event.target.value }))} />
              </label>
              <label>Teléfono paciente
                <input value={newPatient.telefono} onChange={(event) => setNewPatient((current) => ({ ...current, telefono: event.target.value }))} placeholder="Opcional" />
              </label>
            </>
          ) : null}

          {showPrescription ? (
            <PrescriptionForm values={prescription} onChange={(patch) => setPrescription((current) => ({ ...current, ...patch }))} />
          ) : null}

          <label>Folio<input value={folio} onChange={(event) => setFolio(event.target.value)} required /></label>
          <label>Sucursal ID<input value={sucursalId} onChange={(event) => setSucursalId(event.target.value)} required /></label>
          <label>Método pago
            <select value={metodoPago} onChange={(event) => setMetodoPago(event.target.value)} required>
              {['EFECTIVO', 'TARJETA', 'TRANSFERENCIA', 'MIXTO'].map((method) => <option key={method} value={method}>{method}</option>)}
            </select>
          </label>
          <label>Referencia pago<input value={referenciaPago} onChange={(event) => setReferenciaPago(event.target.value)} placeholder="Opcional para efectivo" /></label>

          <div className="wide-field line-editor">
            <div className="split"><strong>Líneas</strong><button className="secondary-button" type="button" onClick={addLine}>Agregar línea</button></div>
            <InlineState loading={products.loading} error={products.error} empty={lineas.length === 0} emptyTitle="Sin líneas" emptyDescription="Agrega al menos un producto a la venta.">
              {lineas.map((line, index) => (
                <div className="line-row" key={`${line.producto_id}-${index}`}>
                  <select value={line.producto_id} onChange={(event) => selectProduct(index, event.target.value)} required>
                    <option value="">Producto</option>
                    {productItems.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.nombre}</option>)}
                  </select>
                  <input type="number" min="0.001" step="0.001" value={line.cantidad} onChange={(event) => updateLine(index, { cantidad: Number(event.target.value) })} />
                  <input type="number" min="0" step="0.01" value={line.precio_unitario} onChange={(event) => updateLine(index, { precio_unitario: Number(event.target.value) })} />
                  <input type="number" min="0" step="0.01" value={line.descuento} onChange={(event) => updateLine(index, { descuento: Number(event.target.value) })} />
                  <button className="danger-button" type="button" onClick={() => setLineas((current) => current.filter((_, lineIndex) => lineIndex !== index))}>Quitar</button>
                </div>
              ))}
            </InlineState>
          </div>

          <div className="wide-field totals-card">
            <span>Subtotal: <strong>{money(subtotal)}</strong></span>
            <span>IVA: <strong>{money(impuestos)}</strong></span>
            <span>Total: <strong>{money(total)}</strong></span>
          </div>
          {formError ? <div className="alert error wide-field">{formError}</div> : null}
          <div className="form-actions wide-field">
            <button className="primary-button" disabled={saving || lineas.length === 0}>{saving ? 'Guardando…' : 'Crear venta'}</button>
          </div>
        </form>
      </SectionPanel>

      <ConfirmDialog open={Boolean(pendingConfirm)} title="Confirmar venta" description="Confirmar descuenta inventario, registra contabilidad y deja la venta lista para facturación/devolución." confirmLabel="Confirmar venta" busy={processing} onConfirm={() => void confirmSale()} onCancel={() => setPendingConfirm(null)}>
        <strong>{pendingConfirm?.folio}</strong>
      </ConfirmDialog>

      <ConfirmDialog open={Boolean(pendingReturn)} title="Registrar devolución" description="La devolución se registrará sobre la primera línea de la venta para validar el flujo operativo inicial." confirmLabel="Registrar devolución" busy={processing} onConfirm={() => void registerReturn()} onCancel={() => setPendingReturn(null)}>
        <div className="form-stack">
          <label>Folio devolución<input value={returnFolio} onChange={(event) => setReturnFolio(event.target.value)} /></label>
          <label>Motivo<input value={returnReason} onChange={(event) => setReturnReason(event.target.value)} /></label>
        </div>
      </ConfirmDialog>
    </section>
  );
}
