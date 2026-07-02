# Informe de proyecto — exSoftOptic Backend

**Fecha del informe:** 2026-07-02  
**Proyecto:** exSoftOptic  
**Módulo evaluado:** Backend  
**Objetivo del informe:** documentar de forma integral la metodología aplicada, arquitectura, estructura técnica, tecnologías, avances implementados, mejoras operativas y el procedimiento recomendado para ejecutar pruebas del backend.

---

## 1. Resumen ejecutivo

Durante esta etapa se consolidó un backend amplio para el sistema óptico **exSoftOptic**, orientado a cubrir flujos operativos de ventas, compras, inventario, contabilidad, laboratorio óptico, garantías, facturación, tesorería, nómina, CRM, presupuestos, reportes, auditoría, idempotencia y outbox transaccional.

El trabajo no se limitó a crear endpoints: también se incorporaron modelos de datos, migraciones Alembic, esquemas Pydantic, servicios de dominio, middleware de seguridad/observabilidad, scripts operativos, auditorías estáticas, CI, pruebas y documentación operacional.

El backend quedó preparado para pasar a la fase de instalación de dependencias y ejecución real de pruebas, con un flujo profesional documentado para validar primero la estructura estática del sistema y después correr migraciones, servicios efímeros y pruebas automatizadas.

---

## 2. Metodología de trabajo aplicada

La metodología aplicada fue incremental, defensiva y orientada a verificabilidad:

### 2.1. Desarrollo por capas

Se trabajó separando responsabilidades en capas claras:

1. **Modelos SQLAlchemy** para representar persistencia.
2. **Migraciones Alembic** para versionar la base de datos.
3. **Schemas Pydantic** para contratos de entrada/salida.
4. **Servicios de dominio** para encapsular reglas de negocio.
5. **Endpoints FastAPI** para exponer capacidades HTTP.
6. **Middleware/Core** para seguridad, trazabilidad, métricas y manejo de errores.
7. **Scripts operativos** para automatizar auditorías, seeds, backups, migraciones y verificaciones.
8. **Pruebas automatizadas** para cubrir servicios, scripts, flujos y smoke tests.
9. **CI** para ejecutar verificaciones en pull requests y ramas principales.

### 2.2. Validación antes de ejecución destructiva

Se agregaron auditorías estáticas para detectar problemas antes de tocar base de datos o ejecutar pruebas pesadas:

- Auditoría de seguridad de endpoints.
- Auditoría de contrato API.
- Auditoría RBAC.
- Auditoría de paginación.
- Auditoría estática de migraciones.
- Validación de configuración runtime.
- Verificación de preparación local para pruebas.

### 2.3. Operación reproducible

Se integraron comandos `make` para que los pasos críticos sean repetibles por cualquier desarrollador o por CI:

- `make test-readiness`
- `make api-contract-audit`
- `make security-audit`
- `make rbac-audit`
- `make pagination-audit`
- `make migration-audit`
- `make migrate-verify`
- `make verify`
- `make e2e`

### 2.4. Seguridad por defecto

Se reforzó el backend eliminando placeholders inseguros, evitando exponer tokens de recuperación, agregando cabeceras de seguridad, rate limiting, contexto de request, auditoría y validaciones de permisos.

### 2.5. Preparación para CI/CD

El workflow de GitHub Actions instala dependencias, valida sintaxis/imports, ejecuta auditorías, valida migraciones, exporta OpenAPI y corre pruebas de backend y smoke E2E.

---

## 3. Tecnología usada

### 3.1. Lenguaje y framework principal

- **Python 3.12** como runtime objetivo en Docker y CI.
- **FastAPI** como framework HTTP.
- **Uvicorn** como servidor ASGI.
- **Pydantic v2** y `pydantic-settings` para validación de datos y configuración.

### 3.2. Persistencia y datos

- **PostgreSQL** como base relacional principal.
- **SQLAlchemy 2 async** para ORM asíncrono.
- **Asyncpg** como driver PostgreSQL async.
- **Alembic** para migraciones.
- **MongoDB/Motor** preparado para datos clínicos/documentales.
- **Redis** para soporte operativo/cache/sesiones según configuración.

### 3.3. Seguridad y autenticación

- **JWT** con `python-jose`.
- **Passlib/bcrypt** para hashing de contraseñas.
- Dependencias FastAPI para autenticación, usuario actual, permisos RBAC y helpers ABAC.
- Middleware de cabeceras de seguridad.
- Rate limiting.
- Protección contra exposición de tokens en recuperación de contraseña.

### 3.4. Operación e integración

- **Docker** con imagen endurecida y usuario no root.
- **Docker Compose** para entornos local, test y staging.
- **GitHub Actions** para CI.
- Scripts operativos en `backend/scripts`.
- Outbox transaccional y worker para integraciones confiables.
- Adaptadores para banking y CFDI/e-invoicing.

### 3.5. Testing y calidad

- **Pytest**.
- **pytest-asyncio**.
- **pytest-cov**.
- **httpx** para cliente async de tests.
- Auditorías estáticas propias.
- Verificador central `verify_backend.py`.

---

## 4. Estructura general del proyecto backend

La estructura principal queda organizada así:

```text
backend/
├── alembic/
│   ├── env.py
│   └── versions/
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
│   └── workers/
├── docker/
├── scripts/
├── seeds/
├── tests/
├── Dockerfile
├── Makefile
├── pytest.ini
├── requirements.txt
└── requirements-dev.txt
```

A nivel repositorio también existen:

```text
.github/workflows/backend-ci.yml
docker-compose.yml
docker-compose.test.yml
docker-compose.staging.yml
docs/backend-operational-runbook.md
docs/backend-permissions.md
informe_de_proyecto.md
```

---

## 5. Estructura de dominio implementada

### 5.1. Dominios principales

Se implementaron módulos para:

- **Autenticación y usuarios**.
- **Productos**.
- **Inventario**.
- **Ventas**.
- **Compras**.
- **Contabilidad**.
- **Facturación/CFDI**.
- **Laboratorio óptico**.
- **Garantías**.
- **Nómina**.
- **Tesorería**.
- **CRM**.
- **Presupuestos**.
- **Reportes**.
- **Auditoría**.
- **Outbox transaccional**.
- **Observabilidad**.
- **Configuración global/operativa**.

### 5.2. Endpoints API v1

Actualmente el router API v1 registra endpoints para:

- `/auth`
- `/usuarios`
- `/productos`
- `/inventario`
- `/contabilidad`
- `/ventas`
- `/compras`
- `/laboratorio`
- `/garantias`
- `/facturacion`
- `/reportes`
- `/nomina`
- `/auditoria`
- `/configuracion`
- `/crm`
- `/tesoreria`
- `/presupuestos`
- `/observabilidad`
- `/outbox`

Se eliminó el endpoint placeholder `clientes.py` porque no tenía rutas reales y podía generar una falsa percepción de funcionalidad implementada.

---

## 6. Modelos, migraciones y base de datos

### 6.1. Modelos SQLAlchemy

Se agregaron modelos para representar entidades de negocio como:

- Empresas, sucursales, usuarios, roles y sesiones.
- Productos, categorías, marcas e inventario.
- Clientes, pacientes, recetas ópticas, ventas, pagos y devoluciones.
- Compras, proveedores, órdenes, recepciones y requisiciones.
- Cuentas contables, asientos, líneas y periodos contables.
- Facturas, líneas y eventos CFDI.
- Citas, recordatorios y CRM.
- Laboratorio óptico, etapas, consumos y control de calidad.
- Garantías, reclamaciones y eventos.
- Nómina, empleados, periodos y recibos.
- Tesorería, cuentas bancarias, movimientos y conciliaciones.
- Presupuestos y centros de costo.
- Auditoría, outbox e idempotencia.

### 6.2. Migraciones Alembic

Se añadieron múltiples revisiones Alembic para evolucionar el esquema desde la base inicial hasta los dominios nuevos.

El conjunto de migraciones incluye:

- Esquema inicial.
- Fundaciones de inventario y contabilidad.
- Workflow de ventas ópticas.
- Compras y recepciones.
- Laboratorio óptico.
- Garantías.
- Facturación electrónica.
- Nómina.
- Auditoría.
- Configuración global.
- Devoluciones de ventas.
- CRM óptico.
- Requisiciones de compra.
- Tesorería y conciliación.
- Presupuestos.
- Outbox transaccional.
- Idempotency keys HTTP.
- Periodos contables.

### 6.3. Auditoría estática de migraciones

Se agregó `audit_migrations_static.py` para validar:

- Que existan migraciones.
- Que cada migración tenga `revision`.
- Que no haya revisiones duplicadas.
- Que el filename incluya el revision ID.
- Que exista `upgrade()`.
- Que exista `downgrade()`.
- Que exista una sola raíz.
- Que exista una sola cabeza.
- Que no haya `down_revision` desconocido.
- Que el grafo sea lineal/conectado.
- Que no existan operaciones destructivas en `upgrade()` como `drop_table` o `drop_column`.

---

## 7. Servicios de aplicación

La lógica de negocio se concentró en servicios para mantener los endpoints delgados y reutilizables.

Servicios destacados:

- `sales_service.py`
- `sales_return_service.py`
- `purchase_service.py`
- `purchase_requisition_service.py`
- `inventory_service.py`
- `inventory_alert_service.py`
- `accounting_engine.py`
- `accounting_period_service.py`
- `invoice_service.py`
- `einvoicing_provider.py`
- `banking_provider.py`
- `treasury_service.py`
- `payroll_service.py`
- `lab_service.py`
- `warranty_service.py`
- `crm_service.py`
- `budget_service.py`
- `report_service.py`
- `audit_service.py`
- `outbox_service.py`
- `outbox_dispatcher.py`
- `idempotency_service.py`
- `secured_audit.py`
- `session_security_service.py`

---

## 8. Seguridad, RBAC y ABAC

### 8.1. RBAC

Se implementó catálogo de permisos basado en declaraciones `require_permissions([...])` de endpoints.

Artefactos relevantes:

- `docs/backend-permissions.md`
- `backend/seeds/roles.base.json`
- `scripts/generate_permission_catalog.py`
- `scripts/generate_role_seed.py`
- `scripts/audit_rbac_coverage.py`
- `scripts/seed_roles.py`

Roles base incluidos:

- `SUPER_ADMIN`
- `ADMIN_EMPRESA`
- `VENTAS_CAJA`
- `INVENTARIO`
- `TESORERIA`
- `CONTABILIDAD`
- `LABORATORIO`
- `REPORTES`
- `SOPORTE_OPERATIVO`

### 8.2. ABAC

Se agregaron helpers para limitar acceso por:

- Empresa (`empresa_id`).
- Sucursal (`sucursal_id`).

### 8.3. Seguridad operativa

Se añadieron:

- Middleware de security headers.
- Rate limiting.
- Contexto de request.
- Métricas.
- Error handlers centralizados.
- Validadores runtime.
- Auditoría de endpoints sin dependencia de seguridad.
- Protección para no devolver token de recuperación en `/forgot-password`.

---

## 9. Observabilidad y operación

### 9.1. Observabilidad

Se incorporaron piezas para:

- Métricas tipo Prometheus.
- Endpoint de observabilidad.
- Request context.
- Health/readiness.
- Auditoría de acciones sensibles.

### 9.2. Outbox transaccional

Se implementó patrón outbox para integraciones confiables:

- Eventos persistidos.
- Dispatcher.
- Worker.
- Comandos para ejecutar worker una vez o en modo continuo.
- Limpieza operacional de eventos publicados/atascados.

### 9.3. Idempotencia

Se agregó soporte para claves de idempotencia en flujos críticos, reduciendo riesgo de duplicidad en operaciones HTTP.

---

## 10. Scripts operativos agregados

En `backend/scripts` se consolidaron scripts para:

| Script | Propósito |
|---|---|
| `verify_backend.py` | Verifica dependencias, sintaxis y opcionalmente pytest. |
| `audit_api_security.py` | Audita endpoints sin guardas de autenticación/permisos. |
| `audit_api_contract.py` | Audita registro de routers, rutas y duplicados. |
| `audit_rbac_coverage.py` | Cruza permisos de endpoints, catálogo y roles. |
| `audit_query_pagination.py` | Detecta endpoints de listado sin límites de paginación. |
| `audit_migrations_static.py` | Valida grafo y seguridad estática de migraciones Alembic. |
| `validate_runtime_config.py` | Valida configuración runtime por entorno. |
| `verify_migrations.py` | Ejecuta Alembic contra DB de prueba/disposable. |
| `export_openapi.py` | Exporta contrato OpenAPI. |
| `generate_permission_catalog.py` | Genera catálogo de permisos. |
| `generate_role_seed.py` | Genera seed de roles base. |
| `seed_roles.py` | Importa roles base a DB. |
| `seed_test_data.py` | Crea dataset mínimo de smoke tests. |
| `check_test_readiness.py` | Preflight local sin requerir dependencias completas. |
| `init_test_environment.py` | Inicializa `.env.test.local`. |
| `wait_for_test_services.py` | Espera servicios efímeros. |
| `cleanup_operational_data.py` | Limpia outbox/idempotency operacional. |
| `manage_database_backup.py` | Backup/restore PostgreSQL. |
| `run_outbox_worker.py` | Ejecuta worker del outbox. |
| `load_smoke.py` | Prueba ligera de carga contra `/health`. |

---

## 11. CI/CD implementado

El workflow `.github/workflows/backend-ci.yml` se ejecuta en:

- `workflow_dispatch`
- Pull requests que modifiquen backend o workflow.
- Push a `main` y `develop` que modifiquen backend o workflow.

### 11.1. Servicios de CI

Levanta PostgreSQL 16 como servicio para migraciones y pruebas.

### 11.2. Pasos principales del CI

1. Checkout.
2. Setup Python 3.12.
3. Instalación de librerías OS para render/reportes.
4. Instalación de dependencias backend.
5. Verificación de dependencias y sintaxis.
6. Auditoría de seguridad de endpoints.
7. Auditoría de contrato API.
8. Validación de catálogo de permisos y roles.
9. Auditoría de paginación.
10. Auditoría estática de migraciones.
11. Validación runtime config.
12. Verificación Alembic con roundtrip.
13. Export OpenAPI.
14. Suite de tests backend.
15. Smoke E2E.

---

## 12. Docker y despliegue

### 12.1. Dockerfile endurecido

Se agregó:

- Imagen base `python:3.12-slim`.
- Variables para comportamiento Python/Pip.
- Instalación de librerías OS mínimas.
- Usuario no root `app`.
- Healthcheck contra `/health`.
- Entrypoint propio.
- Exposición de puerto `8000`.

### 12.2. Compose

Se añadieron/ajustaron:

- `docker-compose.yml`
- `docker-compose.test.yml`
- `docker-compose.staging.yml`

El compose de test levanta servicios efímeros para PostgreSQL, Redis y MongoDB en puertos aislados.

---

## 13. Avances y mejoras concretas

### 13.1. Funcionalidad de negocio

- Ventas ópticas con cliente/paciente/receta/pagos.
- Devoluciones de ventas.
- Inventario con PEPS/kardex/capas/existencias.
- Compras, recepciones y requisiciones.
- Contabilidad y periodos contables.
- Facturación electrónica.
- Laboratorio óptico.
- Garantías.
- Tesorería y conciliación bancaria.
- Nómina.
- CRM.
- Presupuestos.
- Reportes.

### 13.2. Robustez técnica

- Separación por capas.
- Migraciones versionadas.
- Auditorías estáticas.
- Verificación de configuración runtime.
- Outbox e idempotencia.
- Tests automatizados.
- CI.

### 13.3. Seguridad

- RBAC con catálogo y roles base.
- ABAC por empresa/sucursal.
- Session security.
- Security headers.
- Rate limiting.
- Endpoint security audit.
- No exposición de reset tokens.

### 13.4. Operación

- Runbook operativo.
- Seeds de roles y datos mínimos.
- Backup/restore.
- Limpieza operacional.
- Worker outbox.
- Load smoke.
- Docker test/staging.

---

## 14. Estado actual de puntos trabajados

| Punto | Estado | Resultado |
|---:|---|---|
| 1 | Completado | Importador real de roles base a DB. |
| 2 | Completado | Seed/bootstrap mínimo para smoke tests. |
| 3 | Completado | Auditoría RBAC extendida. |
| 4 | Completado | Auditoría estática de contrato API. |
| 5 | Completado | Auditoría estática extendida de migraciones. |
| 6 | Completado | Orden final de verificación backend documentado. |

---

## 15. Cómo preparar pruebas del backend

### 15.1. Preflight antes de instalar dependencias

Desde la raíz del repositorio:

```bash
cd backend
make test-env-init
make test-readiness
make api-contract-audit
make security-audit
make rbac-audit
make pagination-audit
make migration-audit
make permissions-catalog
make role-seed
SECRET_KEY=change-me-but-long-enough-for-tests DATABASE_URL=postgresql+asyncpg://optica_user:optica_password_2026@localhost:5432/optica_test REDIS_URL=redis://localhost:6379/0 ENVIRONMENT=test python scripts/validate_runtime_config.py --environment test
```

Este bloque permite validar estructura, configuración, API, RBAC, migraciones y catálogos antes de instalar dependencias y antes de tocar bases de datos reales.

### 15.2. Instalar dependencias

```bash
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### 15.3. Levantar servicios efímeros

```bash
cd backend
make test-services-up
make test-services-wait
```

### 15.4. Verificar migraciones

```bash
cd backend
make migrate-verify
```

Este comando ejecuta:

```bash
python scripts/verify_migrations.py --roundtrip
```

Debe usarse solo contra bases de datos desechables o de CI porque puede hacer downgrade a base y re-upgrade.

### 15.5. Ejecutar verificación rápida

```bash
cd backend
make verify-fast
```

Equivale a:

```bash
python scripts/verify_backend.py --skip-pytest
```

### 15.6. Ejecutar suite completa

```bash
cd backend
make verify
```

Equivale a:

```bash
python scripts/verify_backend.py
```

### 15.7. Ejecutar CI local equivalente

```bash
cd backend
make ci
```

Equivale a:

```bash
python scripts/verify_backend.py -- -q
```

### 15.8. Ejecutar smoke E2E

```bash
cd backend
make e2e
```

Equivale a:

```bash
python -m pytest tests/test_e2e_smoke.py -q
```

### 15.9. Apagar servicios efímeros

```bash
cd backend
make test-services-down
```

---

## 16. Orden recomendado completo para QA backend

```bash
cd backend
make test-env-init
make test-readiness
make api-contract-audit
make security-audit
make rbac-audit
make pagination-audit
make migration-audit
make permissions-catalog
make role-seed
SECRET_KEY=change-me-but-long-enough-for-tests DATABASE_URL=postgresql+asyncpg://optica_user:optica_password_2026@localhost:5432/optica_test REDIS_URL=redis://localhost:6379/0 ENVIRONMENT=test python scripts/validate_runtime_config.py --environment test
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
make test-services-up
make test-services-wait
make migrate-verify
make verify
make e2e
make test-services-down
```

---

## 17. Consideraciones de entorno

Antes de correr pruebas completas se requiere:

- Python compatible.
- Dependencias instaladas desde `requirements-dev.txt`.
- PostgreSQL accesible.
- Redis accesible.
- MongoDB accesible si el flujo lo requiere.
- Variables runtime mínimas:
  - `SECRET_KEY`
  - `DATABASE_URL`
  - `TEST_DATABASE_URL`
  - `REDIS_URL`
  - `MONGODB_URL`
  - `ENVIRONMENT=test`

---

## 18. Estado de pruebas en el entorno actual

En el entorno actual se han podido ejecutar auditorías estáticas y validaciones sin dependencias completas.

Las pruebas completas con pytest quedan bloqueadas localmente hasta instalar dependencias, especialmente:

- `fastapi`
- `sqlalchemy`
- `pydantic`
- `asyncpg`
- `httpx`

Esto es esperado antes de correr:

```bash
python -m pip install -r requirements-dev.txt
```

---

## 19. Riesgos y recomendaciones

### 19.1. Riesgos pendientes

- Validar la suite completa en un entorno con dependencias instaladas.
- Ejecutar migraciones contra base desechable real antes de cualquier staging persistente.
- Revisar adaptadores reales de CFDI/banking antes de conectar proveedores productivos.
- Revisar secrets y variables en staging/producción.
- Validar performance de endpoints críticos con datos representativos.

### 19.2. Recomendaciones inmediatas

1. Instalar dependencias de desarrollo.
2. Levantar servicios efímeros.
3. Ejecutar `make migrate-verify`.
4. Ejecutar `make verify`.
5. Ejecutar `make e2e`.
6. Exportar OpenAPI y compartirlo con frontend/QA.
7. Revisar logs de outbox y métricas.
8. Preparar dataset QA con `seed_roles.py` y `seed_test_data.py`.

---

## 20. Conclusión

El backend de exSoftOptic pasó de una base parcial a una plataforma backend mucho más completa, verificable y operable. Se incorporaron dominios de negocio, seguridad, auditorías, migraciones, CI, test harness, seeds y documentación operacional.

El sistema queda listo para la siguiente fase: instalación de dependencias, ejecución de servicios efímeros, validación de migraciones y corrida completa de pruebas automatizadas.
