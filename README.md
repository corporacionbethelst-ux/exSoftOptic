# exSoftOptic
Sistema de ventas e inventario para opticas

## Backend operations

Antes de levantar Docker Compose por primera vez, copia `.env.example` a `.env` en la raíz y cambia las contraseñas y `SECRET_KEY` para cualquier entorno compartido o productivo.

Operational backend setup, verification commands, migration workflow, outbox worker usage, production integrations and release checklist are documented in [`docs/backend-operational-runbook.md`](docs/backend-operational-runbook.md).


## Frontend operations

El frontend React/Vite vive en [`frontend/`](frontend/). Puede iniciarse localmente con
`npm install && npm run dev` desde `frontend/`, o como build estático en Nginx con
`docker compose up -d --build frontend` desde la raíz. Antes de probar flujos demo,
ejecuta `make seed-demo` en `backend`.
