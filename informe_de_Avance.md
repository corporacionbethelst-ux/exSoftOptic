# Informe de Avance — Plan profesional de continuidad backend

**Proyecto:** exSoftOptic  
**Módulo:** Backend  
**Fecha de creación:** 2026-07-04  
**Tipo de documento:** informe vivo / bitácora actualizable de avance  
**Referencia principal:** `informe_de_proyecto.md`

---

## 1. Propósito del documento

Este documento complementa el informe general del proyecto y servirá como una bitácora viva para registrar cómo se abordarán los puntos faltantes, importantes y siguientes del backend.

La intención es que este archivo se actualice cada vez que se avance en una etapa, dejando evidencia de:

- Qué punto se trabajó.
- Por qué era importante.
- Qué metodología se aplicó.
- Qué archivos o módulos se tocaron.
- Qué validaciones se ejecutaron.
- Qué riesgos quedaron abiertos.
- Qué punto sigue.

---

## 2. Estado actual resumido

Los puntos estructurales previos ya fueron completados:

| Punto | Estado | Resultado |
|---:|---|---|
| 1 | Completado | Importador real de roles base a base de datos. |
| 2 | Completado | Seed mínimo de datos para smoke/manual QA. |
| 3 | Completado | Auditoría RBAC estática extendida. |
| 4 | Completado | Auditoría estática de contrato API. |
| 5 | Completado | Auditoría estática extendida de migraciones. |
| 6 | Completado | Orden final de verificación backend documentado. |
| 7 | Completado | Informe general del proyecto creado en `informe_de_proyecto.md`. |

Con estos puntos cerrados, el backend está listo para avanzar a una fase más práctica: instalación de dependencias, ejecución real de servicios efímeros, migraciones, pruebas completas, corrección de fallos, estabilización y preparación para QA/staging.

---

## 3. Metodología para abordar los siguientes puntos

La continuidad del proyecto debe abordarse con una metodología de avance controlado:

### 3.1. Primero validar entorno

Antes de tocar lógica adicional, se debe confirmar que el entorno local o CI puede instalar dependencias y levantar servicios.

Objetivo:

- Evitar confundir errores de ambiente con errores reales de backend.
- Confirmar Python, dependencias, PostgreSQL, Redis y MongoDB.
- Ejecutar preflight y auditorías estáticas antes de pruebas pesadas.

### 3.2. Después ejecutar migraciones en base desechable

Las migraciones deben validarse en una base de datos disposable o de CI.

Objetivo:

- Confirmar que el esquema completo se puede crear desde cero.
- Confirmar que el roundtrip `upgrade -> downgrade -> upgrade` funciona.
- Detectar errores de constraints, tipos, foreign keys o índices antes de QA/staging.

### 3.3. Luego correr pruebas por capas

La suite debe ejecutarse de forma gradual:

1. Auditorías estáticas.
2. Verificación rápida de dependencias/sintaxis.
3. Migraciones.
4. Tests unitarios y de servicios.
5. Tests de scripts operativos.
6. Tests de endpoints/API.
7. Smoke E2E.
8. Load smoke básico.

### 3.4. Corregir fallos en ciclos cortos

Cada fallo debe resolverse con una metodología simple:

1. Reproducir el fallo.
2. Identificar si es ambiente, migración, modelo, servicio, schema, endpoint o test.
3. Corregir el menor alcance posible.
4. Ejecutar el test afectado.
5. Ejecutar la auditoría relacionada.
6. Registrar el avance.

### 3.5. Registrar cada hito

Cada avance debe actualizar este archivo con:

- Fecha.
- Punto abordado.
- Resultado.
- Comandos ejecutados.
- Estado final.
- Siguiente punto.

---

## 4. Puntos faltantes/importantes para avanzar

### Punto A — Instalación controlada de dependencias

**Estado:** pendiente.  
**Prioridad:** alta.  
**Objetivo:** instalar dependencias de desarrollo para poder ejecutar imports reales, pytest y smoke E2E.

#### Cómo abordarlo

1. Entrar al backend:

```bash
cd backend
```

2. Actualizar pip:

```bash
python -m pip install --upgrade pip
```

3. Instalar dependencias de desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

4. Validar instalación:

```bash
python scripts/verify_backend.py --skip-pytest
```

#### Criterio de éxito

- `verify_backend.py --skip-pytest` debe pasar sin módulos faltantes.
- No deben aparecer errores de importación de FastAPI, SQLAlchemy, Pydantic, asyncpg ni httpx.

#### Riesgos

- Falla por red/PyPI.
- Conflictos de versiones.
- Dependencias OS faltantes para WeasyPrint/reportes.

#### Acción si falla

- Registrar paquete faltante.
- Validar si está en `requirements.txt` o `requirements-dev.txt`.
- Revisar librerías OS si el error viene de PDF/rendering.

---

### Punto B — Levantar servicios efímeros de prueba

**Estado:** pendiente.  
**Prioridad:** alta.  
**Objetivo:** tener PostgreSQL, Redis y MongoDB aislados para pruebas backend.

#### Cómo abordarlo

```bash
cd backend
make test-services-up
make test-services-wait
```

#### Criterio de éxito

- PostgreSQL acepta conexiones.
- Redis acepta conexiones.
- MongoDB acepta conexiones.
- `wait_for_test_services.py` finaliza exitosamente.

#### Riesgos

- Docker no disponible.
- Puertos ocupados.
- Servicios tardan más en iniciar.

#### Acción si falla

- Revisar puertos de `docker-compose.test.yml`.
- Ejecutar logs:

```bash
make test-services-logs
```

- Bajar y limpiar servicios:

```bash
make test-services-down
```

---

### Punto C — Validación real de migraciones

**Estado:** pendiente.  
**Prioridad:** alta.  
**Objetivo:** validar que todo el esquema Alembic se puede crear, bajar y recrear en DB desechable.

#### Cómo abordarlo

Primero auditoría estática:

```bash
cd backend
make migration-audit
```

Luego validación real:

```bash
make migrate-verify
```

#### Criterio de éxito

- `audit_migrations_static.py` pasa.
- `verify_migrations.py --roundtrip` pasa.
- Alembic termina en `head` después del roundtrip.

#### Riesgos

- Foreign keys fuera de orden.
- Constraints duplicadas.
- Tipos incompatibles.
- Diferencias entre modelos y migraciones.

#### Acción si falla

- Identificar revisión Alembic exacta.
- Revisar `down_revision`.
- Revisar orden de creación/drop.
- Corregir migración, no solo modelo.
- Volver a correr auditoría estática y roundtrip.

---

### Punto D — Ejecutar suite completa de backend

**Estado:** pendiente.  
**Prioridad:** alta.  
**Objetivo:** confirmar que servicios, scripts, endpoints y flujos funcionan con dependencias instaladas.

#### Cómo abordarlo

```bash
cd backend
make verify
```

O equivalente:

```bash
python scripts/verify_backend.py
```

#### Criterio de éxito

- Verificación de dependencias pasa.
- Sintaxis/imports pasan.
- Pytest completo pasa.

#### Riesgos

- Tests con fixtures incompletos.
- Modelos y migraciones inconsistentes.
- Endpoints que requieren datos base.
- Servicios externos simulados incorrectamente.

#### Acción si falla

- Ejecutar test puntual con `-q` o `-vv`.
- Separar fallo de entorno vs fallo de lógica.
- Corregir por dominio.
- Repetir suite del módulo afectado.

---

### Punto E — Ejecutar smoke E2E

**Estado:** pendiente.  
**Prioridad:** alta.  
**Objetivo:** validar el flujo mínimo API + DB.

#### Cómo abordarlo

```bash
cd backend
make e2e
```

Equivalente:

```bash
python -m pytest tests/test_e2e_smoke.py -q
```

#### Criterio de éxito

- `/health` responde correctamente.
- Flujo mínimo de producto/API funciona.
- Auditoría básica no rompe.

#### Riesgos

- App no importa por configuración.
- Dependencias faltantes.
- DB no disponible.
- Fixture de usuario/rol incompleta.

#### Acción si falla

- Revisar `tests/conftest.py`.
- Revisar variables `DATABASE_URL` y `TEST_DATABASE_URL`.
- Confirmar servicios efímeros activos.

---

### Punto F — Seed de roles y datos para QA/manual smoke

**Estado:** pendiente de ejecución.  
**Prioridad:** media-alta.  
**Objetivo:** preparar datos mínimos de prueba manual o QA.

#### Cómo abordarlo

1. Revisar roles:

```bash
cd backend
python scripts/generate_role_seed.py --check
```

2. Importar roles con dry-run:

```bash
python scripts/seed_roles.py --empresa-id 00000000-0000-0000-0000-000000000000 --dry-run
```

3. Ejecutar seed de datos con dry-run:

```bash
python scripts/seed_test_data.py --dry-run
```

4. Aplicar en DB de QA/local si todo está correcto:

```bash
make seed-test-data
```

#### Criterio de éxito

- Roles creados o actualizados.
- Empresa/sucursal/producto/usuario test disponibles.
- Seed idempotente en ejecuciones repetidas.

#### Riesgos

- Ejecutarlo accidentalmente en producción.
- Empresa de prueba colisiona con datos reales.
- Password hash no apto para login real.

#### Acción preventiva

- Solo usar en local, QA o staging desechable.
- Confirmar `DATABASE_URL` antes de ejecutar sin `--dry-run`.

---

### Punto G — Exportar OpenAPI y alinear con frontend/QA

**Estado:** pendiente.  
**Prioridad:** media.  
**Objetivo:** generar contrato API para revisión con frontend, QA y documentación.

#### Cómo abordarlo

```bash
cd backend
make openapi-export
```

Equivalente:

```bash
python scripts/export_openapi.py --output ../docs/openapi.json
```

#### Criterio de éxito

- Se genera `docs/openapi.json`.
- Frontend puede validar rutas, schemas y payloads.
- QA puede diseñar casos de prueba a partir del contrato.

#### Riesgos

- App no importa si faltan dependencias.
- Schemas Pydantic inválidos.
- Endpoints sin response model claro.

---

### Punto H — Ensayo de staging

**Estado:** pendiente.  
**Prioridad:** media.  
**Objetivo:** validar comportamiento similar a producción antes de despliegue real.

#### Cómo abordarlo

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml --profile migrations run --rm migration-job
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d backend outbox-worker
```

#### Criterio de éxito

- Migración one-shot funciona.
- Backend levanta sin modo reload.
- Worker outbox levanta.
- Healthcheck responde.

#### Riesgos

- Imagen no construida/tag incorrecto.
- Variables secret incompletas.
- DB persistente con estado previo incompatible.

---

### Punto I — Observabilidad y operación post-arranque

**Estado:** pendiente.  
**Prioridad:** media.  
**Objetivo:** confirmar que métricas, health, readiness, logs y outbox son observables.

#### Cómo abordarlo

1. Revisar `/health`.
2. Revisar readiness.
3. Revisar métricas.
4. Ejecutar worker una vez:

```bash
cd backend
make outbox-worker-once
```

5. Ejecutar limpieza operacional en DB de prueba:

```bash
make operational-cleanup empresa_id=00000000-0000-0000-0000-000000000000
```

#### Criterio de éxito

- Health/readiness OK.
- Métricas disponibles.
- Worker no falla.
- Limpieza imprime counters esperados.

---

### Punto J — Corrección de fallos detectados por pruebas

**Estado:** pendiente hasta correr suite real.  
**Prioridad:** variable según severidad.  
**Objetivo:** estabilizar backend con base en errores reales.

#### Cómo abordarlo

Para cada fallo:

1. Clasificar tipo:
   - dependencia,
   - configuración,
   - migración,
   - modelo,
   - schema,
   - servicio,
   - endpoint,
   - test,
   - infraestructura.
2. Reproducir localmente.
3. Corregir mínimo necesario.
4. Ejecutar test específico.
5. Ejecutar auditoría relacionada.
6. Registrar en este informe.

---

## 5. Orden recomendado de avance inmediato

El orden recomendado para continuar profesionalmente es:

1. **Instalar dependencias.**
2. **Ejecutar `verify_backend.py --skip-pytest`.**
3. **Levantar servicios efímeros.**
4. **Ejecutar auditoría estática de migraciones.**
5. **Ejecutar roundtrip Alembic.**
6. **Ejecutar suite completa.**
7. **Ejecutar smoke E2E.**
8. **Corregir fallos si aparecen.**
9. **Exportar OpenAPI.**
10. **Preparar seed QA/manual.**
11. **Ensayar staging.**
12. **Validar observabilidad/outbox/cleanup.**

---

## 6. Comandos recomendados para la próxima ejecución

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

## 7. Bitácora de avance

| Fecha | Punto | Estado | Evidencia | Siguiente acción |
|---|---|---|---|---|
| 2026-07-04 | Creación del informe de avance | Completado | `informe_de_Avance.md` | Instalar dependencias y ejecutar verificación rápida. |

---

## 8. Criterios para marcar un punto como completado

Un punto se marcará como completado solo si cumple:

1. Código o documentación aplicada.
2. Comando asociado ejecutado.
3. Resultado registrado.
4. Riesgos identificados.
5. Siguiente paso definido.
6. Commit realizado.
7. PR registrado cuando aplique.

---

## 9. Estado final de este informe

Este documento queda creado como bitácora viva para actualizarse en cada avance. La siguiente actualización recomendada debe hacerse después de instalar dependencias y ejecutar:

```bash
cd backend
python scripts/verify_backend.py --skip-pytest
```

En esa próxima actualización se debe registrar:

- Resultado de instalación.
- Paquetes faltantes si los hubiera.
- Resultado de imports/sintaxis.
- Bloqueadores detectados.
- Siguiente punto técnico.
