import type { PageKey } from '../types/navigation';

/**
 * Permiso de LECTURA requerido para mostrar cada sección del menú.
 * Las claves coinciden exactamente con los permisos declarados en el backend
 * (app/api/deps.py::require_permissions en app/api/v1/endpoints/*).
 */
export const moduleReadPermissions: Record<PageKey, string[]> = {
  dashboard: [],
  users: ['usuarios.ver'],
  products: ['productos.leer'],
  inventory: ['inventario.leer'],
  sales: ['ventas.leer'],
  purchases: ['compras.leer'],
  crm: ['crm.clientes.leer', 'crm.citas.leer'],
  patients: ['crm.pacientes.leer'],
  lab: ['laboratorio.ordenes.leer'],
  finance: ['contabilidad.asientos.leer', 'tesoreria.movimientos.leer', 'presupuestos.leer'],
  billing: ['facturacion.leer', 'garantias.leer'],
  reports: ['reportes.ventas.leer', 'reportes.inventario.leer', 'reportes.contabilidad.leer'],
  operations: ['auditoria.leer', 'outbox.eventos.leer', 'observabilidad.metricas.leer'],
  admin: [
    'configuracion.impuestos.leer',
    'configuracion.series.crear',
    'nomina.leer',
    'privacidad.solicitudes.exportar',
  ],
};
