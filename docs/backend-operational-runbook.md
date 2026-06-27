# Backend operational runbook

This runbook documents the minimum steps to operate and verify the backend in development, CI and production-like environments.

## 1. Required environment

Copy `backend/.env.example` to `backend/.env` and set production-safe secrets before deploying.

Critical variables:

| Area | Variables | Notes |
| --- | --- | --- |
| Security | `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` | Rotate secrets outside the repository and never reuse development values. |
| Database | `DATABASE_URL`, `DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW` | `DATABASE_URL` must use the async PostgreSQL driver. |
| Cache | `REDIS_URL`, `REDIS_CACHE_TTL` | Required by runtime cache/session integrations. |
| CFDI | `CFDI_PROVIDER`, `CFDI_API_URL`, `CFDI_API_KEY`, `CFDI_TIMEOUT_SECONDS` | Use `MOCK` only for local/test environments; use `HTTP`/`API` for provider gateways. |
| Banking | `BANKING_PROVIDER`, `BANKING_API_URL`, `BANKING_API_KEY`, `BANKING_TIMEOUT_SECONDS` | Use `CSV` for manual imports or `HTTP`/`API` for banking gateways. |

## 2. Local verification

Run from `backend/`:

```bash
make verify-fast
make security-audit
make config-audit
make migrate-verify
make ci
make e2e
```

If dependency installation is needed:

```bash
python -m pip install -r requirements-dev.txt
```

## 3. Migration workflow

1. Create migrations with `make migrate msg="description"`.
2. Review generated DDL before committing.
3. Apply locally with `make migrate-up`.
4. Validate roundtrip behavior with `make migrate-verify`.
5. CI must run `python scripts/verify_migrations.py --roundtrip` before merge.

## 4. Outbox operations

The transactional outbox decouples domain transactions from external dispatch.

Run a single dispatch batch:

```bash
make outbox-worker-once
```

Run continuously:

```bash
make outbox-worker
```

Operational expectations:

- Monitor pending and failed events through `/api/v1/outbox` endpoints.
- Investigate repeated failures before increasing retry windows.
- Keep external providers idempotent because events may be retried.

## 5. Production integrations

### CFDI/e-invoicing

- Local/test: `CFDI_PROVIDER=MOCK`.
- Production gateway: `CFDI_PROVIDER=HTTP` or `CFDI_PROVIDER=API` with `CFDI_API_URL` and `CFDI_API_KEY`.
- The provider contract is `POST /invoices` and `POST /invoices/{uuid_fiscal}/cancel`.

### Banking statements

- Manual imports: `BANKING_PROVIDER=CSV` and provide CSV content to the treasury import endpoint.
- Production gateway: `BANKING_PROVIDER=HTTP` or `BANKING_PROVIDER=API` with `BANKING_API_URL` and `BANKING_API_KEY`.
- The provider contract is `GET /accounts/{account_number}/statement?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`.

## 6. Security and endpoint governance

Before merging backend endpoint changes, run:

```bash
make security-audit
```

The audit checks that non-public API endpoints declare authentication and permission dependencies. New endpoints should also record audit events for business-sensitive writes.


## 8. Runtime configuration audit

Before deploying with production variables, run:

```bash
make config-audit
```

For explicit production validation, use:

```bash
ENVIRONMENT=production python scripts/validate_runtime_config.py --strict
```

The validator blocks unsafe defaults, missing provider credentials, non-async PostgreSQL URLs, invalid timeouts and permissive production CORS values.




## 11. RBAC permission governance

The backend permission catalog is generated from endpoint `require_permissions([...])` declarations:

```bash
make permissions-catalog
python scripts/generate_permission_catalog.py --check
```

Review [`docs/backend-permissions.md`](backend-permissions.md) when creating or changing roles. Operational rules:

- Avoid assigning `*` outside emergency super-admin roles.
- Prefer module wildcards such as `ventas.*` only for module owners.
- Assign granular permissions for cashier, inventory, lab, treasury and reporting users.
- Re-run the catalog generator after adding endpoints or changing permission names.

## 10. Observability and SRE checks

Runtime metrics are available for authorized operators in two formats:

```bash
GET /api/v1/observabilidad/metrics
GET /api/v1/observabilidad/metrics/prometheus
```

Use the JSON endpoint for quick operator inspection and the Prometheus text endpoint for internal scrapers. Monitor at least:

- `exsoftoptic_requests_total` for traffic volume.
- `exsoftoptic_responses_total{status_code=...}` for 4xx/5xx trends.
- `exsoftoptic_exceptions_total` for unhandled runtime errors.
- `exsoftoptic_request_latency_average_ms` for latency regressions.
- Outbox failed/pending events through `/api/v1/outbox` endpoints.

## 9. Database backup and recovery

Create a PostgreSQL custom-format backup:

```bash
make db-backup
```

Restore a backup into the configured `DATABASE_URL`:

```bash
make db-restore file=./backups/exsoftoptic-backend-YYYYMMDDTHHMMSSZ.dump
```

Dry-run the generated commands without touching the database:

```bash
python scripts/manage_database_backup.py backup --dry-run
python scripts/manage_database_backup.py restore --input ./backups/example.dump --clean --dry-run
```

Operational expectations:

- Store backups outside the application host and outside git.
- Encrypt backups at rest in production environments.
- Test restores against disposable databases before relying on a backup policy.
- Run `make migrate-verify` after restore validation when schema changes are part of the release.

## 7. Release checklist

Before tagging or deploying:

- [ ] `.env` values are production-safe and secrets are managed outside git.
- [ ] `make verify-fast` passes.
- [ ] `make security-audit` passes.
- [ ] `python scripts/generate_permission_catalog.py --check` passes.
- [ ] `make config-audit` passes with target environment variables.
- [ ] `make migrate-verify` passes against a disposable database.
- [ ] A recent database backup exists and restore has been tested in a disposable environment.
- [ ] `make ci` passes with a real test database.
- [ ] `make e2e` passes.
- [ ] Outbox worker deployment is configured if integrations are enabled.
- [ ] CFDI and banking provider credentials are configured for the target environment.
