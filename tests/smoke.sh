#!/usr/bin/env bash
# =============================================================================
# tests/smoke.sh — Pruebas de humo sobre endpoints críticos del backend.
# Verifica que /health responda 200 y que /auth/login responda
# 200 (credenciales válidas opcionales) o 401 (credenciales inválidas).
#
# Uso:
#   API_ROOT=http://localhost:8000 ./tests/smoke.sh
# Exit codes: 0 = todos los checks pasaron, 1 = al menos un fallo.
# =============================================================================
set -euo pipefail

API_ROOT="${API_ROOT:-http://localhost:8000}"
API_BASE_URL="${API_BASE_URL:-${API_ROOT}/api/v1}"
CURL_TIMEOUT="${CURL_TIMEOUT:-10}"
FAILED=0

log_ok()   { printf '  [OK]   %s\n' "$1"; }
log_fail() { printf '  [FAIL] %s\n' "$1"; FAILED=1; }

check_status() {
  # $1=url  $2=método  $3=cuerpo(JSON opcional)  $4...=estados aceptados
  local url="$1" method="$2" body="$3"; shift 3
  local code
  if [[ -n "$body" ]]; then
    code=$(curl -s -o /dev/null -w '%{http_code}' -X "$method" \
      -H 'Content-Type: application/json' -d "$body" \
      --max-time "$CURL_TIMEOUT" "$url" || echo "000")
  else
    code=$(curl -s -o /dev/null -w '%{http_code}' -X "$method" \
      --max-time "$CURL_TIMEOUT" "$url" || echo "000")
  fi
  for expected in "$@"; do
    if [[ "$code" == "$expected" ]]; then
      return 0
    fi
  done
  echo "$code" > /tmp/smoke_last_code
  return 1
}

echo "== Smoke: ExSoftOptic =="
echo "API_ROOT=$API_ROOT"
echo "API_BASE_URL=$API_BASE_URL"
echo

# 1. Health check raíz (esperado: 200)
if check_status "${API_ROOT}/health" GET "" 200; then
  log_ok "GET /health -> 200"
else
  log_fail "GET /health -> $(cat /tmp/smoke_last_code) (esperado 200)"
fi

# 2. Login con credenciales inválidas (esperado: 401/422, nunca 200/500)
if check_status "${API_BASE_URL}/auth/login" POST \
  '{"username":"smoke_invalid_user","password":"invalid_password"}' 401 422; then
  log_ok "POST /auth/login (inválido) -> 401/422"
else
  log_fail "POST /auth/login (inválido) -> $(cat /tmp/smoke_last_code) (esperado 401/422)"
fi

# 3. Ruta protegida sin token (esperado: 401 o 403)
if check_status "${API_BASE_URL}/auth/me" GET "" 401 403; then
  log_ok "GET /auth/me (sin token) -> 401/403"
else
  log_fail "GET /auth/me (sin token) -> $(cat /tmp/smoke_last_code) (esperado 401/403)"
fi

# 4. Login válido OPCIONAL (solo si se proveen credenciales por entorno)
if [[ -n "${SMOKE_USERNAME:-}" && -n "${SMOKE_PASSWORD:-}" ]]; then
  if check_status "${API_BASE_URL}/auth/login" POST \
    "{\"username\":\"${SMOKE_USERNAME}\",\"password\":\"${SMOKE_PASSWORD}\"}" 200; then
    log_ok "POST /auth/login (válido) -> 200"
  else
    log_fail "POST /auth/login (válido) -> $(cat /tmp/smoke_last_code) (esperado 200)"
  fi
else
  echo "  [SKIP] login válido (definir SMOKE_USERNAME/SMOKE_PASSWORD para habilitarlo)"
fi

echo
if [[ "$FAILED" -eq 0 ]]; then
  echo "RESULTADO: PASS ✅"
else
  echo "RESULTADO: FAIL ❌"
fi
exit "$FAILED"
