# Backend permission catalog

This catalog is generated from `require_permissions([...])` declarations in `backend/app/api/v1/endpoints`.

Use it as the baseline for RBAC role templates and access reviews.

## auditoria

- `auditoria.leer`
- `auditoria.verificar`

## compras

- `compras.aprobar`
- `compras.crear`
- `compras.leer`
- `compras.recibir`
- `compras.solicitudes.generar`

## configuracion

- `configuracion.impuestos.crear`
- `configuracion.impuestos.leer`
- `configuracion.reglas_contables.crear`
- `configuracion.reglas_contables.leer`
- `configuracion.series.crear`
- `configuracion.series.usar`
- `configuracion.tipos_cambio.crear`
- `configuracion.tipos_cambio.leer`

## contabilidad

- `contabilidad.asientos.leer`
- `contabilidad.cuentas.crear`
- `contabilidad.cuentas.leer`
- `contabilidad.periodos.cerrar`
- `contabilidad.periodos.crear`
- `contabilidad.periodos.leer`

## crm

- `crm.citas.crear`
- `crm.citas.estado`
- `crm.citas.leer`
- `crm.recordatorios.crear`
- `crm.recordatorios.leer`

## facturacion

- `facturacion.cancelar`
- `facturacion.emitir`
- `facturacion.leer`

## garantias

- `garantias.crear`
- `garantias.leer`
- `garantias.reclamaciones.crear`
- `garantias.reclamaciones.resolver`

## inventario

- `inventario.alertas.leer`
- `inventario.entrada`
- `inventario.leer`
- `inventario.salida`

## laboratorio

- `laboratorio.consumos.registrar`
- `laboratorio.control_calidad.registrar`
- `laboratorio.etapas.completar`
- `laboratorio.ordenes.crear`
- `laboratorio.ordenes.entregar`
- `laboratorio.ordenes.leer`
- `laboratorio.ordenes.procesar`

## nomina

- `nomina.calcular`
- `nomina.confirmar`
- `nomina.empleados.crear`
- `nomina.leer`
- `nomina.periodos.crear`

## observabilidad

- `observabilidad.mantenimiento.ejecutar`
- `observabilidad.metricas.leer`

## outbox

- `outbox.eventos.crear`
- `outbox.eventos.leer`
- `outbox.eventos.procesar`

## presupuestos

- `presupuestos.centros_costo.crear`
- `presupuestos.comprometer`
- `presupuestos.crear`

## productos

- `productos.crear`
- `productos.leer`

## reportes

- `reportes.contabilidad.leer`
- `reportes.inventario.leer`
- `reportes.ventas.leer`

## tesoreria

- `tesoreria.conciliar`
- `tesoreria.cuentas.crear`
- `tesoreria.movimientos.crear`
- `tesoreria.movimientos.importar`
- `tesoreria.movimientos.leer`

## usuarios

- `usuarios.crear`
- `usuarios.editar`
- `usuarios.eliminar`
- `usuarios.ver`

## ventas

- `ventas.confirmar`
- `ventas.crear`
- `ventas.devolver`
- `ventas.leer`
