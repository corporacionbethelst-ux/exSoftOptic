#!/usr/bin/env sh
set -eu

if [ "${RUN_MIGRATIONS_ON_START:-false}" = "true" ]; then
  echo "Running Alembic migrations before application start..."
  alembic upgrade head
fi

exec "$@"
