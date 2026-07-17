import type { FormEvent } from 'react';
import { useCallback, useState } from 'react';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { crmService } from '../../services';
import type { CitaEstado, CitaOpticaPayload, RecordatorioClientePayload } from '../../types/crm';
import { useApiResource } from '../../hooks/useApiResource';
import { useAuth } from '../auth/AuthContext';

const APPOINTMENT_STATES: CitaEstado[] = ['PROGRAMADA', 'CONFIRMADA', 'EN_PROCESO', 'COMPLETADA', 'CANCELADA', 'NO_ASISTIO'];

function localDateTime(offsetMinutes = 0) {
  const date = new Date(Date.now() + offsetMinutes * 60_000);
  date.setSeconds(0, 0);
  return date.toISOString().slice(0, 16);
}

function toIsoLocal(value: string) {
  return new Date(value).toISOString();
}

function appointmentTone(status: string): 'success' | 'warning' | 'danger' | 'neutral' {
  if (status === 'COMPLETADA') return 'success';
  if (status === 'CANCELADA' || status === 'NO_ASISTIO') return 'danger';
  if (status === 'CONFIRMADA' || status === 'EN_PROCESO') return 'warning';
  return 'neutral';
}

export function CrmPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [sucursalId, setSucursalId] = useState(user?.sucursal_id ?? '');
  const [folio, setFolio] = useState(() => `CITA-${Date.now()}`);
  const [clienteId, setClienteId] = useState('');
  const [pacienteId, setPacienteId] = useState('');
  const [optometristaId, setOptometristaId] = useState('');
  const [fechaInicio, setFechaInicio] = useState(() => localDateTime(60));
  const [fechaFin, setFechaFin] = useState(() => localDateTime(90));
  const [tipo, setTipo] = useState('EXAMEN_VISUAL');
  const [motivo, setMotivo] = useState('Revisión visual');
  const [observaciones, setObservaciones] = useState('');
  const [reminderClientId, setReminderClientId] = useState('');
  const [reminderPatientId, setReminderPatientId] = useState('');
  const [reminderAppointmentId, setReminderAppointmentId] = useState('');
  const [reminderType, setReminderType] = useState('CITA');
  const [reminderChannel, setReminderChannel] = useState('EMAIL');
  const [reminderDate, setReminderDate] = useState(() => localDateTime(30));
  const [reminderMessage, setReminderMessage] = useState('Recordatorio de cita óptica programada.');
  const [operationMessage, setOperationMessage] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [savingAppointment, setSavingAppointment] = useState(false);
  const [savingReminder, setSavingReminder] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null);
  const skip = (page - 1) * pageSize;

  const loadAppointments = useCallback(() => crmService.appointments({ skip, limit: pageSize }), [pageSize, skip]);
  const loadReminders = useCallback(() => crmService.pendingReminders(100), []);
  const appointments = useApiResource(loadAppointments);
  const reminders = useApiResource(loadReminders);
  const appointmentItems = appointments.data ?? [];
  const reminderItems = reminders.data ?? [];

  async function submitAppointment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingAppointment(true);
    setFormError(null);
    setOperationMessage(null);
    try {
      const payload: CitaOpticaPayload = {
        sucursal_id: sucursalId,
        cliente_id: clienteId,
        paciente_id: pacienteId || null,
        optometrista_id: optometristaId || null,
        folio,
        fecha_inicio: toIsoLocal(fechaInicio),
        fecha_fin: toIsoLocal(fechaFin),
        tipo,
        motivo: motivo || null,
        observaciones: observaciones || null,
      };
      await crmService.createAppointment(payload);
      setOperationMessage('Cita creada correctamente. Puedes cambiar su estado desde el listado.');
      setFolio(`CITA-${Date.now()}`);
      await appointments.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo crear la cita');
    } finally {
      setSavingAppointment(false);
    }
  }

  async function changeStatus(id: string, status: CitaEstado) {
    setUpdatingStatus(id);
    setFormError(null);
    try {
      await crmService.changeAppointmentStatus(id, status);
      setOperationMessage(`Cita actualizada a ${status}.`);
      await appointments.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo cambiar el estado de la cita');
    } finally {
      setUpdatingStatus(null);
    }
  }

  async function submitReminder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingReminder(true);
    setFormError(null);
    setOperationMessage(null);
    try {
      const payload: RecordatorioClientePayload = {
        cliente_id: reminderClientId,
        paciente_id: reminderPatientId || null,
        cita_id: reminderAppointmentId || null,
        tipo: reminderType,
        canal: reminderChannel,
        programado_para: toIsoLocal(reminderDate),
        mensaje: reminderMessage,
      };
      await crmService.createReminder(payload);
      setOperationMessage('Recordatorio creado correctamente.');
      setReminderDate(localDateTime(30));
      await reminders.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo crear el recordatorio');
    } finally {
      setSavingReminder(false);
    }
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="CRM"
        title="Citas y recordatorios"
        description="Fase CRM: agenda óptica, gestión de estados de cita y recordatorios pendientes por cliente/paciente."
      />

      {operationMessage ? <div className="alert success">{operationMessage}</div> : null}
      {formError ? <div className="alert error">{formError}</div> : null}

      <SectionPanel title="Agenda de citas" footer={<span className="muted compact">{appointmentItems.length} en esta página</span>}>
        <InlineState loading={appointments.loading} error={appointments.error} empty={appointmentItems.length === 0} emptyTitle="Sin citas" emptyDescription="Crea una cita usando un cliente existente generado desde ventas o demo seed.">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Folio</th><th>Estado</th><th>Inicio</th><th>Fin</th><th>Tipo</th><th>Cliente</th><th>Cambiar estado</th></tr></thead>
              <tbody>
                {appointmentItems.map((appointment) => (
                  <tr key={appointment.id}>
                    <td>{appointment.folio}</td>
                    <td><StatusBadge tone={appointmentTone(appointment.estado)}>{appointment.estado}</StatusBadge></td>
                    <td>{new Date(appointment.fecha_inicio).toLocaleString()}</td>
                    <td>{new Date(appointment.fecha_fin).toLocaleString()}</td>
                    <td>{appointment.tipo}</td>
                    <td className="compact-id">{appointment.cliente_id}</td>
                    <td>
                      <select disabled={updatingStatus === appointment.id} value={appointment.estado} onChange={(event) => void changeStatus(appointment.id, event.target.value as CitaEstado)}>
                        {APPOINTMENT_STATES.map((state) => <option key={state} value={state}>{state}</option>)}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={page}
            pageSize={pageSize}
            total={Math.max(appointmentItems.length + skip, page * pageSize)}
            onPageChange={setPage}
            onPageSizeChange={(nextPageSize) => {
              setPage(1);
              setPageSize(nextPageSize);
            }}
          />
        </InlineState>
      </SectionPanel>

      <div className="module-grid">
        <SectionPanel title="Nueva cita" description="Agenda una cita con cliente existente y paciente/optometrista opcionales.">
          <form className="crud-form" onSubmit={(event) => void submitAppointment(event)}>
            <label>Folio<input value={folio} onChange={(event) => setFolio(event.target.value)} required /></label>
            <label>Sucursal ID<input value={sucursalId} onChange={(event) => setSucursalId(event.target.value)} required /></label>
            <label>Cliente ID<input value={clienteId} onChange={(event) => setClienteId(event.target.value)} required /></label>
            <label>Paciente ID<input value={pacienteId} onChange={(event) => setPacienteId(event.target.value)} /></label>
            <label>Optometrista ID<input value={optometristaId} onChange={(event) => setOptometristaId(event.target.value)} /></label>
            <label>Tipo<input value={tipo} onChange={(event) => setTipo(event.target.value)} required /></label>
            <label>Inicio<input type="datetime-local" value={fechaInicio} onChange={(event) => setFechaInicio(event.target.value)} required /></label>
            <label>Fin<input type="datetime-local" value={fechaFin} onChange={(event) => setFechaFin(event.target.value)} required /></label>
            <label className="wide-field">Motivo<input value={motivo} onChange={(event) => setMotivo(event.target.value)} /></label>
            <label className="wide-field">Observaciones<textarea value={observaciones} onChange={(event) => setObservaciones(event.target.value)} /></label>
            <div className="form-actions wide-field"><button className="primary-button" disabled={savingAppointment}>{savingAppointment ? 'Guardando…' : 'Crear cita'}</button></div>
          </form>
        </SectionPanel>

        <SectionPanel title="Recordatorios pendientes" description="Lista y programa recordatorios para seguimiento de clientes.">
          <InlineState loading={reminders.loading} error={reminders.error} empty={reminderItems.length === 0} emptyTitle="Sin recordatorios" emptyDescription="Programa recordatorios para aparecer aquí.">
            <div className="list-stack">
              {reminderItems.map((reminder) => (
                <div className="row-card" key={reminder.id}>
                  <div>
                    <strong>{reminder.tipo} · {reminder.canal}</strong>
                    <span>{new Date(reminder.programado_para).toLocaleString()} · {reminder.mensaje}</span>
                  </div>
                  <StatusBadge tone="warning">{reminder.estado}</StatusBadge>
                </div>
              ))}
            </div>
          </InlineState>
          <form className="crud-form reminder-form" onSubmit={(event) => void submitReminder(event)}>
            <label>Cliente ID<input value={reminderClientId} onChange={(event) => setReminderClientId(event.target.value)} required /></label>
            <label>Paciente ID<input value={reminderPatientId} onChange={(event) => setReminderPatientId(event.target.value)} /></label>
            <label>Cita ID<input value={reminderAppointmentId} onChange={(event) => setReminderAppointmentId(event.target.value)} /></label>
            <label>Tipo<input value={reminderType} onChange={(event) => setReminderType(event.target.value)} required /></label>
            <label>Canal<input value={reminderChannel} onChange={(event) => setReminderChannel(event.target.value)} required /></label>
            <label>Programado<input type="datetime-local" value={reminderDate} onChange={(event) => setReminderDate(event.target.value)} required /></label>
            <label className="wide-field">Mensaje<textarea value={reminderMessage} onChange={(event) => setReminderMessage(event.target.value)} required /></label>
            <div className="form-actions wide-field"><button className="secondary-button" disabled={savingReminder}>{savingReminder ? 'Guardando…' : 'Crear recordatorio'}</button></div>
          </form>
        </SectionPanel>
      </div>
    </section>
  );
}
