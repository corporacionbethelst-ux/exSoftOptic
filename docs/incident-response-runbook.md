# Incident response and on-call runbook

## Severity and response targets

| Severity | Example | Acknowledge | Update cadence | Target mitigation |
| --- | --- | --- | --- | --- |
| SEV-1 | Data exposure, total outage, fiscal corruption | 10 minutes | 30 minutes | 1 hour |
| SEV-2 | Major workflow unavailable, sustained 5xx/SLO breach | 20 minutes | 60 minutes | 4 hours |
| SEV-3 | Degraded non-critical feature or delayed integration | 4 business hours | Daily | 2 business days |
| SEV-4 | Cosmetic/support issue with workaround | 1 business day | As agreed | Planned release |

Targets must be approved against the commercial support agreement before launch.

## First 15 minutes

1. Create an incident channel and assign incident commander, technical lead and communications owner.
2. Record detection time, affected tenant(s), release SHA, symptoms and current severity.
3. Preserve evidence; do not paste secrets, patient details or full database rows into chat/tickets.
4. Run `make diagnostics` from an authorized application host and review the JSON before sharing.
5. Check `/health`, `/ready`, Prometheus alerts, recent deployment and outbox backlog.
6. For suspected data exposure, stop exports, preserve audit records and notify privacy/security owners.

## Mitigation decision tree

- **Recent release and broad regression:** stop rollout and execute the documented rollback.
- **Database unavailable:** verify provider status, connection exhaustion and storage; do not restart repeatedly.
- **Provider degraded:** verify circuit state and outbox; disable only the affected integration when safe.
- **Single tenant affected:** confirm tenant isolation before any data correction.
- **Capacity/SLO breach:** reduce non-essential workers, scale within approved bounds and preserve evidence.

## Safe diagnostic bundle

```bash
make diagnostics
python3 scripts/collect_incident_diagnostics.py \
  --base-url https://internal-api.example.com \
  --output artifacts/incident-INC-1234.json
```

The collector records host capacity, Git revision/status, health/readiness and Docker Compose status. It intentionally excludes environment variables, secrets and application logs. Operators must still review output before attachment.

## Communication template

```text
[SEV-N] exSoftOptic incident INC-YYYY-NNN
Started: <UTC timestamp>
Impact: <user-visible impact, tenants/regions, no personal details>
Current status: <investigating | identified | monitoring | resolved>
Mitigation: <action taken>
Next update: <UTC timestamp>
```

## Resolution and follow-up

1. Confirm health, readiness, error rate, latency and critical business smoke tests.
2. Reconcile uncertain sales, payments, invoices, inventory and provider operations.
3. Communicate resolution and monitoring period.
4. Complete a blameless review within five business days for SEV-1/SEV-2.
5. Assign every corrective action an owner, due date and verification method.
6. Update runbooks, alerts, tests and capacity assumptions from findings.
