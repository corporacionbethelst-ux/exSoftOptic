import type { ID } from '../types/common';
import type { Empleado, EmpleadoPayload, Impuesto, ImpuestoPayload, NominaConfirmarPayload, NominaPeriodo, NominaPeriodoPayload, ReglaContable, ReglaContablePayload, SerieFolio, SerieFolioPayload, TipoCambio, TipoCambioPayload } from '../types/admin';
import { apiRequest } from './http/httpClient';

type ListParams = { skip?: number; limit?: number };
function query(params: ListParams = {}) { const q = new URLSearchParams(); q.set('skip', String(params.skip ?? 0)); q.set('limit', String(params.limit ?? 100)); return q.toString(); }

export const adminService = {
  taxes: (params?: ListParams) => apiRequest<Impuesto[]>(`/api/v1/configuracion/impuestos?${query(params)}`),
  createTax: (payload: ImpuestoPayload) => apiRequest<Impuesto>('/api/v1/configuracion/impuestos', { method: 'POST', body: JSON.stringify(payload) }),
  createSeries: (payload: SerieFolioPayload) => apiRequest<SerieFolio>('/api/v1/configuracion/series', { method: 'POST', body: JSON.stringify(payload) }),
  nextFolio: (documento: string, serie: string) => apiRequest<{ folio: string }>(`/api/v1/configuracion/series/${documento}/${serie}/siguiente`, { method: 'POST' }),
  createExchangeRate: (payload: TipoCambioPayload) => apiRequest<TipoCambio>('/api/v1/configuracion/tipos-cambio', { method: 'POST', body: JSON.stringify(payload) }),
  exchangeRate: (moneda_origen: string, moneda_destino: string) => apiRequest<TipoCambio>(`/api/v1/configuracion/tipos-cambio?moneda_origen=${moneda_origen}&moneda_destino=${moneda_destino}`),
  rules: (params?: ListParams) => apiRequest<ReglaContable[]>(`/api/v1/configuracion/reglas-contables?${query(params)}`),
  createRule: (payload: ReglaContablePayload) => apiRequest<ReglaContable>('/api/v1/configuracion/reglas-contables', { method: 'POST', body: JSON.stringify(payload) }),
  employees: (params?: ListParams) => apiRequest<Empleado[]>(`/api/v1/nomina/empleados?${query(params)}`),
  createEmployee: (payload: EmpleadoPayload) => apiRequest<Empleado>('/api/v1/nomina/empleados', { method: 'POST', body: JSON.stringify(payload) }),
  payrollPeriods: (params?: ListParams) => apiRequest<NominaPeriodo[]>(`/api/v1/nomina/periodos?${query(params)}`),
  createPayrollPeriod: (payload: NominaPeriodoPayload) => apiRequest<NominaPeriodo>('/api/v1/nomina/periodos', { method: 'POST', body: JSON.stringify(payload) }),
  calculatePayroll: (id: ID) => apiRequest<NominaPeriodo>(`/api/v1/nomina/periodos/${id}/calcular`, { method: 'POST' }),
  confirmPayroll: (id: ID, payload: NominaConfirmarPayload) => apiRequest<NominaPeriodo>(`/api/v1/nomina/periodos/${id}/confirmar`, { method: 'POST', body: JSON.stringify(payload) }),
};
