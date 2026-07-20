# Frontend ExSoftOptic

Aplicación web administrativa para consumir el backend de ExSoftOptic. Está pensada como punto de partida productivo para el panel de administración y operación de la óptica.

## Stack

- React + TypeScript
- Vite
- CSS propio sin dependencia de UI externa
- Cliente API con `fetch` y token Bearer persistido en `localStorage`


## Arquitectura de carpetas

```text
src/
  app/             # bootstrap, providers y raíz de aplicación
  components/      # componentes UI reutilizables y agnósticos del dominio
  config/          # lectura de variables de entorno y configuración runtime
  features/        # pantallas y módulos orientados al negocio
  hooks/           # hooks compartidos para estado asíncrono y UI
  layout/          # shell autenticado, sidebar, topbar y layouts base
  routes/          # definición de navegación y resolución de páginas
  services/        # clientes por dominio, HTTP client y storage
  styles/          # estilos globales/tokens visuales
  types/           # contratos TypeScript por dominio
  utils/           # helpers puros de formato y transformación
```

La intención es mantener separación clara entre UI, casos de uso, contratos, transporte HTTP y configuración para poder crecer hacia módulos CRUD completos sin mezclar responsabilidades.

## Variables de entorno

Copia el ejemplo si necesitas apuntar a otra URL de backend:

```bash
cp .env.example .env.local
```

```env
VITE_API_BASE_URL=http://localhost:8000
```

Si no defines `VITE_API_BASE_URL`, Vite usa los proxies configurados para `/api`, `/health` y `/ready`.

## Instalación de dependencias

Antes de ejecutar `npm run lint`, `npm run typecheck`, `npm run build` o `npm run dev`, instala las dependencias locales del frontend:

```bash
cd frontend
npm install
```

En entornos de CI o cuando ya exista `package-lock.json`, usa instalación reproducible:

```bash
cd frontend
npm ci
```

Si ves el error `sh: 1: eslint: not found`, significa que `node_modules/` no existe o está incompleto. Ejecuta `npm install` desde `frontend/` y vuelve a correr `npm run lint`.

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
