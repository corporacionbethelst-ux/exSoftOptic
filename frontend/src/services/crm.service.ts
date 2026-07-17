import type { ID } from '../types/common';
import type { CitaEstado, CitaOptica, CitaOpticaPayload, RecordatorioCliente, RecordatorioClientePayload } from '../types/crm';
import { apiRequest } from './http/httpClient';

export type AppointmentListParams = {
  skip?: number;
  limit?: number;
};

function appointmentQuery(params: AppointmentListParams = {}) {
  const query = new URLSearchParams();
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 50));
  return query.toString();
}

export const crmService = {
  appointments: (params?: AppointmentListParams) => apiRequest<CitaOptica[]>(`/api/v1/crm/citas?${appointmentQuery(params)}`),
  createAppointment: (payload: CitaOpticaPayload) => apiRequest<CitaOptica>('/api/v1/crm/citas', { method: 'POST', body: JSON.stringify(payload) }),
  changeAppointmentStatus: (id: ID, status: CitaEstado) => apiRequest<CitaOptica>(`/api/v1/crm/citas/${id}/estado/${status}`, { method: 'POST' }),
  pendingReminders: (limit = 100) => apiRequest<RecordatorioCliente[]>(`/api/v1/crm/recordatorios/pendientes?limit=${limit}`),
  createReminder: (payload: RecordatorioClientePayload) => apiRequest<RecordatorioCliente>('/api/v1/crm/recordatorios', { method: 'POST', body: JSON.stringify(payload) }),
};
