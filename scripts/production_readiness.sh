#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:---fast}"

if [[ "$MODE" != "--fast" && "$MODE" != "--full" ]]; then
  echo "Uso: $0 [--fast|--full]" >&2
  exit 2
fi

run() {
  local label="$1"
  shift
  printf '\n==> %s\n' "$label"
  "$@"
}

cd "$ROOT_DIR"

run "Sintaxis de scripts Python" python3 -m compileall -q backend/app backend/scripts
run_backend() {
  local label="$1"
  shift
  run "$label" bash -c 'cd "$1" && shift && "$@"' _ "$ROOT_DIR/backend" "$@"
}

run_backend "Contrato estatico de la API" python3 scripts/audit_api_contract.py
run_backend "Seguridad declarativa de endpoints" python3 scripts/audit_api_security.py
run_backend "Grafo de migraciones" python3 scripts/audit_migrations_static.py
run_backend "Cobertura RBAC" python3 scripts/audit_rbac_coverage.py
run_backend "Catalogo de permisos actualizado" python3 scripts/generate_permission_catalog.py --check
run_backend "Roles base actualizados" python3 scripts/generate_role_seed.py --check
run "Lint del frontend" npm --prefix frontend run lint
run "Tipos del frontend" npm --prefix frontend run typecheck
run "Build del frontend" npm --prefix frontend run build

if [[ "$MODE" == "--fast" ]]; then
  printf '\nReadiness rapida completada. Use --full con Docker y dependencias backend disponibles.\n'
  exit 0
fi

command -v docker >/dev/null 2>&1 || {
  echo "ERROR: Docker es obligatorio para --full." >&2
  exit 1
}

run "Configuracion Docker Compose" docker compose config --quiet
run "Preflight de pruebas backend" bash -c 'cd backend && python3 scripts/check_test_readiness.py --strict'
run "Suite backend" bash -c 'cd backend && python3 scripts/verify_backend.py -- -q'
run "Migraciones desde cero y roundtrip" bash -c 'cd backend && python3 scripts/verify_migrations.py --roundtrip'

printf '\nReadiness completa aprobada. Aun se requiere aprobacion humana y smoke test en staging.\n'
