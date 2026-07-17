import type { ID } from '../types/common';
import type { Cliente, ClientePayload, Paciente, PacientePayload, RecetaOptica, RecetaOpticaPayload } from '../types/patients';
import { apiRequest } from './http/httpClient';

type ListParams = {
  search?: string;
  cliente_id?: ID;
  paciente_id?: ID;
  skip?: number;
  limit?: number;
};

function buildQuery(params: ListParams = {}) {
  const query = new URLSearchParams();
  if (params.search) query.set('search', params.search);
  if (params.cliente_id) query.set('cliente_id', params.cliente_id);
  if (params.paciente_id) query.set('paciente_id', params.paciente_id);
  query.set('skip', String(params.skip ?? 0));
  query.set('limit', String(params.limit ?? 50));
  return query.toString();
}

export const patientsService = {
  clients: (params?: ListParams) => apiRequest<Cliente[]>(`/api/v1/crm/clientes?${buildQuery(params)}`),
  createClient: (payload: ClientePayload) => apiRequest<Cliente>('/api/v1/crm/clientes', { method: 'POST', body: JSON.stringify(payload) }),
  patients: (params?: ListParams) => apiRequest<Paciente[]>(`/api/v1/crm/pacientes?${buildQuery(params)}`),
  createPatient: (payload: PacientePayload) => apiRequest<Paciente>('/api/v1/crm/pacientes', { method: 'POST', body: JSON.stringify(payload) }),
  prescriptions: (params?: ListParams) => apiRequest<RecetaOptica[]>(`/api/v1/crm/recetas?${buildQuery(params)}`),
  createPrescription: (payload: RecetaOpticaPayload) => apiRequest<RecetaOptica>('/api/v1/crm/recetas', { method: 'POST', body: JSON.stringify(payload) }),
};
