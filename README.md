# exSoftOptic
Sistema de ventas e inventario para opticas

## Backend operations

Antes de levantar Docker Compose por primera vez, copia `.env.example` a `.env` en la raíz y cambia las contraseñas y `SECRET_KEY` para cualquier entorno compartido o productivo.

Operational backend setup, verification commands, migration workflow, outbox worker usage, production integrations and release checklist are documented in [`docs/backend-operational-runbook.md`](docs/backend-operational-runbook.md).

El avance hacia producción se controla con la [ruta de producción en 15 fases](docs/production-roadmap.md). Ejecute `make readiness-fast` para la puerta local sin servicios o `make readiness` para la validación completa con Docker, pruebas backend y migraciones.


## Frontend operations

El frontend React/Vite vive en [`frontend/`](frontend/). Puede iniciarse localmente con
`npm install && npm run dev` desde `frontend/`, o como build estático en Nginx con
`docker compose up -d --build frontend` desde la raíz. Antes de probar flujos demo,
ejecuta `make seed-demo` en `backend`.
