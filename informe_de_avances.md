# Informe de avances y guía de pruebas con Docker Compose

> Proyecto: **exSoftOptic**  
> Fecha de referencia: 2026-07-17  
> Objetivo de este documento: dejar un estado claro de los avances realizados y una guía paso a paso para levantar servicios con Docker Compose y ejecutar verificaciones/pruebas del proyecto.

---

## 1. Resumen ejecutivo

El proyecto evolucionó desde un backend con módulos de negocio hacia una plataforma más completa con:

- Frontend administrativo React/Vite en `frontend/`.
- Servicios HTTP tipados por dominio en `frontend/src/services/`.
- Pantallas funcionales para los flujos principales de óptica.
- Endpoints backend de lectura/listado y CRUD ampliados para soportar la UI.
- Seeds idempotentes para datos base y demo.
- Infraestructura de pruebas con servicios efímeros mediante `docker-compose.test.yml`.
- Mejoras de calidad: lint frontend limpio, typecheck y build funcionando.
- Pruebas backend agregadas para workflows clave como laboratorio, presupuesto y tesorería.

---

## 2. Avances por área

### 2.1 Frontend React/Vite

Se agregó una aplicación frontend en `frontend/` con:

- React + TypeScript + Vite.
- Layout autenticado con sidebar/topbar.
- Cliente HTTP con token Bearer.
- Manejo de sesión y contexto de autenticación.
- Componentes reutilizables: estados vacíos, loading/error, métricas, badges, paginación, paneles, confirmaciones.
- Servicios por dominio.
- Tipos TypeScript por dominio.
- Estilos globales.

#### Módulos visuales disponibles

- Dashboard.
- Usuarios.
- Productos.
- Inventario.
- Ventas.
- Compras.
- CRM.
- Pacientes.
- Laboratorio.
- Finanzas.
- Facturación.
- Reportes.
- Operación.
- Administración.

### 2.2 Backend API

Se ampliaron endpoints y servicios para soportar la operación visual:

- `productos`: listado, búsqueda, lectura, actualización y baja lógica.
- `usuarios`: perfil, roles, búsqueda, paginación y UUIDs en parámetros.
- `crm`: clientes, pacientes y recetas.
- `compras`: listado de órdenes y flujos de compra.
- `ventas`: integración con UI de ventas.
- `inventario`: kardex, entradas, salidas, alertas y valuación.
- `laboratorio`: órdenes, etapas, consumos y control de calidad.
- `facturacion`: listado, detalle, emisión y cancelación.
- `garantias`: listado, detalle, creación, reclamaciones y resolución.
- `nomina`: empleados, periodos, cálculo y confirmación.
- `tesoreria`: cuentas bancarias, movimientos, importación y conciliación.
- `presupuestos`: centros de costo, presupuestos y compromisos.
- `reportes`: contabilidad, inventario, márgenes, auditoría y métricas.
- `observabilidad` / `outbox`: métricas runtime, readiness, mantenimiento idempotency y operación de eventos.

### 2.3 Seeds y datos demo

Se mejoró el proceso de datos iniciales:

- Seed base idempotente en `backend/app/core/seed.py`.
- Script demo idempotente en `backend/scripts/seed_demo_data.py`.
- Target `seed-demo` en `backend/Makefile`.
- Plantillas `.env.example` y `.env.test` para desarrollo/pruebas.

### 2.4 Calidad y pruebas

Se agregaron o ajustaron pruebas para:

- Workflows de laboratorio.
- Workflows de presupuesto.
- Workflows de tesorería.
- Infraestructura de fixtures backend.
- Validación de endpoints, RBAC, migraciones, auditoría, outbox y operación.

En frontend se verificó:

- `npm run lint`.
- `npm run typecheck`.
- `npm run build`.

---

## 3. Estructura Docker Compose disponible

### 3.1 `docker-compose.yml`

Uso principal: desarrollo local completo.

Servicios incluidos:

- `postgres`: PostgreSQL principal en puerto `5432`.
- `redis`: Redis principal en puerto `6379`.
- `mongodb`: MongoDB principal en puerto `27017`.
- `backend`: FastAPI en puerto `8000`.
- `redis-commander`: UI opcional Redis en puerto `8081`.
- `mongo-express`: UI opcional MongoDB en puerto `8082`.

### 3.2 `docker-compose.test.yml`

Uso principal: servicios efímeros para pruebas backend.

Servicios incluidos:

- `postgres-test`: PostgreSQL de pruebas en puerto host `55432`.
- `redis-test`: Redis de pruebas en puerto host `56379`.
- `mongodb-test`: MongoDB de pruebas en puerto host `57017`.

Estos servicios usan `tmpfs`, por lo que los datos se descartan al detenerlos con `down -v`.

---

## 4. Requisitos recomendados para pruebas

### 4.1 Requisitos del sistema

Instalar o tener disponible:

- Docker.
- Docker Compose v2 (`docker compose`).
- Python 3.12 recomendado para backend.
- Node.js LTS recomendado para frontend.
- npm.

> Nota importante: el backend usa `python:3.12-slim` en Dockerfile. Para evitar fricción con dependencias condicionales de Python 3.14, se recomienda usar Python 3.12 localmente para pruebas backend.

### 4.2 Verificación rápida de versiones

Desde la raíz del repositorio:

```bash
docker --version
docker compose version
python --version
node --version
npm --version
```

---

## 5. Flujo recomendado para pruebas backend con Docker Compose

Este es el flujo recomendado para ejecutar pruebas backend usando Docker Compose para levantar PostgreSQL, Redis y MongoDB de pruebas.

### Paso 1: ubicarse en la raíz del repositorio

```bash
cd /ruta/al/repositorio/exSoftOptic
```

### Paso 2: levantar servicios efímeros de pruebas

```bash
docker compose -f docker-compose.test.yml up -d
```

### Paso 3: verificar estado de contenedores

```bash
docker compose -f docker-compose.test.yml ps
```

Esperado:

- `postgres-test` healthy.
- `redis-test` healthy.
- `mongodb-test` healthy.

### Paso 4: revisar logs si algo no queda healthy

```bash
docker compose -f docker-compose.test.yml logs postgres-test
docker compose -f docker-compose.test.yml logs redis-test
docker compose -f docker-compose.test.yml logs mongodb-test
```

### Paso 5: preparar entorno Python backend

Desde la raíz del repo:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

> Si se usa Windows PowerShell:
>
> ```powershell
> cd backend
> py -3.12 -m venv .venv
> .\.venv\Scripts\Activate.ps1
> python -m pip install --upgrade pip
> pip install -r requirements-dev.txt
> ```

### Paso 6: inicializar override local de test si hace falta

```bash
make test-env-init
```

Esto crea `backend/.env.test.local` desde la plantilla sin sobrescribir configuraciones locales existentes.

### Paso 7: validar readiness de configuración de pruebas

```bash
make test-readiness
```

### Paso 8: esperar conectividad TCP de servicios

```bash
make test-services-wait
```

### Paso 9: ejecutar pruebas completas backend

```bash
pytest -q
```

O usando Makefile:

```bash
make test
```

### Paso 10: ejecutar pruebas por áreas críticas

```bash
pytest tests/test_lab_workflow.py -q
pytest tests/test_budget_workflow.py -q
pytest tests/test_treasury_workflow.py -q
pytest tests/test_invoice_workflow.py -q
pytest tests/test_sales_workflow.py -q
pytest tests/test_purchase_workflow.py -q
pytest tests/test_reports.py -q
```

### Paso 11: bajar servicios de pruebas

Desde `backend/`:

```bash
make test-services-down
```

O desde la raíz:

```bash
docker compose -f docker-compose.test.yml down -v
```

---

## 6. Flujo alternativo: targets Makefile para servicios de pruebas

Desde `backend/`:

```bash
make test-services-up
make test-services-wait
pytest -q
make test-services-down
```

Para ver logs:

```bash
make test-services-logs
```

---

## 7. Flujo recomendado para levantar ambiente de desarrollo completo

Este flujo levanta backend y dependencias principales para operar manualmente el sistema.

### Paso 1: levantar stack principal

Desde la raíz:

```bash
docker compose up -d --build
```

### Paso 2: verificar contenedores

```bash
docker compose ps
```

Esperado:

- `optica_postgres` healthy.
- `optica_redis` healthy.
- `optica_mongodb` healthy.
- `optica_backend` running/healthy.

### Paso 3: revisar logs backend

```bash
docker compose logs -f backend
```

### Paso 4: aplicar migraciones dentro del backend

```bash
docker compose exec backend alembic upgrade head
```

### Paso 5: cargar seed base

```bash
docker compose exec backend python -m app.core.seed
```

### Paso 6: cargar seed demo

```bash
docker compose exec backend python scripts/seed_demo_data.py
```

### Paso 7: validar health/readiness

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

### Paso 8: abrir documentación API

```text
http://localhost:8000/docs
```

### Paso 9: detener stack principal

```bash
docker compose down
```

Si se quiere borrar volúmenes:

```bash
docker compose down -v
```

---

## 8. Flujo recomendado para frontend

### Paso 1: instalar dependencias

Desde la raíz:

```bash
cd frontend
npm install
```

### Paso 2: configurar URL de API

Opcional si se usa el default/proxy:

```bash
cp .env.example .env.local
```

Contenido recomendado si el backend corre en `localhost:8000`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Paso 3: ejecutar validaciones frontend

```bash
npm run lint
npm run typecheck
npm run build
```

### Paso 4: correr frontend en modo desarrollo

```bash
npm run dev
```

Abrir:

```text
http://localhost:5173
```

### Paso 5: credenciales demo esperadas

```text
admin / Admin123!
```

> Las credenciales dependen de que se hayan ejecutado `seed` y `seed-demo` correctamente.

---

## 9. Checklist de pruebas manuales por módulo

### 9.1 Autenticación

1. Abrir frontend.
2. Iniciar sesión con usuario demo.
3. Verificar que redirige a Dashboard.
4. Recargar navegador y confirmar que la sesión se hidrata.
5. Cerrar sesión.

### 9.2 Dashboard

1. Verificar métricas principales.
2. Confirmar que errores API se muestran de forma controlada.

### 9.3 Productos

1. Listar productos.
2. Buscar por texto.
3. Crear producto.
4. Editar producto.
5. Eliminar/desactivar producto.
6. Confirmar que la tabla se actualiza.

### 9.4 Inventario

1. Seleccionar sucursal.
2. Registrar entrada manual.
3. Registrar salida manual.
4. Verificar kardex.
5. Revisar alertas de stock.

### 9.5 Ventas

1. Listar ventas.
2. Crear flujo de venta si aplica.
3. Confirmar venta.
4. Revisar estado final.

### 9.6 Compras

1. Listar órdenes de compra.
2. Crear/consultar orden.
3. Validar estados y totales.

### 9.7 CRM y pacientes

1. Crear cliente.
2. Crear paciente asociado.
3. Crear receta.
4. Confirmar que los listados muestran registros.

### 9.8 Laboratorio

1. Crear orden desde venta confirmada.
2. Iniciar orden.
3. Avanzar etapas.
4. Registrar consumo.
5. Registrar control de calidad.
6. Entregar orden.

### 9.9 Facturación y garantías

1. Emitir factura desde venta confirmada.
2. Revisar detalle fiscal.
3. Revisar líneas y eventos.
4. Cancelar factura si está timbrada.
5. Crear garantía.
6. Abrir reclamación.
7. Resolver reclamación.

### 9.10 Finanzas, tesorería y presupuestos

1. Crear cuenta contable.
2. Crear periodo contable.
3. Crear cuenta bancaria.
4. Registrar movimiento bancario.
5. Crear centro de costo.
6. Crear presupuesto.
7. Comprometer presupuesto.
8. Revisar listados y selección automática.

### 9.11 Reportes

1. Seleccionar rango de fechas.
2. Revisar balanza.
3. Revisar estado de resultados.
4. Revisar inventario valuado.
5. Revisar márgenes.
6. Revisar auditoría y observabilidad.

### 9.12 Operación

1. Ver readiness.
2. Ver métricas runtime.
3. Crear evento outbox manual.
4. Marcar evento como processing/published/failed.
5. Ejecutar dispatch.
6. Ejecutar limpieza de idempotency.

### 9.13 Administración

1. Crear impuesto.
2. Crear serie/folio.
3. Registrar tipo de cambio.
4. Crear regla contable.
5. Crear empleado.
6. Crear periodo de nómina.
7. Calcular nómina.
8. Confirmar nómina.

---

## 10. Comandos de verificación recomendados antes de PR

Desde `frontend/`:

```bash
npm run lint
npm run typecheck
npm run build
```

Desde `backend/` con servicios de pruebas levantados:

```bash
make test-readiness
make test-services-wait
pytest -q
make migrate-verify
make security-audit
make api-contract-audit
make rbac-audit
make pagination-audit
```

Desde la raíz:

```bash
git status --short
git diff --check
```

---

## 11. Troubleshooting

### 11.1 `ModuleNotFoundError: No module named 'dotenv'`

Causa: dependencias backend no instaladas.

Solución:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 11.2 Servicios de pruebas no conectan

Verificar contenedores:

```bash
docker compose -f docker-compose.test.yml ps
```

Revisar logs:

```bash
docker compose -f docker-compose.test.yml logs postgres-test
```

Reiniciar todo:

```bash
docker compose -f docker-compose.test.yml down -v
docker compose -f docker-compose.test.yml up -d
```

### 11.3 Problemas con Python 3.14

El Dockerfile del backend usa Python 3.12, por lo que la recomendación para pruebas locales es usar Python 3.12. Python 3.14 puede intentar resolver dependencias desde repositorios Git en lugar de paquetes PyPI estables.

### 11.4 Frontend no conecta al backend

Verificar `.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Verificar backend:

```bash
curl http://localhost:8000/health
```

### 11.5 Login demo no funciona

Confirmar que se ejecutaron seeds:

```bash
docker compose exec backend python -m app.core.seed
docker compose exec backend python scripts/seed_demo_data.py
```

---

## 12. Orden recomendado para continuar el desarrollo

1. Ejecutar pruebas backend completas en entorno Python 3.12 con `docker-compose.test.yml`.
2. Corregir cualquier falla de tests.
3. Completar CRUDs visuales restantes por módulo.
4. Agregar pruebas E2E de frontend con Playwright o Cypress.
5. Automatizar CI con:
   - backend lint/test/migrations/audits.
   - frontend lint/typecheck/build.
6. Generar y versionar contrato OpenAPI.
7. Crear cliente frontend desde OpenAPI cuando el contrato esté estable.
8. Preparar Docker Compose de frontend o contenedor estático para despliegue.

---

## 13. Estado final sugerido para validar la entrega

La entrega debe considerarse lista cuando pasen:

```bash
# Frontend
cd frontend
npm run lint
npm run typecheck
npm run build

# Backend
cd ../backend
make test-services-up
make test-services-wait
pytest -q
make migrate-verify
make security-audit
make api-contract-audit
make rbac-audit
make pagination-audit
make test-services-down
```

Y el stack completo debe levantar con:

```bash
cd ..
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.core.seed
docker compose exec backend python scripts/seed_demo_data.py
```

Finalmente validar manualmente:

```text
Backend API: http://localhost:8000/docs
Frontend:    http://localhost:5173
```
