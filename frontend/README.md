# Frontend ExSoftOptic

Aplicación web administrativa para consumir el backend de ExSoftOptic. Está pensada como punto de partida productivo para el panel de administración y operación de la óptica.

## Stack

- React + TypeScript
- Vite
- CSS propio sin dependencia de UI externa
- Cliente API con `fetch` y token Bearer persistido en `localStorage`

## Variables de entorno

Copia el ejemplo si necesitas apuntar a otra URL de backend:

```bash
cp .env.example .env.local
```

```env
VITE_API_BASE_URL=http://localhost:8000
```

Si no defines `VITE_API_BASE_URL`, Vite usa los proxies configurados para `/api`, `/health` y `/ready`.

## Desarrollo local

Desde la raíz del repo:

```bash
cd backend
make migrate-up
make seed
make seed-demo
make run
```

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Abre:

```text
http://localhost:5173
```

Credenciales demo base:

```text
admin / Admin123!
```

## Pantallas iniciales

- Login
- Dashboard operativo
- Usuarios
- Productos
- Ventas
- Laboratorio

## Camino a producción

1. Completar formularios CRUD por módulo.
2. Generar cliente TypeScript desde `docs/openapi.json` cuando el contrato se estabilice.
3. Añadir pruebas de componentes y E2E.
4. Configurar CI para `npm run lint`, `npm run typecheck` y `npm run build`.
5. Servir `dist/` detrás de Nginx/CDN o contenedor estático.
