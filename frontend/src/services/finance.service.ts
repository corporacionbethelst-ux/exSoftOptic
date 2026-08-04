import type { ID } from '../types/common';
import type { AsientoContable, CentroCosto, CentroCostoPayload, ComprometerPresupuestoPayload, ConciliacionPayload, CuentaBancaria, CuentaBancariaPayload, CuentaContable, CuentaContablePayload, MovimientoBancario, MovimientoBancarioPayload, PeriodoContable, PeriodoContablePayload, Presupuesto, PresupuestoPayload } from '../types/finance';
import { apiRequest } from './http/httpClient';

type ListParams = { skip?: number; limit?: number; cuenta_bancaria_id?: ID };
function query(params: ListParams = {}) { const q = new URLSearchParams(); q.set('skip', String(params.skip ?? 0)); q.set('limit', String(params.limit ?? 100)); if (params.cuenta_bancaria_id) q.set('cuenta_bancaria_id', params.cuenta_bancaria_id); return q.toString(); }

export const financeService = {
  accounts: (params?: ListParams) => apiRequest<CuentaContable[]>(`/api/v1/contabilidad/cuentas?${query(params)}`),
  createAccount: (payload: CuentaContablePayload) => apiRequest<CuentaContable>('/api/v1/contabilidad/cuentas', { method: 'POST', body: JSON.stringify(payload) }),
  entries: (params?: ListParams) => apiRequest<AsientoContable[]>(`/api/v1/contabilidad/asientos?${query(params)}`),
  periods: (params?: ListParams) => apiRequest<PeriodoContable[]>(`/api/v1/contabilidad/periodos?${query(params)}`),
  createPeriod: (payload: PeriodoContablePayload) => apiRequest<PeriodoContable>('/api/v1/contabilidad/periodos', { method: 'POST', body: JSON.stringify(payload) }),
  changePeriodStatus: (id: ID, estado: 'ABIERTO' | 'CERRADO') => apiRequest<PeriodoContable>(`/api/v1/contabilidad/periodos/${id}/estado`, { method: 'PATCH', body: JSON.stringify({ estado }) }),
  bankAccounts: (params?: ListParams) => apiRequest<CuentaBancaria[]>(`/api/v1/tesoreria/cuentas-bancarias?${query(params)}`),
  createBankAccount: (payload: CuentaBancariaPayload) => apiRequest<CuentaBancaria>('/api/v1/tesoreria/cuentas-bancarias', { method: 'POST', body: JSON.stringify(payload) }),
  pendingBankMovements: (params?: ListParams) => apiRequest<MovimientoBancario[]>(`/api/v1/tesoreria/movimientos/pendientes?${query(params)}`),
  createBankMovement: (payload: MovimientoBancarioPayload) => apiRequest<MovimientoBancario>('/api/v1/tesoreria/movimientos', { method: 'POST', body: JSON.stringify(payload) }),
  reconcile: (payload: ConciliacionPayload) => apiRequest<unknown>('/api/v1/tesoreria/conciliaciones', { method: 'POST', body: JSON.stringify(payload) }),
  costCenters: (params?: ListParams) => apiRequest<CentroCosto[]>(`/api/v1/presupuestos/centros-costo?${query(params)}`),
  createCostCenter: (payload: CentroCostoPayload) => apiRequest<CentroCosto>('/api/v1/presupuestos/centros-costo', { method: 'POST', body: JSON.stringify(payload) }),
  budgets: (params?: ListParams) => apiRequest<Presupuesto[]>(`/api/v1/presupuestos/?${query(params)}`),
  createBudget: (payload: PresupuestoPayload) => apiRequest<Presupuesto>('/api/v1/presupuestos/', { method: 'POST', body: JSON.stringify(payload) }),
  commitBudget: (payload: ComprometerPresupuestoPayload) => apiRequest<Presupuesto>('/api/v1/presupuestos/comprometer', { method: 'POST', body: JSON.stringify(payload) }),
};
