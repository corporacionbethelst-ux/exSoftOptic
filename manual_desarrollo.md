# Manual de desarrollo del backend de exSoftOptic

> Documento orientado a desarrolladores que necesitan entender la arquitectura, la lógica de negocio y la forma correcta de extender el backend actual.

## 1. Propósito del sistema

`exSoftOptic` es un sistema de gestión para ópticas. El backend está desarrollado con FastAPI, SQLAlchemy asíncrono y PostgreSQL como base transaccional principal. El dominio actual cubre:

- Empresas, sucursales, usuarios, roles y sesiones.
- Catálogo de productos, categorías y marcas.
- Inventario con existencias, capas PEPS/FIFO y kardex.
- Ventas, pagos, devoluciones, clientes, pacientes y recetas ópticas.
- Compras, órdenes de compra, recepciones y solicitudes por stock mínimo.
- Contabilidad de doble partida, periodos, cuentas y reportes financieros.
- Facturación electrónica con proveedor mock o HTTP.
- Laboratorio óptico con etapas, consumo de materiales y control de calidad.
- Garantías y reclamaciones.
- Nómina, tesorería, presupuestos, CRM, auditoría, outbox e idempotencia.

El backend está organizado para que los endpoints HTTP sean delgados y la lógica de negocio viva en servicios de dominio.

---

## 2. Estructura general del backend

La carpeta principal del backend es `backend/`.

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   ├── core/
│   ├── crud/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── workers/
│   └── main.py
├── tests/
├── scripts/
├── alembic/
├── Makefile
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```

### Responsabilidad por carpeta

| Carpeta / archivo | Responsabilidad |
|---|---|
| `app/main.py` | Crea la app FastAPI, registra middlewares, routers, health checks y documentación. |
| `app/api/deps.py` | Dependencias de autenticación, permisos, scope por empresa/sucursal y usuario actual. |
| `app/api/v1/router.py` | Agrega todos los routers por módulo bajo `/api/v1`. |
| `app/api/v1/endpoints/` | Endpoints HTTP por módulo. Deben delegar la lógica al servicio correspondiente. |
| `app/core/` | Configuración, conexión DB, seguridad, métricas, rate limit, errores, seed. |
| `app/models/` | Modelos SQLAlchemy y relaciones ORM. Representan tablas reales. |
| `app/schemas/` | Schemas Pydantic de request/response. Representan el contrato del API. |
| `app/services/` | Lógica de negocio y orquestación transaccional. |
| `app/crud/` | CRUD genérico y usuario legacy/específico. |
| `app/workers/` | Procesos background, principalmente outbox worker. |
| `tests/` | Suite automatizada del backend. |
| `scripts/` | Verificadores, utilidades operativas, seeds RBAC, OpenAPI, migraciones, backup, etc. |

---

## 3. Capas del backend

El backend usa una separación por capas bastante clásica:

```text
HTTP request
   ↓
Endpoint FastAPI
   ↓
Dependencias: auth, permisos, DB session
   ↓
Schema Pydantic de entrada
   ↓
Servicio de dominio
   ↓
Modelos SQLAlchemy
   ↓
Base de datos
   ↓
Schema Pydantic de respuesta
   ↓
HTTP response
```

### 3.1 Endpoints

Los endpoints están en `app/api/v1/endpoints/`. En general:

1. Reciben `payload` Pydantic.
2. Obtienen `db` con `Depends(get_db)`.
3. Obtienen `current_user` con `Depends(get_current_active_user)`.
4. Declaran permisos con `Depends(require_permissions([...]))`.
5. Llaman al servicio de dominio.
6. Convierten errores de negocio (`ValueError`) en HTTP errors.
7. Registran auditoría cuando aplica.

Ejemplo conceptual:

```python
@router.post("/", response_model=VentaResponse)
async def crear_venta(payload: VentaCreate, db: AsyncSession, current_user: Usuario):
    try:
        return await SalesService(db).crear_venta(
            empresa_id=current_user.empresa_id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```

### 3.2 Schemas

Los schemas Pydantic están en `app/schemas/`. Sirven para:

- Validar entrada.
- Definir respuestas.
- Calcular propiedades simples de payload, por ejemplo `importe` de una línea.
- Aislar el contrato HTTP del modelo SQLAlchemy.

Importante: cuando un schema tiene `lineas: list[...]`, eso representa JSON de entrada/salida. No significa que se guarde como JSON en la base de datos. Normalmente se transforma a filas relacionales en servicios.

### 3.3 Servicios

Los servicios están en `app/services/`. Son la capa más importante para entender la lógica de negocio.

Reglas generales:

- Validan estados de negocio.
- Calculan totales.
- Bloquean registros cuando hay concurrencia (`with_for_update`).
- Coordinan varios módulos, por ejemplo venta + inventario + contabilidad + outbox.
- Crean entidades hijas con FK explícita y `add_all(...)`.
- Devuelven entidades recargadas con `selectinload(...)` cuando se necesita detalle.

### 3.4 Modelos

Los modelos SQLAlchemy están en `app/models/`. Representan tablas y relaciones. Casi todas las entidades heredan de `BaseModel`, que aporta:

- `id` UUID.
- `created_at`.
- `updated_at`.
- `deleted_at`.
- `is_active`.

### 3.5 Base de datos

La conexión se define en `app/core/database.py` usando:

- `create_async_engine`.
- `async_sessionmaker`.
- `AsyncSession`.
- `expire_on_commit=False`.
- `autoflush=False`.

La dependencia `get_db()` abre sesión, hace commit si todo va bien, rollback si hay error y cierra la sesión.

---

## 4. Configuración y arranque

### 4.1 Variables de entorno

La configuración vive en `app/core/config.py` y se carga con `pydantic-settings` desde `.env`.

Variables relevantes:

| Variable | Uso |
|---|---|
| `SECRET_KEY` | Firma de tokens JWT. |
| `DATABASE_URL` | URL async de PostgreSQL. |
| `MONGODB_URL` | Configuración MongoDB para módulo clínico/futuro. |
| `REDIS_URL` | Redis para cache o tareas operativas. |
| `CORS_ORIGINS` | Orígenes permitidos para frontend. |
| `CFDI_PROVIDER` | Proveedor de facturación: `MOCK` o HTTP. |
| `BANKING_PROVIDER` | Proveedor bancario: CSV o HTTP. |
| `DEBUG` | Activa SQL echo y modo debug. |
| `ENVIRONMENT` | Ambiente lógico: development, test, production. |

### 4.2 Comandos principales

Desde `backend/`:

```bash
make install          # instala dependencias base
make dev              # instala dependencias de desarrollo
make run              # levanta FastAPI con uvicorn
make migrate-up       # aplica migraciones Alembic
make seed             # carga/actualiza datos demo
make test             # ejecuta pytest con cobertura
make verify           # verificación completa del backend
make verify-fast      # verificación rápida sin pytest completo
```

### 4.3 URLs locales

Con `make run`:

| URL | Uso |
|---|---|
| `http://localhost:8000/` | Root del backend. |
| `http://localhost:8000/docs` | Swagger UI. |
| `http://localhost:8000/redoc` | ReDoc. |
| `http://localhost:8000/health` | Health simple. |
| `http://localhost:8000/ready` | Verifica conectividad con DB. |
| `http://localhost:8000/api/v1/...` | API versionada. |

---

## 5. Seguridad, usuarios y permisos

### 5.1 Autenticación

El login está en `/api/v1/auth/login`. El flujo general es:

1. Endpoint recibe `LoginRequest`.
2. `AuthService.login` autentica usuario con `crud_usuario.authenticate`.
3. Se crea `access_token` y `refresh_token` JWT.
4. Se guarda una sesión en tabla `sesiones` con hash del token.
5. El response devuelve tokens y datos de usuario.

El token contiene:

- `sub` / `user_id`.
- `username`.
- `email`.
- `rol`.
- `sucursal_id`.
- `empresa_id`.
- tipo (`access` o `refresh`).

### 5.2 Sesiones

Aunque el JWT sea válido, el backend verifica que exista una sesión activa asociada al hash del token. Esto permite:

- Logout individual.
- Logout de todos los dispositivos.
- Invalidar sesiones.
- Controlar actividad.

### 5.3 Permisos RBAC

Los endpoints usan `require_permissions([...])`. La lógica permite:

- `SUPER_ADMIN`: acceso total.
- Permiso `*`: acceso total.
- Permiso exacto, por ejemplo `ventas.crear`.
- Wildcard por módulo, por ejemplo `ventas.*`.

Ejemplos de permisos:

```text
ventas.crear
ventas.leer
ventas.confirmar
compras.crear
compras.recibir
inventario.entrada
contabilidad.asientos.leer
```

### 5.4 Scope por empresa y sucursal

La mayoría de servicios reciben `empresa_id=current_user.empresa_id`. Esto evita operaciones cross-tenant. Algunas dependencias también permiten validar sucursal cuando aplique.

Regla importante: **nunca se debe confiar en `empresa_id` enviado por el frontend para operaciones multiempresa**. Debe salir del usuario autenticado.

---

## 6. Modelo base y patrones de persistencia

### 6.1 UUIDs

Las entidades usan UUID como llave primaria. Esto facilita:

- Identificadores no secuenciales.
- Integración externa.
- Menor exposición del volumen de datos.

### 6.2 Soft delete

`BaseModel` incluye `deleted_at` e `is_active`, aunque no todos los servicios aplican soft delete todavía. Al extender el sistema, mantener este patrón.

### 6.3 Relaciones cabecera-detalle

Muchas operaciones usan patrón cabecera-detalle:

| Módulo | Cabecera | Detalle |
|---|---|---|
| Ventas | `Venta` | `VentaLinea` |
| Ventas | `Venta` | `PagoVenta` |
| Devoluciones | `DevolucionVenta` | `DevolucionVentaLinea` |
| Compras | `OrdenCompra` | `OrdenCompraLinea` |
| Recepciones | `RecepcionCompra` | `RecepcionCompraLinea` |
| Facturación | `Factura` | `FacturaLinea` |
| Contabilidad | `AsientoContable` | `LineaAsientoContable` |
| Laboratorio | `OrdenLaboratorio` | `OrdenLaboratorioEtapa` |
| Presupuestos | `Presupuesto` | `PresupuestoLinea` |
| Nómina | `NominaPeriodo` | `NominaRecibo` |

### 6.4 No usar JSON para detalle transaccional

Los detalles de ventas, compras, facturas, asientos, recepciones y devoluciones se guardan como filas en tablas hijas. El JSON aparece en:

- Requests HTTP.
- Responses HTTP.
- Campos operativos como payload de outbox, permisos o configuraciones.

Pero el detalle transaccional principal se modela relacionalmente.

### 6.5 Técnica de inserción de detalles

Patrón recomendado:

```python
cabecera = EntidadCabecera(...)
db.add(cabecera)
await db.flush()  # obtener cabecera.id

lineas = [
    EntidadLinea(cabecera_id=cabecera.id, ...)
    for item in payload.lineas
]

db.add_all(lineas)
await db.flush()
return await self.obtener_entidad(...)
```

Se evita hacer `cabecera.lineas.append(...)` cuando puede disparar lazy loads en contexto async.

---

## 7. Módulos de negocio

## 7.1 Empresas y sucursales

### Entidades principales

- `Empresa`: razón social, RFC, régimen fiscal, código postal, moneda base y configuración contable.
- `Sucursal`: pertenece a empresa, tiene código, nombre, dirección, ciudad, estado y marca de principal.

### Uso de negocio

La empresa define el tenant. Casi todas las entidades tienen `empresa_id`. La sucursal segmenta operaciones físicas como inventario, ventas, compras, laboratorio y tesorería.

### Seed inicial

`app/core/seed.py` crea o actualiza:

- Empresa demo.
- Sucursal principal.
- Roles base.
- Usuario admin.
- Usuarios demo.

El seed es idempotente: puede ejecutarse más de una vez sin duplicar empresa por RFC, sucursal por código, roles por nombre o usuarios por username.

---

## 7.2 Productos, categorías y marcas

### Entidades

- `Producto`: catálogo vendible o consumible.
- `Categoria`: agrupación lógica.
- `Marca`: fabricante/marca comercial.

### Campos importantes de producto

- `empresa_id`.
- `sku`.
- `codigo_barras`.
- `nombre`.
- `tipo`.
- `precio_venta`.
- `costo_promedio`.
- `stock_minimo`.
- `es_servicio`.

### Lógica

Los productos se usan en:

- Líneas de venta.
- Líneas de compra.
- Inventario.
- Laboratorio como material consumido.
- Reportes de inventario y márgenes.

Si `es_servicio=True`, una venta puede no consumir inventario en la confirmación.

---

## 7.3 Inventario

### Entidades

- `InventarioExistencia`: saldo por empresa, sucursal y producto.
- `CapaInventario`: capas de costo disponibles para PEPS/FIFO.
- `KardexMovimiento`: historial de movimientos.

### Entrada de inventario

`InventoryService.entrada(...)`:

1. Valida cantidad positiva y costo no negativo.
2. Obtiene o crea existencia con bloqueo `FOR UPDATE`.
3. Valida producto.
4. Crea una capa de inventario con cantidad inicial/disponible.
5. Aumenta existencia y valor total.
6. Recalcula costo promedio.
7. Crea movimiento kardex tipo `ENTRADA`.

Usos típicos:

- Recepción de compra.
- Devolución de venta.
- Entrada manual.

### Salida PEPS/FIFO

`InventoryService.salida_peps(...)`:

1. Valida cantidad positiva.
2. Bloquea existencia.
3. Verifica inventario suficiente.
4. Lee capas disponibles ordenadas por `created_at` e `id`.
5. Consume de las capas más antiguas primero.
6. Calcula costo total real de salida.
7. Disminuye existencia y valor.
8. Crea movimiento kardex tipo `SALIDA`.

Usos típicos:

- Confirmación de venta.
- Consumo de material en laboratorio.

### Importante

El costo de venta no sale del precio de venta. Sale de las capas PEPS consumidas.

---

## 7.4 Ventas

### Entidades

- `Cliente`.
- `Paciente`.
- `RecetaOptica`.
- `Venta`.
- `VentaLinea`.
- `PagoVenta`.
- `DevolucionVenta`.
- `DevolucionVentaLinea`.

### Crear venta

`SalesService.crear_venta(...)`:

1. Recibe `VentaCreate`.
2. Calcula subtotal desde `payload.lineas`.
3. Suma impuestos para calcular total.
4. Valida que los pagos igualen el total si se enviaron pagos.
5. Resuelve cliente existente o crea cliente nuevo.
6. Resuelve paciente si aplica.
7. Resuelve receta si aplica.
8. Crea cabecera `Venta` en estado `BORRADOR`.
9. Crea filas `VentaLinea` con `venta_id`.
10. Crea filas `PagoVenta`.
11. Devuelve venta con líneas y pagos cargados.

### Confirmar venta

`SalesService.confirmar_venta(...)`:

1. Bloquea venta con `FOR UPDATE`.
2. Requiere estado `BORRADOR`.
3. Requiere al menos una línea.
4. Requiere pagos por el total.
5. Por cada línea no servicio, consume inventario PEPS.
6. Guarda costo real por línea.
7. Genera asiento contable de venta confirmada.
8. Actualiza `costo_total` y `asiento_id`.
9. Cambia estado a `CONFIRMADA`.
10. Encola evento outbox `VentaConfirmada`.

### Asiento de venta confirmada

El asiento estándar:

| Cuenta | Movimiento |
|---|---|
| Cuenta de cobro / caja / CxC | Debe por total de venta |
| Ingreso por venta | Haber por total de venta |
| Costo de venta | Debe por costo PEPS |
| Inventario | Haber por costo PEPS |

### Devolución de venta

`SalesReturnService` maneja devoluciones:

1. Bloquea venta confirmada.
2. Valida líneas devueltas.
3. Calcula importes proporcionales.
4. Reingresa inventario con costo proporcional.
5. Crea `DevolucionVenta` y `DevolucionVentaLinea`.
6. Genera asiento reverso.
7. Encola evento outbox.

---

## 7.5 Compras

### Entidades

- `Proveedor`.
- `OrdenCompra`.
- `OrdenCompraLinea`.
- `RecepcionCompra`.
- `RecepcionCompraLinea`.
- `SolicitudCompra`.
- `SolicitudCompraLinea`.

### Crear orden de compra

`PurchaseService.crear_orden(...)`:

1. Resuelve proveedor existente o crea proveedor.
2. Calcula subtotal desde líneas.
3. Crea cabecera `OrdenCompra` en `BORRADOR`.
4. Crea líneas `OrdenCompraLinea` con `orden_id`.
5. Inicializa `cantidad_recibida=0`.
6. Devuelve orden con líneas.

### Aprobar orden

`PurchaseService.aprobar_orden(...)`:

- Cambia estado de `BORRADOR` a `APROBADA`.

### Recibir orden

`PurchaseService.recibir_orden(...)`:

1. Bloquea orden.
2. Valida que esté `APROBADA` o `PARCIAL`.
3. Crea cabecera `RecepcionCompra`.
4. Por cada línea recibida:
   - Verifica que la línea pertenezca a la orden.
   - Verifica que no exceda la cantidad pendiente.
   - Calcula importe.
   - Ejecuta entrada de inventario.
   - Aumenta `cantidad_recibida` de la línea de orden.
   - Crea `RecepcionCompraLinea`.
5. Genera asiento contable de compra recibida.
6. Actualiza estado de orden a `PARCIAL` o `RECIBIDA`.
7. Encola evento outbox `CompraRecibida`.

### Asiento de compra recibida

| Cuenta | Movimiento |
|---|---|
| Inventario | Debe por total recibido |
| Cuenta por pagar proveedor | Haber por total recibido |

### Solicitudes por stock mínimo

`PurchaseRequisitionService.generar_desde_stock_minimo(...)`:

1. Revisa existencias por debajo del mínimo.
2. Crea `SolicitudCompra`.
3. Crea líneas sugeridas.
4. Devuelve solicitud con detalle.

---

## 7.6 Contabilidad

### Entidades

- `CuentaContable`.
- `PeriodoContable`.
- `AsientoContable`.
- `LineaAsientoContable`.

### Motor contable

`AccountingEngine` centraliza asientos de doble partida.

Reglas:

1. Un asiento debe tener mínimo dos líneas.
2. Total debe debe ser positivo.
3. Total debe debe ser igual a total haber.
4. La fecha debe pertenecer a un periodo contabilizable.
5. Todas las cuentas usadas deben existir para la empresa.

### Eventos que generan asientos

| Evento | Método |
|---|---|
| Venta confirmada | `handle_venta_confirmada` |
| Devolución de venta | `handle_devolucion_venta` |
| Compra recibida | `handle_compra_recibida` |
| Nómina generada | `handle_nomina_generada` |

### Periodos contables

`AccountingPeriodService` valida que una fecha pueda contabilizarse. Un periodo cerrado debe bloquear nuevos asientos para esa fecha.

---

## 7.7 Facturación

### Entidades

- `Factura`.
- `FacturaLinea`.
- `FacturaEvento`.

### Emitir factura desde venta

`InvoiceService.emitir_desde_venta(...)`:

1. Requiere venta `CONFIRMADA`.
2. Requiere líneas facturables.
3. Crea cabecera `Factura` en `BORRADOR`.
4. Copia líneas de venta a `FacturaLinea`.
5. Llama proveedor CFDI (`MOCK` o HTTP).
6. Guarda UUID fiscal, URLs XML/PDF y fecha de timbrado.
7. Cambia estado a `TIMBRADA`.
8. Registra evento `FACTURA_TIMBRADA`.
9. Encola outbox `FacturaTimbrada`.

### Cancelar factura

`InvoiceService.cancelar_factura(...)`:

1. Requiere factura `TIMBRADA`.
2. Llama proveedor para cancelar.
3. Cambia estado a `CANCELADA`.
4. Registra evento.
5. Encola outbox `FacturaCancelada`.

---

## 7.8 Laboratorio óptico

### Entidades

- `OrdenLaboratorio`.
- `OrdenLaboratorioEtapa`.
- `ConsumoMaterialLaboratorio`.
- `ControlCalidadLaboratorio`.

### Etapas estándar

```text
BLOQUEO
TALLADO
PULIDO
TRATAMIENTO
MONTAJE
CONTROL_CALIDAD
```

### Crear orden desde venta

`LabService.crear_orden_desde_venta(...)`:

1. Requiere venta `CONFIRMADA`.
2. Requiere paciente asociado.
3. Crea `OrdenLaboratorio` en estado `PENDIENTE`.
4. Crea etapas estándar en estado `PENDIENTE`.
5. Usa timestamps con microsegundos distintos para conservar orden.

### Iniciar orden

`LabService.iniciar_orden(...)`:

1. Requiere estado `PENDIENTE`.
2. Cambia orden a `EN_PROCESO`.
3. Marca primera etapa como `EN_PROCESO`.

### Completar etapa

`LabService.completar_etapa(...)`:

1. Requiere orden `EN_PROCESO`.
2. Requiere etapa actual `EN_PROCESO`.
3. Marca etapa como `COMPLETADA`.
4. Si quedan pendientes, inicia la siguiente.
5. Si no quedan, cambia orden a `CONTROL_CALIDAD`.

### Consumo de materiales

`LabService.registrar_consumo_material(...)`:

1. Requiere orden `EN_PROCESO`.
2. Consume inventario con PEPS.
3. Registra `ConsumoMaterialLaboratorio` con costo real.

### Control de calidad

`LabService.registrar_control_calidad(...)`:

- `APROBADO`: orden pasa a `LISTA_ENTREGA`.
- `RETRABAJO`: orden vuelve a `EN_PROCESO`.
- Otro resultado: orden pasa a `RECHAZADA`.

### Entrega

`LabService.entregar_orden(...)`:

- Requiere `LISTA_ENTREGA`.
- Cambia a `ENTREGADA`.
- Marca `fecha_entrega`.

---

## 7.9 Garantías

### Entidades

- `Garantia`.
- `ReclamacionGarantia`.
- `EventoGarantia`.

### Crear garantía

`WarrantyService.crear_garantia(...)`:

1. Requiere venta `CONFIRMADA`.
2. Valida que `fecha_fin >= fecha_inicio`.
3. Crea garantía `ACTIVA`.
4. Registra evento `GARANTIA_CREADA`.

### Crear garantía desde laboratorio

`crear_desde_orden_laboratorio(...)`:

1. Requiere orden de laboratorio existente.
2. Requiere orden `ENTREGADA`.
3. Crea garantía ligada a la venta y orden.

### Reclamación

`abrir_reclamacion(...)`:

1. Bloquea garantía.
2. Actualiza a `VENCIDA` si fecha fin ya pasó.
3. Requiere garantía `ACTIVA`.
4. Crea reclamación `ABIERTA`.
5. Cambia garantía a `EN_RECLAMO`.
6. Registra evento.

### Resolver reclamación

`resolver_reclamacion(...)`:

1. Requiere reclamación `ABIERTA`.
2. Guarda estado final y resolución.
3. Marca fecha de cierre.
4. Si se rechaza/cierra, garantía vuelve a `ACTIVA`; si se aprueba, queda `EN_RECLAMO`.
5. Registra evento.

---

## 7.10 Nómina

### Entidades

- `Empleado`.
- `NominaPeriodo`.
- `NominaRecibo`.

### Flujo

1. Crear empleados activos.
2. Crear periodo de nómina `BORRADOR`.
3. Calcular periodo:
   - Borra recibos previos si recalcula.
   - Busca empleados activos.
   - Calcula días pagados.
   - Calcula percepciones como salario diario por días.
   - Deducciones actuales en cero.
   - Crea recibos `CALCULADO`.
   - Actualiza totales.
4. Confirmar periodo:
   - Requiere estado `CALCULADO`.
   - Requiere neto positivo.
   - Genera asiento contable.
   - Cambia periodo y recibos a `CONFIRMADO`.

---

## 7.11 Tesorería

### Entidades

- `CuentaBancaria`.
- `MovimientoBancario`.
- `ConciliacionBancaria`.

### Flujo

1. Crear cuenta bancaria ligada a cuenta contable.
2. Registrar movimientos manuales o importar extracto.
3. Importación bancaria:
   - Usa proveedor CSV o HTTP.
   - Evita duplicados por cuenta, referencia, fecha y monto.
4. Conciliar:
   - Movimiento debe estar pendiente.
   - Asiento debe existir.
   - Monto del movimiento debe coincidir con monto del asiento.
   - Se crea conciliación y movimiento pasa a `CONCILIADO`.

---

## 7.12 Presupuestos

### Entidades

- `CentroCosto`.
- `Presupuesto`.
- `PresupuestoLinea`.

### Flujo

1. Crear centro de costo.
2. Crear presupuesto con líneas por cuenta.
3. Comprometer presupuesto:
   - Busca línea por cuenta.
   - Verifica monto disponible.
   - Aumenta comprometido.

---

## 7.13 CRM

### Entidades

- `CitaOptica`.
- `RecordatorioCliente`.

### Funcionalidad

- Crear citas.
- Listar citas paginadas.
- Cambiar estado de cita.
- Crear recordatorios.
- Listar recordatorios pendientes.

---

## 7.14 Configuración

### Entidades

- `Impuesto`.
- `SerieFolio`.
- `TipoCambio`.
- `ReglaContable`.

### Funcionalidad

- Configurar impuestos.
- Administrar series y folios.
- Registrar tipos de cambio.
- Definir reglas contables por evento.

---

## 7.15 Reportes

`ReportService` genera reportes desde tablas transaccionales.

Reportes principales:

- Balanza de comprobación.
- Libro diario.
- Libro mayor.
- Estado de resultados.
- Balance general.
- Inventario valuado.
- Margen de ventas.

Regla: reportes no deben modificar datos. Solo consultan y agregan.

---

## 7.16 Auditoría

### Entidad

- `AuditoriaEvento`.

### Uso

Los endpoints relevantes llaman `audit_user_action(...)` para guardar:

- Usuario.
- Acción.
- Entidad.
- ID de entidad.
- Payload resumido.

También existe verificación de cadena para detectar alteraciones.

---

## 7.17 Idempotencia

### Entidad

- `IdempotencyKey`.

### Problema que resuelve

Evita duplicar operaciones críticas cuando el cliente reintenta una request por timeout o mala conexión.

### Funcionamiento

1. Cliente manda header `Idempotency-Key`.
2. Endpoint llama `IdempotencyService.start(...)`.
3. Se calcula hash canónico del payload.
4. Si la key no existe, se crea en `PROCESSING`.
5. Si existe con mismo payload y `COMPLETED`, se devuelve respuesta guardada.
6. Si existe con payload distinto, se rechaza.
7. Si está en proceso y bloqueada, se rechaza temporalmente.
8. Al terminar, se llama `complete(...)` o `fail(...)`.

Usos actuales:

- Confirmar venta.
- Registrar recepción de compra.
- Algunas operaciones críticas con outbox.

---

## 7.18 Outbox transaccional

### Entidad

- `OutboxEvent`.

### Problema que resuelve

Cuando una transacción de negocio debe publicar eventos externos, el patrón outbox evita perder eventos si el proceso cae después del commit.

### Flujo

1. Servicio de negocio modifica datos.
2. Dentro de la misma transacción, encola evento outbox.
3. Un worker procesa eventos pendientes.
4. Marca `PROCESSING`, luego `PUBLISHED` o `FAILED`.
5. En fallos calcula próximo intento con backoff.

Eventos comunes:

- `VentaConfirmada`.
- `CompraRecibida`.
- `FacturaTimbrada`.
- `FacturaCancelada`.

---

## 8. Flujos de negocio completos

## 8.1 Flujo venta → inventario → contabilidad → facturación → laboratorio → garantía

```text
1. Crear cliente / paciente / receta
2. Crear venta BORRADOR con líneas y pagos
3. Confirmar venta
   ├── consume inventario PEPS
   ├── calcula costo real
   ├── genera asiento contable
   └── encola outbox VentaConfirmada
4. Emitir factura desde venta
   ├── copia líneas de venta
   ├── llama proveedor CFDI
   ├── marca TIMBRADA
   └── encola outbox FacturaTimbrada
5. Crear orden de laboratorio desde venta
   ├── crea etapas estándar
   └── queda PENDIENTE
6. Iniciar laboratorio
7. Consumir materiales
   └── consume inventario PEPS
8. Completar etapas
9. Control de calidad
10. Entregar orden
11. Crear garantía desde orden entregada
12. Abrir/revisar reclamaciones si aplica
```

## 8.2 Flujo compra → recepción → inventario → contabilidad

```text
1. Crear proveedor
2. Crear orden de compra BORRADOR con líneas
3. Aprobar orden
4. Recibir orden total o parcialmente
   ├── valida pendientes por línea
   ├── crea recepción y líneas de recepción
   ├── alimenta inventario
   ├── actualiza cantidad_recibida
   ├── cambia orden a PARCIAL o RECIBIDA
   ├── genera asiento compra recibida
   └── encola outbox CompraRecibida
```

## 8.3 Flujo stock mínimo → solicitud de compra

```text
1. Inventario tiene productos con stock_minimo
2. Servicio revisa existencias
3. Si cantidad actual < mínimo, crea línea sugerida
4. Genera SolicitudCompra BORRADOR
5. Usuario puede usarla como base para comprar
```

## 8.4 Flujo devolución de venta

```text
1. Venta debe estar CONFIRMADA
2. Se seleccionan líneas a devolver
3. Se calcula importe devuelto
4. Se reingresa inventario con costo proporcional
5. Se crea devolución y líneas
6. Se genera asiento reverso
7. Se encola evento outbox
```

## 8.5 Flujo nómina

```text
1. Crear empleados activos
2. Crear periodo BORRADOR
3. Calcular periodo
   ├── genera recibos por empleado activo
   └── calcula totales
4. Confirmar periodo
   ├── genera asiento contable
   └── marca periodo y recibos como CONFIRMADO
```

---

## 9. Estados de negocio principales

### Venta

```text
BORRADOR → CONFIRMADA
CONFIRMADA → devolución parcial/total por DevolucionVenta
```

### Orden de compra

```text
BORRADOR → APROBADA → PARCIAL → RECIBIDA
APROBADA → RECIBIDA
```

### Recepción de compra

```text
RECIBIDA
```

### Factura

```text
BORRADOR → TIMBRADA → CANCELADA
```

### Orden de laboratorio

```text
PENDIENTE → EN_PROCESO → CONTROL_CALIDAD → LISTA_ENTREGA → ENTREGADA
                         ↘ RECHAZADA
                         ↘ EN_PROCESO por retrabajo
```

### Etapa de laboratorio

```text
PENDIENTE → EN_PROCESO → COMPLETADA
```

### Garantía

```text
ACTIVA → EN_RECLAMO
ACTIVA → VENCIDA
EN_RECLAMO → ACTIVA si reclamación rechazada/cerrada
```

### Reclamación de garantía

```text
ABIERTA → APROBADA / RECHAZADA / CERRADA
```

### Nómina

```text
BORRADOR → CALCULADO → CONFIRMADO
```

### Outbox

```text
PENDING → PROCESSING → PUBLISHED
PENDING → PROCESSING → FAILED → PENDING/PROCESSING en reintento
```

### Idempotencia

```text
PROCESSING → COMPLETED
PROCESSING → FAILED
```

---

## 10. Reglas técnicas importantes

### 10.1 Async SQLAlchemy

El backend usa SQLAlchemy async. Evitar patrones que disparen lazy loading implícito fuera de `await`.

Recomendado:

```python
result = await db.execute(
    select(Venta)
    .options(selectinload(Venta.lineas))
    .where(Venta.id == venta_id)
)
```

Evitar acceder a relaciones no cargadas si eso puede generar IO implícito.

### 10.2 `flush()` vs `commit()`

- `flush()` envía cambios a DB dentro de la transacción y permite obtener IDs.
- `commit()` lo maneja generalmente `get_db()` al final del request.
- Servicios usan `flush()` para coordinar cabecera-detalle.

### 10.3 Transacciones anidadas

Algunos servicios usan `async with self.db.begin_nested():` para agrupar operaciones críticas. Ejemplos:

- Confirmar venta.
- Recibir compra.
- Emitir/cancelar factura.
- Registrar consumo de laboratorio.
- Confirmar nómina.

### 10.4 Bloqueos `FOR UPDATE`

Se usan cuando hay riesgo de concurrencia:

- Existencia de inventario.
- Venta al confirmar.
- Orden de compra al recibir.
- Garantía al reclamar.
- Periodo de nómina al calcular/confirmar.

### 10.5 Carga de relaciones

Usar `selectinload(...)` para devolver entidades con detalle.

Ejemplo:

```python
select(Venta).options(selectinload(Venta.lineas), selectinload(Venta.pagos))
```

### 10.6 Multiempresa

Toda operación debe filtrar por `empresa_id`. Nunca consultar solo por `id` cuando el dato pertenece a una empresa, salvo que inmediatamente se valide `obj.empresa_id == empresa_id`.

### 10.7 Errores de negocio

Los servicios suelen lanzar `ValueError`. Los endpoints convierten esos errores a:

- `400 BAD REQUEST` para payload inválido o creación inválida.
- `404 NOT FOUND` para inexistente.
- `409 CONFLICT` para estado de negocio incompatible.

---

## 11. Convenciones de desarrollo

### 11.1 Para agregar un nuevo módulo

1. Crear modelo en `app/models/nuevo_modulo.py`.
2. Importarlo en `app/models/__init__.py`.
3. Crear schemas en `app/schemas/nuevo_modulo.py`.
4. Crear servicio en `app/services/nuevo_modulo_service.py`.
5. Crear endpoints en `app/api/v1/endpoints/nuevo_modulo.py`.
6. Registrar router en `app/api/v1/router.py`.
7. Agregar permisos RBAC en endpoints.
8. Agregar tests.
9. Crear migración Alembic.
10. Actualizar documentación si cambia flujo de negocio.

### 11.2 Para agregar una operación cabecera-detalle

1. Definir tabla cabecera.
2. Definir tabla detalle con FK a cabecera.
3. Definir relación `lineas = relationship(...)`.
4. Crear schema `LineaCreate`.
5. En schema cabecera incluir `lineas: list[LineaCreate]`.
6. En servicio crear cabecera, `flush()`, crear líneas con FK, `add_all()`.
7. Retornar cabecera recargada con `selectinload`.

### 11.3 Para agregar un evento contable

1. Crear método en `AccountingEngine`.
2. Validar cuentas necesarias.
3. Construir líneas balanceadas.
4. Invocarlo desde servicio de dominio en el punto de confirmación.
5. Guardar `asiento_id` en entidad origen si aplica.
6. Agregar test de asiento.

### 11.4 Para agregar evento outbox

1. Definir `aggregate_type`.
2. Definir `aggregate_id`.
3. Definir `event_type`.
4. Definir payload mínimo estable.
5. Usar idempotency key determinística.
6. Encolar dentro de la misma transacción de negocio.

Ejemplo:

```python
await OutboxService(self.db).enqueue(
    empresa_id=empresa_id,
    payload=OutboxEventCreate(
        aggregate_type="Venta",
        aggregate_id=str(venta.id),
        event_type="VentaConfirmada",
        payload={"venta_id": str(venta.id)},
        idempotency_key=f"venta:{venta.id}:confirmada",
    ),
)
```

### 11.5 Para agregar endpoint idempotente

1. Aceptar header `Idempotency-Key`.
2. Llamar `IdempotencyService.start(...)` antes de ejecutar operación.
3. Si `replay=True`, devolver respuesta almacenada.
4. Al éxito, llamar `complete(...)`.
5. Al error, llamar `fail(...)`.

---

## 12. Pruebas

### 12.1 Comandos

Desde `backend/`:

```bash
make test
make verify
pytest -q -x
pytest tests/test_sales_workflow.py -q
pytest tests/test_purchase_workflow.py -q
```

### 12.2 Infraestructura de tests

`tests/conftest.py`:

- Carga `.env.test` y luego `.env.test.local`.
- Define URLs seguras para servicios de test.
- Usa engine async con `NullPool` para evitar reuso de conexiones entre event loops.
- Crea/droppea metadata para test DB.
- Usa `httpx.AsyncClient` con `ASGITransport` para probar FastAPI.
- Sobrescribe `get_db` en la app.

### 12.3 Tipos de tests existentes

| Test | Qué valida |
|---|---|
| `test_auth.py` | Login, sesiones, auth básica. |
| `test_sales_workflow.py` | Crear/confirmar venta. |
| `test_sales_returns.py` | Devolución y reingreso a inventario. |
| `test_purchase_workflow.py` | Orden, recepción, inventario y CxP. |
| `test_inventory_accounting.py` | Inventario, kardex y costo. |
| `test_invoice_workflow.py` | Facturación desde venta. |
| `test_lab_workflow.py` | Orden de laboratorio y etapas. |
| `test_warranty_workflow.py` | Garantías y reclamaciones. |
| `test_outbox_workflow.py` | Estados del outbox. |
| `test_idempotency_workflow.py` | Reintentos idempotentes. |
| `test_reports.py` | Reportes contables/inventario/ventas. |
| `test_treasury_workflow.py` | Tesorería y conciliación. |
| `test_budget_workflow.py` | Presupuestos. |
| `test_payroll_workflow.py` | Nómina. |
| `test_api_security_audit.py` | Cobertura de seguridad en endpoints. |
| `test_api_contract_audit.py` | Registro y contrato API. |

### 12.4 Cómo probar un flujo manualmente

1. Levantar servicios DB.
2. Aplicar migraciones.
3. Ejecutar seed.
4. Levantar backend.
5. Abrir Swagger.
6. Login con usuario demo.
7. Usar token Bearer.
8. Ejecutar endpoints en orden de negocio.

Credenciales seed:

```text
admin / Admin123!
admin_sucursal / Demo123!
optometrista / Demo123!
vendedor / Demo123!
contador / Demo123!
```

---

## 13. Operación local para navegador

Flujo recomendado:

```bash
cd backend
make install
make migrate-up
make seed
make run
```

Luego abrir:

```text
http://localhost:8000/docs
```

Verificar:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Si `/health` responde pero `/ready` falla, el backend inició pero no llega a PostgreSQL.

---

## 14. Migraciones

El proyecto usa Alembic.

Comandos:

```bash
make migrate msg="descripcion"
make migrate-up
make migrate-down
```

Reglas:

- Todo cambio en modelos que afecte DB debe tener migración.
- Revisar migraciones autogeneradas antes de aplicarlas.
- No borrar datos en migraciones sin respaldo o estrategia.
- Mantener migraciones reversibles cuando sea razonable.

---

## 15. Integraciones externas

### 15.1 Facturación electrónica

`einvoicing_provider.py` define proveedores:

- `MOCK`: proveedor simulado para desarrollo/pruebas.
- `HTTP`: integración remota configurable.

Se usa desde `InvoiceService`.

### 15.2 Banco

`banking_provider.py` define proveedores:

- CSV.
- HTTP.

Se usa desde `TreasuryService.importar_estado_bancario(...)`.

### 15.3 Outbox worker

Comandos:

```bash
make outbox-worker-once
make outbox-worker
```

---

## 16. Observabilidad y hardening

### Middlewares registrados

- `RequestContextMiddleware`.
- `MetricsMiddleware`.
- `SecurityHeadersMiddleware`.
- `RateLimitMiddleware`.
- `CORSMiddleware`.

### Endpoints de observabilidad

- `/api/v1/observabilidad/metrics`.
- `/api/v1/observabilidad/metrics/prometheus`.
- `/api/v1/observabilidad/readiness`.
- `/health`.
- `/ready`.

---

## 17. Errores comunes y diagnóstico

### 17.1 `duplicate key value violates unique constraint`

Causa: se intentó insertar un dato con clave única existente.

Solución:

- Para seed, ya se usa upsert idempotente.
- Para operaciones de negocio, validar folio único por empresa o usar endpoints idempotentes.

### 17.2 `MissingGreenlet`

Causa típica: acceso a relación lazy que intenta hacer IO sin `await` en SQLAlchemy async.

Solución:

- Cargar relaciones con `selectinload`.
- Evitar `obj.lineas.append(...)` si la relación no está cargada.
- Crear hijos con FK explícita y `add_all(...)`.

### 17.3 `Inventario insuficiente`

Causa: no hay existencia suficiente o capas disponibles.

Solución:

- Registrar entrada manual.
- Recibir compra.
- Verificar sucursal/producto correctos.

### 17.4 `Asiento descuadrado`

Causa: total debe distinto de total haber.

Solución:

- Revisar cuentas y montos del evento contable.
- Verificar costo PEPS y total de venta/compra.

### 17.5 `/ready` falla

Causa: DB no disponible o `DATABASE_URL` incorrecto.

Solución:

- Verificar Postgres.
- Verificar `.env`.
- Verificar migraciones.

### 17.6 Aviso de bcrypt/passlib

Causa: `passlib` 1.7.x espera un atributo legacy en `bcrypt` que versiones nuevas removieron.

Solución aplicada:

- Shim en `app/core/security.py` antes de crear `CryptContext`.

---

## 18. Checklist para desarrollar una nueva funcionalidad

Antes de codificar:

- [ ] Identificar módulo de negocio.
- [ ] Definir estados.
- [ ] Definir entidad cabecera/detalle si aplica.
- [ ] Definir si afecta inventario.
- [ ] Definir si genera contabilidad.
- [ ] Definir si requiere outbox.
- [ ] Definir si debe ser idempotente.
- [ ] Definir permisos RBAC.
- [ ] Definir tests.

Durante implementación:

- [ ] Crear/ajustar modelos.
- [ ] Crear/ajustar schemas.
- [ ] Implementar servicio.
- [ ] Mantener endpoints delgados.
- [ ] Usar `empresa_id` del usuario actual.
- [ ] Usar `selectinload` para relaciones necesarias.
- [ ] Usar `with_for_update` en recursos concurrentes.
- [ ] Usar `flush()` antes de crear detalles.
- [ ] Usar `add_all()` para detalles.
- [ ] Agregar auditoría si aplica.
- [ ] Agregar outbox si aplica.
- [ ] Agregar migración.
- [ ] Agregar tests.

Antes de entregar:

- [ ] `make verify-fast`.
- [ ] `make test` o tests focalizados.
- [ ] `make migrate-verify` si tocaste migraciones.
- [ ] Revisar OpenAPI si cambiaste endpoints.
- [ ] Probar flujo manual en `/docs` si es crítico.

---

## 19. Mapa rápido de servicios

| Servicio | Responsabilidad |
|---|---|
| `AuthService` | Login, refresh, logout, usuario actual, cambio/reset de contraseña. |
| `InventoryService` | Entradas, salidas PEPS, existencias, kardex. |
| `SalesService` | Crear, listar, obtener y confirmar ventas. |
| `SalesReturnService` | Devoluciones de venta y reingreso de inventario. |
| `PurchaseService` | Órdenes de compra, aprobación y recepción. |
| `PurchaseRequisitionService` | Solicitudes por stock mínimo. |
| `AccountingEngine` | Asientos contables de doble partida. |
| `AccountingPeriodService` | Valida periodos contabilizables. |
| `InvoiceService` | Emisión/cancelación de facturas. |
| `LabService` | Órdenes de laboratorio, etapas, consumos, calidad y entrega. |
| `WarrantyService` | Garantías, reclamaciones y eventos. |
| `PayrollService` | Empleados, periodos, cálculo y confirmación de nómina. |
| `TreasuryService` | Cuentas bancarias, movimientos, importación y conciliación. |
| `BudgetService` | Centros de costo, presupuestos y compromisos. |
| `ReportService` | Reportes contables, inventario y ventas. |
| `ConfigurationService` | Impuestos, series, tipos de cambio y reglas contables. |
| `CRMService` | Citas y recordatorios. |
| `AuditService` | Auditoría y verificación de cadena. |
| `IdempotencyService` | Control de reintentos seguros. |
| `OutboxService` | Persistencia de eventos por publicar. |
| `OutboxDispatcherService` | Despacho de eventos pendientes. |
| `SessionSecurityService` | Seguridad operacional de sesiones. |

---

## 20. Orden recomendado para estudiar el backend

1. `app/main.py` para entender cómo arranca la app.
2. `app/api/v1/router.py` para ver módulos expuestos.
3. `app/api/deps.py` para entender auth/permisos.
4. `app/models/base.py` y `app/models/__init__.py` para entender entidades.
5. `app/models/venta.py`, `compra.py`, `inventario.py`, `contabilidad.py`.
6. `app/schemas/ventas.py` y `compras.py`.
7. `app/services/sales_service.py`.
8. `app/services/purchase_service.py`.
9. `app/services/inventory_service.py`.
10. `app/services/accounting_engine.py`.
11. `app/services/invoice_service.py`.
12. `app/services/lab_service.py`.
13. `app/services/warranty_service.py`.
14. Tests de workflow: ventas, compras, inventario, facturación, laboratorio y garantías.

---

## 21. Resumen mental del sistema

La idea central del backend es:

```text
Una empresa opera sucursales.
Las sucursales venden y compran productos.
Las compras alimentan inventario.
Las ventas consumen inventario.
Inventario calcula costo real por PEPS.
Ventas y compras generan asientos contables.
Ventas confirmadas pueden facturarse.
Ventas con paciente pueden pasar a laboratorio.
Laboratorio puede consumir materiales.
Órdenes entregadas pueden generar garantías.
Operaciones críticas publican eventos por outbox.
Reintentos críticos se controlan con idempotencia.
Todo está segmentado por empresa y protegido por permisos.
```

---

## 22. Glosario

| Término | Significado |
|---|---|
| Cabecera | Registro principal de una operación, por ejemplo `Venta`. |
| Línea / detalle | Registro hijo de una cabecera, por ejemplo `VentaLinea`. |
| PEPS/FIFO | Primero en entrar, primero en salir; método de consumo de capas de inventario. |
| Kardex | Historial de movimientos de inventario. |
| Asiento | Registro contable con líneas debe/haber. |
| Outbox | Tabla de eventos pendientes para publicar de forma confiable. |
| Idempotencia | Capacidad de reintentar una request sin duplicar efectos. |
| Tenant | Empresa propietaria de los datos. |
| RBAC | Control de acceso basado en roles/permisos. |
| ABAC | Control por atributos, por ejemplo empresa/sucursal del usuario. |
| CFDI | Facturación electrónica mexicana. |

---

## 23. Recomendaciones finales

- Para entender una operación, leer primero el test de workflow correspondiente.
- Luego leer endpoint, schema, servicio y modelo.
- Si una operación modifica inventario, buscar llamadas a `InventoryService`.
- Si genera contabilidad, buscar llamadas a `AccountingEngine`.
- Si emite eventos, buscar llamadas a `OutboxService`.
- Si maneja reintentos desde frontend, buscar `IdempotencyService`.
- Mantener lógica de negocio fuera de endpoints.
- Mantener detalles transaccionales en tablas relacionales, no JSON.
- Usar JSON solo para contratos HTTP, payloads operativos y configuraciones flexibles.
