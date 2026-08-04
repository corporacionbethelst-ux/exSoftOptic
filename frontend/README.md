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

### Error `react-hooks/set-state-in-effect` en `src/lib/useApiResource.ts`

La implementación vigente del hook está en `src/hooks/useApiResource.ts`. El archivo
`src/lib/useApiResource.ts` solo conserva una reexportación por compatibilidad con imports
anteriores. Si ESLint muestra una llamada `if (enabled) void load()` dentro de
`src/lib/useApiResource.ts`, la copia local está desactualizada o tiene cambios sin integrar.

Desde la raíz del repositorio, comprueba y restaura exclusivamente ambos archivos:

```bash
git status --short -- frontend/src/lib/useApiResource.ts frontend/src/hooks/useApiResource.ts
git restore --source=HEAD -- frontend/src/lib/useApiResource.ts frontend/src/hooks/useApiResource.ts
npm ci --prefix frontend
npm run lint --prefix frontend
```

La primera orden permite comprobar si se descartará algún cambio local. No ejecutes
`git restore` si necesitas conservar esas modificaciones: guárdalas primero con `git diff`
o `git stash`. El aviso de una nueva versión de npm es informativo y no causa este error.

## Desarrollo local

Desde la raíz del repo:

```bash
cd backend
make db-up
make migrate-up
make seed
make seed-demo
make run
```

`make seed-demo` necesita una conexión activa a PostgreSQL. Si aparece
`Connect call failed ('127.0.0.1', 5432)`, la base principal no está levantada o
`DATABASE_URL` apunta a un puerto incorrecto. `make db-up` usa el archivo
`docker-compose.yml` de la raíz y espera a que PostgreSQL esté saludable sin
levantar otra instancia del backend que compita con `make run` por el puerto 8000.

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

### Frontend con Docker Compose

Desde la raíz del repositorio puedes compilar y levantar el frontend junto al backend:

```bash
docker compose up -d --build frontend
docker compose ps frontend
```

El contenedor publica la aplicación en `http://localhost:5173`. Nginx sirve el build
estático y redirige `/api`, `/health` y `/ready` al servicio `backend` dentro de la
red de Compose, por lo que el navegador no necesita resolver el nombre interno del
contenedor.

Para reconstruir el frontend después de modificar su código:

```bash
docker compose up -d --build --force-recreate frontend
```

Para consultar sus logs o detenerlo:

```bash
docker compose logs -f frontend
docker compose stop frontend
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
