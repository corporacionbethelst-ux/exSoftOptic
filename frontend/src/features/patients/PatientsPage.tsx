import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { patientsService } from '../../services';
import type { ClientePayload, PacientePayload, RecetaOpticaPayload } from '../../types/patients';
import { useApiResource } from '../../hooks/useApiResource';

const PAGE_SIZE = 25;

function today() {
  return new Date().toISOString().slice(0, 10);
}

function optional(value: string) {
  return value.trim() || null;
}

function numericOrNull(value: string) {
  return value.trim() === '' ? null : Number(value);
}

export function PatientsPage() {
  const [clientSearch, setClientSearch] = useState('');
  const [clientPage, setClientPage] = useState(1);
  const [patientSearch, setPatientSearch] = useState('');
  const [patientPage, setPatientPage] = useState(1);
  const [prescriptionPage, setPrescriptionPage] = useState(1);
  const [selectedClientId, setSelectedClientId] = useState('');
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [savingClient, setSavingClient] = useState(false);
  const [savingPatient, setSavingPatient] = useState(false);
  const [savingPrescription, setSavingPrescription] = useState(false);

  const [clientForm, setClientForm] = useState({ nombre: '', email: '', telefono: '', rfc: '', codigo_postal: '', regimen_fiscal: '' });
  const [patientForm, setPatientForm] = useState({ nombre: '', fecha_nacimiento: '', telefono: '', email: '' });
  const [prescriptionForm, setPrescriptionForm] = useState({
    fecha: today(), od_esfera: '', od_cilindro: '', od_eje: '', od_adicion: '', oi_esfera: '', oi_cilindro: '', oi_eje: '', oi_adicion: '', dnp: '', altura: '', observaciones: '',
  });

  const clientSkip = (clientPage - 1) * PAGE_SIZE;
  const patientSkip = (patientPage - 1) * PAGE_SIZE;
  const prescriptionSkip = (prescriptionPage - 1) * PAGE_SIZE;

  const loadClients = useCallback(() => patientsService.clients({ search: clientSearch || undefined, skip: clientSkip, limit: PAGE_SIZE }), [clientSearch, clientSkip]);
  const loadPatients = useCallback(() => patientsService.patients({ cliente_id: selectedClientId || undefined, search: patientSearch || undefined, skip: patientSkip, limit: PAGE_SIZE }), [patientSearch, patientSkip, selectedClientId]);
  const loadPrescriptions = useCallback(() => patientsService.prescriptions({ paciente_id: selectedPatientId || undefined, skip: prescriptionSkip, limit: PAGE_SIZE }), [prescriptionSkip, selectedPatientId]);
  const clients = useApiResource(loadClients);
  const patients = useApiResource(loadPatients);
  const prescriptions = useApiResource(loadPrescriptions);

  const clientItems = useMemo(() => clients.data ?? [], [clients.data]);
  const patientItems = useMemo(() => patients.data ?? [], [patients.data]);
  const prescriptionItems = prescriptions.data ?? [];
  const selectedClient = useMemo(() => clientItems.find((client) => client.id === selectedClientId), [clientItems, selectedClientId]);
  const selectedPatient = useMemo(() => patientItems.find((patient) => patient.id === selectedPatientId), [patientItems, selectedPatientId]);

  async function submitClient(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingClient(true); setError(null); setMessage(null);
    try {
      const payload: ClientePayload = {
        nombre: clientForm.nombre,
        email: optional(clientForm.email),
        telefono: optional(clientForm.telefono),
        rfc: optional(clientForm.rfc),
        codigo_postal: optional(clientForm.codigo_postal),
        regimen_fiscal: optional(clientForm.regimen_fiscal),
      };
      const created = await patientsService.createClient(payload);
      setSelectedClientId(created.id);
      setClientForm({ nombre: '', email: '', telefono: '', rfc: '', codigo_postal: '', regimen_fiscal: '' });
      setMessage('Cliente creado correctamente. Ahora puedes registrar paciente y receta.');
      await clients.reload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'No se pudo crear el cliente');
    } finally {
      setSavingClient(false);
    }
  }

  async function submitPatient(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedClientId) { setError('Selecciona un cliente antes de crear el paciente.'); return; }
    setSavingPatient(true); setError(null); setMessage(null);
    try {
      const payload: PacientePayload = { cliente_id: selectedClientId, nombre: patientForm.nombre, fecha_nacimiento: optional(patientForm.fecha_nacimiento), telefono: optional(patientForm.telefono), email: optional(patientForm.email) };
      const created = await patientsService.createPatient(payload);
      setSelectedPatientId(created.id);
      setPatientForm({ nombre: '', fecha_nacimiento: '', telefono: '', email: '' });
      setMessage('Paciente creado correctamente. Ya puedes capturar su receta óptica.');
      await patients.reload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'No se pudo crear el paciente');
    } finally {
      setSavingPatient(false);
    }
  }

  async function submitPrescription(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPatientId) { setError('Selecciona un paciente antes de crear la receta.'); return; }
    setSavingPrescription(true); setError(null); setMessage(null);
    try {
      const payload: RecetaOpticaPayload = {
        paciente_id: selectedPatientId,
        fecha: prescriptionForm.fecha,
        od_esfera: numericOrNull(prescriptionForm.od_esfera), od_cilindro: numericOrNull(prescriptionForm.od_cilindro), od_eje: numericOrNull(prescriptionForm.od_eje), od_adicion: numericOrNull(prescriptionForm.od_adicion),
        oi_esfera: numericOrNull(prescriptionForm.oi_esfera), oi_cilindro: numericOrNull(prescriptionForm.oi_cilindro), oi_eje: numericOrNull(prescriptionForm.oi_eje), oi_adicion: numericOrNull(prescriptionForm.oi_adicion),
        dnp: numericOrNull(prescriptionForm.dnp), altura: numericOrNull(prescriptionForm.altura), observaciones: optional(prescriptionForm.observaciones),
      };
      await patientsService.createPrescription(payload);
      setPrescriptionForm((current) => ({ ...current, fecha: today(), od_esfera: '', od_cilindro: '', od_eje: '', od_adicion: '', oi_esfera: '', oi_cilindro: '', oi_eje: '', oi_adicion: '', dnp: '', altura: '', observaciones: '' }));
      setMessage('Receta óptica creada correctamente.');
      await prescriptions.reload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'No se pudo crear la receta');
    } finally {
      setSavingPrescription(false);
    }
  }

  return (
    <section className="page-stack">
      <PageHeader eyebrow="Pacientes" title="Clientes, pacientes y recetas" description="Fase completa de expediente clínico: alta de clientes, pacientes dependientes y recetas ópticas con búsqueda y selección contextual." />
      {message ? <div className="alert success">{message}</div> : null}
      {error ? <div className="alert error">{error}</div> : null}

      <div className="module-grid two-columns">
        <SectionPanel title="Clientes" footer={<Pagination page={clientPage} pageSize={PAGE_SIZE} total={clientItems.length} onPageChange={setClientPage} onPageSizeChange={() => undefined} />}>
          <form className="toolbar" onSubmit={(event) => { event.preventDefault(); setClientPage(1); void clients.reload(); }}>
            <input value={clientSearch} onChange={(event) => setClientSearch(event.target.value)} placeholder="Buscar por nombre, email o teléfono" />
            <button type="submit" className="secondary">Buscar</button>
          </form>
          <InlineState loading={clients.loading} error={clients.error} empty={clientItems.length === 0} emptyTitle="Sin clientes" emptyDescription="Crea un cliente para iniciar su expediente.">
            <div className="table-wrap"><table><thead><tr><th>Nombre</th><th>Contacto</th><th>Fiscal</th></tr></thead><tbody>{clientItems.map((client) => (
              <tr key={client.id} className={client.id === selectedClientId ? 'selected-row' : undefined} onClick={() => { setSelectedClientId(client.id); setSelectedPatientId(''); }}>
                <td><strong>{client.nombre}</strong><br /><span className="compact-id">{client.id}</span></td><td>{client.email ?? '—'}<br />{client.telefono ?? '—'}</td><td>{client.rfc ?? 'Sin RFC'}<br />{client.regimen_fiscal ?? '—'}</td>
              </tr>
            ))}</tbody></table></div>
          </InlineState>
        </SectionPanel>

        <SectionPanel title="Crear cliente">
          <form className="crud-form" onSubmit={submitClient}>
            <label>Nombre<input required value={clientForm.nombre} onChange={(event) => setClientForm({ ...clientForm, nombre: event.target.value })} /></label>
            <label>Email<input type="email" value={clientForm.email} onChange={(event) => setClientForm({ ...clientForm, email: event.target.value })} /></label>
            <label>Teléfono<input value={clientForm.telefono} onChange={(event) => setClientForm({ ...clientForm, telefono: event.target.value })} /></label>
            <div className="form-row"><label>RFC<input value={clientForm.rfc} onChange={(event) => setClientForm({ ...clientForm, rfc: event.target.value })} /></label><label>C.P.<input value={clientForm.codigo_postal} onChange={(event) => setClientForm({ ...clientForm, codigo_postal: event.target.value })} /></label></div>
            <label>Régimen fiscal<input value={clientForm.regimen_fiscal} onChange={(event) => setClientForm({ ...clientForm, regimen_fiscal: event.target.value })} /></label>
            <button type="submit" disabled={savingClient}>{savingClient ? 'Guardando…' : 'Crear cliente'}</button>
          </form>
        </SectionPanel>
      </div>

      <div className="module-grid two-columns">
        <SectionPanel title="Pacientes" footer={<span className="muted compact">{selectedClient ? `Cliente: ${selectedClient.nombre}` : 'Todos los clientes'}</span>}>
          <form className="toolbar" onSubmit={(event) => { event.preventDefault(); setPatientPage(1); void patients.reload(); }}>
            <input value={patientSearch} onChange={(event) => setPatientSearch(event.target.value)} placeholder="Buscar paciente" />
            <button type="submit" className="secondary">Buscar</button>
            <button type="button" className="ghost" onClick={() => { setSelectedClientId(''); setSelectedPatientId(''); }}>Ver todos</button>
          </form>
          <InlineState loading={patients.loading} error={patients.error} empty={patientItems.length === 0} emptyTitle="Sin pacientes" emptyDescription="Selecciona o crea un cliente y agrega su paciente.">
            <div className="table-wrap"><table><thead><tr><th>Paciente</th><th>Nacimiento</th><th>Contacto</th></tr></thead><tbody>{patientItems.map((patient) => (
              <tr key={patient.id} className={patient.id === selectedPatientId ? 'selected-row' : undefined} onClick={() => { setSelectedPatientId(patient.id); setSelectedClientId(patient.cliente_id); }}>
                <td><strong>{patient.nombre}</strong><br /><span className="compact-id">{patient.id}</span></td><td>{patient.fecha_nacimiento ?? '—'}</td><td>{patient.email ?? '—'}<br />{patient.telefono ?? '—'}</td>
              </tr>
            ))}</tbody></table></div>
          </InlineState>
          <Pagination page={patientPage} pageSize={PAGE_SIZE} total={patientItems.length} onPageChange={setPatientPage} onPageSizeChange={() => undefined} />
        </SectionPanel>

        <SectionPanel title="Crear paciente" footer={<span className="muted compact">{selectedClient ? selectedClient.nombre : 'Selecciona un cliente'}</span>}>
          <form className="crud-form" onSubmit={submitPatient}>
            <label>Nombre<input required value={patientForm.nombre} onChange={(event) => setPatientForm({ ...patientForm, nombre: event.target.value })} /></label>
            <label>Fecha nacimiento<input type="date" value={patientForm.fecha_nacimiento} onChange={(event) => setPatientForm({ ...patientForm, fecha_nacimiento: event.target.value })} /></label>
            <label>Email<input type="email" value={patientForm.email} onChange={(event) => setPatientForm({ ...patientForm, email: event.target.value })} /></label>
            <label>Teléfono<input value={patientForm.telefono} onChange={(event) => setPatientForm({ ...patientForm, telefono: event.target.value })} /></label>
            <button type="submit" disabled={savingPatient || !selectedClientId}>{savingPatient ? 'Guardando…' : 'Crear paciente'}</button>
          </form>
        </SectionPanel>
      </div>

      <SectionPanel title="Recetas ópticas" footer={<span className="muted compact">{selectedPatient ? `Paciente: ${selectedPatient.nombre}` : 'Selecciona un paciente para filtrar'}</span>}>
        <InlineState loading={prescriptions.loading} error={prescriptions.error} empty={prescriptionItems.length === 0} emptyTitle="Sin recetas" emptyDescription="Captura la primera receta del paciente seleccionado.">
          <div className="table-wrap"><table><thead><tr><th>Fecha</th><th>OD</th><th>OI</th><th>DNP / Altura</th><th>Observaciones</th></tr></thead><tbody>{prescriptionItems.map((rx) => (
            <tr key={rx.id}><td>{rx.fecha}</td><td>Esf {rx.od_esfera ?? '—'} / Cil {rx.od_cilindro ?? '—'} / Eje {rx.od_eje ?? '—'} / Add {rx.od_adicion ?? '—'}</td><td>Esf {rx.oi_esfera ?? '—'} / Cil {rx.oi_cilindro ?? '—'} / Eje {rx.oi_eje ?? '—'} / Add {rx.oi_adicion ?? '—'}</td><td>{rx.dnp ?? '—'} / {rx.altura ?? '—'}</td><td>{rx.observaciones ?? '—'}</td></tr>
          ))}</tbody></table></div>
        </InlineState>
        <Pagination page={prescriptionPage} pageSize={PAGE_SIZE} total={prescriptionItems.length} onPageChange={setPrescriptionPage} onPageSizeChange={() => undefined} />
      </SectionPanel>

      <SectionPanel title="Crear receta óptica" footer={<span className="muted compact">{selectedPatient ? selectedPatient.nombre : 'Selecciona un paciente'}</span>}>
        <form className="crud-form" onSubmit={submitPrescription}>
          <label>Fecha<input type="date" required value={prescriptionForm.fecha} onChange={(event) => setPrescriptionForm({ ...prescriptionForm, fecha: event.target.value })} /></label>
          <div className="optical-grid">
            {(['od_esfera','od_cilindro','od_eje','od_adicion','oi_esfera','oi_cilindro','oi_eje','oi_adicion','dnp','altura'] as const).map((field) => <label key={field}>{field.toUpperCase()}<input type="number" step="0.01" value={prescriptionForm[field]} onChange={(event) => setPrescriptionForm({ ...prescriptionForm, [field]: event.target.value })} /></label>)}
          </div>
          <label>Observaciones<textarea value={prescriptionForm.observaciones} onChange={(event) => setPrescriptionForm({ ...prescriptionForm, observaciones: event.target.value })} /></label>
          <button type="submit" disabled={savingPrescription || !selectedPatientId}>{savingPrescription ? 'Guardando…' : 'Crear receta'}</button>
        </form>
      </SectionPanel>
    </section>
  );
}
