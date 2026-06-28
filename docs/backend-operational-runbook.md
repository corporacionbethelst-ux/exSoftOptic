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







## 14. Authentication, observability and integration resilience

The backend now includes three additional hardening layers:

- session security helpers for revoking sessions, cleaning up expired sessions and account lockout after repeated failures;
- per-route runtime metrics in Prometheus output through `exsoftoptic_route_responses_total`;
- retry policy helpers used by HTTP banking/CFDI provider adapters for transient provider failures.

Recommended operational checks:

```bash
python scripts/validate_runtime_config.py --environment production --strict
GET /api/v1/observabilidad/metrics/prometheus
```

Tune these settings per environment: `MAX_FAILED_LOGIN_ATTEMPTS`, `ACCOUNT_LOCK_MINUTES`, `CFDI_RETRY_ATTEMPTS` and `BANKING_RETRY_ATTEMPTS`.

## 13. Container deployment hardening

The backend image is built from `backend/Dockerfile` with:

- non-root `app` user;
- `.dockerignore` to avoid secrets, virtualenvs, logs, uploads and backups in images;
- `/health` Docker healthcheck;
- optional startup migrations through `RUN_MIGRATIONS_ON_START=true`;
- production default command without `--reload`.

Build locally:

```bash
docker build -t exsoftoptic-backend:local backend
```

Run with migrations explicitly enabled only when the deployment strategy allows it:

```bash
docker run --rm -e RUN_MIGRATIONS_ON_START=true --env-file backend/.env exsoftoptic-backend:local
```

Operational guidance:

- Prefer running migrations as a separate release job for multi-replica deployments.
- Keep `RUN_MIGRATIONS_ON_START=false` for horizontally scaled application pods.
- Never bake `.env`, backups, uploads or logs into the image.

## 12. Performance and load smoke checks

After starting the API locally or in staging, run a lightweight load smoke test:

```bash
make load-smoke
python scripts/load_smoke.py --url https://staging.example.com/health --requests 100 --concurrency 10 --max-p95-ms 750
```

Use this as a fast regression check, not as a full capacity test. Track:

- failure rate;
- average latency;
- p95 latency;
- 5xx responses during deployment windows;
- differences between `/health`, `/ready` and representative authenticated endpoints.

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

- [ ] `make test-readiness` reports no blockers before dependency installation.
- [ ] `.env` values are production-safe and secrets are managed outside git.
- [ ] `make verify-fast` passes.
- [ ] `make security-audit` passes.
- [ ] `python scripts/generate_permission_catalog.py --check` passes.
- [ ] `python scripts/audit_query_pagination.py --strict` passes with zero unbounded list endpoints.
- [ ] `make config-audit` passes with target environment variables.
- [ ] `make migrate-verify` passes against a disposable database.
- [ ] A recent database backup exists and restore has been tested in a disposable environment.
- [ ] `make ci` passes with a real test database.
- [ ] `make e2e` passes.
- [ ] `make load-smoke` or staging `scripts/load_smoke.py` passes against target health endpoints.
- [ ] Container image is built without secrets and runs as non-root.
- [ ] Outbox worker deployment is configured if integrations are enabled.
- [ ] CFDI and banking provider credentials are configured for the target environment.

## 17. Query performance and pagination audit

List endpoints must expose an explicit page-size boundary before they are promoted to production traffic. Run the static audit before adding new collection endpoints:

```bash
make pagination-audit
python scripts/audit_query_pagination.py --strict
```

The non-strict Makefile target is intended for discovery during development; use `--strict` in focused hardening branches once known findings have been remediated. Any endpoint that returns a list-like `response_model` should define `limit`, `page_size` or `per_page` and the service implementation should apply a bounded database query.

## 18. Baseline production roles seed

The permission catalog is the source of truth for system roles. Regenerate the seed after endpoint permissions change:

```bash
make permissions-catalog
make role-seed
python scripts/generate_role_seed.py --check
python scripts/seed_roles.py --empresa-id 00000000-0000-0000-0000-000000000000 --dry-run
```

The generated `backend/seeds/roles.base.json` contains emergency `SUPER_ADMIN`, company administrator and module-oriented roles for cashier, inventory, treasury, accounting, laboratory, reporting and operational support. Import it during tenant bootstrap only after reviewing whether module roles need to be reduced for the customer deployment.

## 19. Staging deployment rehearsal

Use the staging compose override to rehearse production-like behavior without development bind mounts or reload flags:

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml --profile migrations run --rm migration-job
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d backend outbox-worker
```

The staging override expects a prebuilt `exsoftoptic-backend:staging` image, disables automatic migrations on backend startup, and runs migrations through an explicit one-shot profile so rollouts can be controlled and audited.

## 20. OpenAPI contract artifact

Export the current API contract for frontend, QA and partner integration review:

```bash
make openapi-export
python scripts/export_openapi.py --output ../docs/openapi.json
```

Commit or publish the generated artifact when API compatibility needs review. Diff the OpenAPI JSON in pull requests that add, remove or rename endpoints, schemas or status-code responses.


## 21. Operational table retention

Run tenant-scoped cleanup jobs to keep idempotency and outbox tables compact without deleting active work:

```bash
make operational-cleanup empresa_id=00000000-0000-0000-0000-000000000000
python scripts/cleanup_operational_data.py --empresa-id 00000000-0000-0000-0000-000000000000 --outbox-published-days 30 --processing-timeout-minutes 15
```

The cleanup job removes expired idempotency keys, releases stale `PROCESSING` outbox events back to `PENDING` for retry and deletes old `PUBLISHED` outbox events. Schedule it per tenant during low-traffic windows and monitor the JSON counters it prints for unexpected spikes.


## 22. Backend test readiness preflight

Before installing dependencies or starting a full test run, execute the stdlib-only preflight:

```bash
make test-readiness
python scripts/check_test_readiness.py --strict
```

The preflight verifies Python version, repository files, critical requirement declarations and recommended environment variables without importing FastAPI, SQLAlchemy or test-only packages. Use the non-strict target for local setup guidance and `--strict` when preparing a CI-like environment.


## 23. Ephemeral backend test services

Before installing dependencies or running integration tests locally, copy the test env template and start disposable services:

```bash
cd backend
make test-env-init
make test-readiness
make test-services-up
make test-services-wait
```

The test compose file exposes isolated ports (`55432`, `56379`, `57017`) and uses `tmpfs` volumes so local verification does not mutate development data. Stop and remove them with:

```bash
make test-services-down
```


Use `make test-services-wait` after `make test-services-up` to block until PostgreSQL, Redis and MongoDB test ports accept TCP connections before installing dependencies or launching migration/test commands.


`make test-env-init` creates `backend/.env.test.local` from the tracked test template only when the file does not already exist. Use `python scripts/init_test_environment.py --force` only when intentionally resetting local test variables.


## 24. Baseline role import

After reviewing `backend/seeds/roles.base.json`, import or update the baseline roles for the target company:

```bash
cd backend
python scripts/seed_roles.py --empresa-id 00000000-0000-0000-0000-000000000000 --dry-run
make seed-roles empresa_id=00000000-0000-0000-0000-000000000000
```

The importer is idempotent: it creates missing roles, updates changed system roles and leaves unchanged roles untouched. Use `--dry-run` before writing to production or staging databases.


## 25. Minimal backend smoke dataset

After migrations and baseline roles are ready, create a deterministic company, branch, catalog product and admin-like test user for manual smoke checks:

```bash
cd backend
python scripts/seed_test_data.py --dry-run
make seed-test-data
```

The seed is idempotent and intentionally small: one company, one principal branch, one category, one brand, one optical frame product, one wildcard test role and one active test user. Use it only in local, QA or disposable staging databases; production tenants should be initialized with customer-approved data instead.
