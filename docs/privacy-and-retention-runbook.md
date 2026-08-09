# Privacy, subject rights and retention runbook

This runbook defines the technical baseline for handling personal and clinical data. It does not replace jurisdiction-specific legal review.

## Data classification

| Classification | Examples | Required controls |
| --- | --- | --- |
| Public | Product descriptions, public branch details | Integrity and change control |
| Internal | Operational folios, inventory movements | Authentication and tenant isolation |
| Personal | Name, email, telephone, postal code, RFC | Least privilege, audit, encryption and retention limit |
| Sensitive clinical | Birth date, prescriptions, optical measurements, clinical notes | Restricted role, audit, encrypted backup and explicit legal basis |
| Secret | Password hashes, JWT signing keys, provider/API credentials | Secret manager, rotation, never log or export |

## Subject access export

Authorized privacy operators can produce a tenant-scoped JSON export:

```http
GET /api/v1/crm/privacy/clientes/{cliente_id}/export
Permission: privacidad.solicitudes.exportar
```

The export includes the customer's direct data and linked patients, prescriptions, sales summaries, appointments and reminders. Every export creates an audit event. Store the resulting file encrypted, deliver it through an approved channel and delete the temporary copy after delivery.

## Anonymization workflow

Anonymization is intentionally a separate privileged operation:

```http
POST /api/v1/crm/privacy/clientes/{cliente_id}/anonymize
Permission: privacidad.solicitudes.anonimizar

{"confirmation":"ANONYMIZE","reason":"Approved privacy request reference PR-1234"}
```

The operation removes direct customer and patient identifiers, soft-deletes those records, clears free-text prescription/appointment content, cancels pending reminders and retains referential records needed for accounting or legal obligations. It cannot be reversed from the application. Take an approved backup and obtain legal/operational authorization before execution.

## Retention baseline requiring business approval

| Dataset | Proposed retention | Disposal |
| --- | --- | --- |
| Authentication sessions | Until expiration plus 30 days | Scheduled hard delete |
| Audit events | 2 years | Tenant-scoped purge after legal hold check |
| Clinical prescriptions | 5 years after last service | Anonymize/direct-identifier separation |
| Fiscal invoices and accounting | Jurisdictional statutory period | Immutable archive, then approved purge |
| Operational reminders | 90 days after terminal state | Hard delete message content |
| Backups | 35 daily + 12 monthly copies | Cryptographic deletion and inventory update |

Do not activate automated deletion until legal counsel and the data owner approve these periods. Legal holds override all scheduled disposal.

## Request handling checklist

1. Verify requester identity using an approved out-of-band method.
2. Record request ID, scope, jurisdiction, deadline and legal basis.
3. Search all tenant systems, exports, object storage and provider platforms.
4. Obtain privacy-role approval before export or anonymization.
5. Run export first and have a second operator review its scope.
6. Execute anonymization only with `ANONYMIZE` confirmation and a non-empty reason.
7. Verify audit records and communicate completion without exposing data in tickets.
8. Record exceptions for legal hold, fraud, fiscal or healthcare retention.

## Logging and incident rules

- Structured application logs redact bearer tokens, token/password/API-key assignments and email addresses.
- Never log request bodies for authentication, clinical, fiscal or privacy endpoints.
- Treat an unauthorized export, cross-tenant lookup or backup disclosure as a security incident.
- Rotate affected credentials and preserve immutable audit evidence during investigation.
