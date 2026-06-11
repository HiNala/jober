# API error contract

**Status:** Mission 18 (2026-06-10) · **Consumers:** web `mapApiErrors`, admin tools, future SDK.

## Envelope

All JSON error responses use FastAPI’s `detail` field plus cross-cutting metadata:

```json
{
  "detail": "Job target not found",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "code": null
}
```

Structured `detail` (conflicts, budget, dependency outages):

```json
{
  "detail": {
    "message": "Human checkpoint required",
    "code": "human_checkpoint_required",
    "gate": "resume_missing",
    "run_id": "…"
  },
  "correlation_id": "…",
  "code": "human_checkpoint_required"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `detail` | Yes | `string`, Pydantic `array` (422), or `object` with `message` |
| `correlation_id` | Yes | Echoed in `X-Correlation-Id` response header; pass through on retries |
| `code` | When branching | Duplicated from `detail.code` when present |

**Never** include stack traces, file paths, or driver messages in `detail`.

## Status code decision table

| Situation | Status | `code` (if any) |
|-----------|--------|-----------------|
| Cross-tenant or missing owned resource | **404** | — |
| Authenticated but forbidden (RBAC, CSRF, submit policy) | **403** | — |
| Conflict (duplicate email, job in list, human gate) | **409** | domain-specific |
| Validation / business rule | **422** | optional |
| LLM monthly budget exceeded | **402** | `llm_budget_exceeded` |
| Rate limit (resend, login) | **429** | — |
| MinIO / Redis / broker unreachable at request time | **503** | `dependency_unavailable` |
| Unexpected server fault | **500** | opaque `"Internal server error"` |

### Tenant isolation

Missing resources in another tenant’s scope return **404**, not **403**, so existence is not leaked. Enforced in `test_tenant_isolation.py` via `tenant_guard`.

## Code registry

| Code | Status | When |
|------|--------|------|
| `dependency_unavailable` | 503 | Storage, cache, or enqueue dependency down |
| `llm_budget_exceeded` | 402 | Monthly LLM cap hit |
| `human_checkpoint_required` | 409 | Form fill blocked for human gate |
| `verification_blocked` | 409 | Readiness verify failed with open run |
| `checkpoint_already_resolved` | 422 | Double-resolve on run console |

Add new codes only when the web or a client must branch; otherwise a string `detail` is enough.

## Implementation

- `jober_api/errors.py` — envelope helpers, correlation middleware, global handlers
- `register_exception_handlers(app)` in `main.py`
- Routers raise `HTTPException` or helpers (`budget_exceeded_http`, `dependency_unavailable_http`, `error_detail`)
- `/readyz` reports Postgres, Redis, MinIO; runtime 503s align with readiness semantics

## Web mapping

`apps/web/src/lib/forms/map-api-errors.ts`:

- `detail` string → form error
- `detail` array → field errors (422)
- `detail.message` → form error
- Status **402** / **503** → friendly copy (503 prefers API message when present)

## CORS

`CORSMiddleware` wraps all responses, including 4xx/5xx, so browsers can read error bodies from allowed origins.
