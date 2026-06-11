# Mission 18 — API error inventory

**Validated:** 2026-06-10 · Router audit + handler rollout.

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Global exception handler | None | Opaque 500 + structured log |
| Correlation ID | None | `X-Correlation-Id` on all responses |
| Envelope documented | No | `docs/architecture/errors.md` |
| Storage outage → 503 | Raw 500 / leak | `resumes`, `documents` generate |
| Budget 402 `code` | String only | `llm_budget_exceeded` |
| Leak test | None | `test_error_contract.py` |

## Router inventory

| Router | Primary shapes | Codes added | Leaks fixed |
|--------|----------------|-------------|-------------|
| `auth.py` | string | — | global 500 handler |
| `admin*.py` | string | — | — |
| `analytics*.py` | via deps | — | — |
| `batches.py` | string / 402 dict | `llm_budget_exceeded` | — |
| `billing.py` | service | — | — |
| `documents.py` | string / dict | `llm_budget_exceeded`, 503 | storage wrap |
| `discovery.py` | string (domain) | — | — |
| `exports.py` | service | — | — |
| `form_discovery.py` | string | — | — |
| `form_fill.py` | dict 409 | `human_checkpoint_required` | — |
| `imports.py` | string | — | — |
| `job_extraction.py` | dict 409 | — | — |
| `job_lists.py` | string 409 | — | — |
| `job_targets.py` | string | — | — |
| `library.py` | service | — | — |
| `llm.py` | service | — | — |
| `privacy.py` | string | — | — |
| `profile.py` | string | — | — |
| `recovery.py` | string | — | — |
| `resumes.py` | string / 503 dict | `dependency_unavailable` | storage wrap |
| `run_console.py` | string / dict 422 | `checkpoint_already_resolved` | — |
| `settings.py` | string | — | — |
| `verification.py` | string / dict 409 | `verification_blocked` | — |
| `waitlist.py` | string | — | — |
| `webhooks.py` | string | — | — |

**Convention:** String `detail` remains valid for simple errors. Dict `detail` always includes `message`; optional `code` when clients branch.

## Tenant isolation

`test_tenant_isolation.py` — cross-tenant **404** unchanged. RBAC **403** unchanged.

## Downstream failures

| Dependency | `/readyz` | Runtime endpoint |
|------------|-----------|------------------|
| Postgres | check | existing DB errors |
| Redis | check | enqueue paths — future 503 batch |
| MinIO | check | resume upload, cover letter generate → **503** |

## Deferrals

| Item | Owner |
|------|-------|
| Normalize every `detail=str(exc)` router catch | Incremental — domain messages are user-safe; raw `Exception` → 500 handler |
| Celery enqueue explicit 503 | Mission 23 |
| Promote checkpoint double-resolve to 409 | Web expects 422 today — code added, status unchanged |
| Parametrized per-router envelope sweep | Mission 25 |

## Gates

- `test_error_contract.py` — envelope, leak, 503 resume, CORS on 404
- `test_documents_api.py` — 402 code assertion updated
- Policy suite unchanged semantics
