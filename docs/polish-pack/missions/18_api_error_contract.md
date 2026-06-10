# Mission 18: API Error Contract Consistency and Reliability

## Purpose
Twenty-eight routers built across 35 missions almost certainly drifted in error behavior: mixed error body shapes, inconsistent status-code choices, raw exception leakage, and uneven handling of downstream failures (MinIO, Redis, LLM, Playwright worker). This mission unifies the error contract so the web app (Mission 12's mapper) and API consumers get predictable failures.

## Context From Audits
Application audit §13 ("API error response shape consistency across 28 routers likely drifted") and §19. Existing assets: FastAPI/Pydantic 422 defaults, the 402 LLM-budget convention, write-time redaction (`LOG_MODE=redacted`) which must keep error bodies leak-free, `/healthz` vs `/readyz` split.

## Scope
- Define the canonical error envelope (document what the majority already does; prefer FastAPI's `{"detail": ...}` family extended with a stable `code` field where the web needs to branch) in `docs/architecture/errors.md`.
- Audit every router in `apps/api/src/jober_api/routers/` for: error shape, correct status codes (404 vs 403 on cross-tenant access — must match `test_tenant_isolation.py` expectations; 409 for conflicts like double-resolve; 402 budget; 429 rate limits), and exception leakage (raw 500s with stack details).
- Global exception handler: unexpected errors → opaque 500 envelope + structured log with correlation id; never internals in the body.
- Downstream failure mapping: MinIO down, Redis down, worker enqueue failure each map to a deliberate status + envelope (503 with retry hint where honest); `/readyz` reflects them.
- Verify CORS and error interaction (`test_config_cors.py`) — error responses still carry CORS headers so the web can read them.

## Out of Scope
- Changing success-path schemas (zero contract breakage for working clients).
- New middleware frameworks; keep to FastAPI idioms already in use.
- Web-side rendering (Mission 12 already built the mapper — update only the mapper's `code` awareness if the envelope gains one).

## Starting Checklist
1. `grep -rn "HTTPException" apps/api/src/jober_api/routers | wc -l` then sample 10 routers across domains for shape variety.
2. Read `apps/api/src/jober_api/main.py` (or app factory) for existing exception handlers/middleware.
3. Read `tests/test_tenant_isolation.py` for the 404-vs-403 convention already enforced.
4. Force downstream failures locally: stop minio/redis containers, hit affected endpoints, record actual behavior.
5. Check how the worker enqueue path fails when Celery broker is unreachable.

## Tasks
1. Write the error inventory (`docs/polish-pack/notes/18_error_inventory.md`): router × {shapes used, codes used, leaks found}.
2. Author `docs/architecture/errors.md` (envelope, code registry, status-code decision table).
3. Implement the global handler + correlation id (reuse existing structured-logging setup from build-mission 34 ops work).
4. Normalize outlier routers to the envelope; add `code` only where the web branches on it.
5. Downstream-failure mapping + `/readyz` truthfulness check.
6. Tests: envelope contract test applied across routers (parametrized), downstream-failure tests with mocked clients, leak test (no `Traceback`/path strings in any error body).
7. Update Mission 12's web mapper if the envelope changed.

## Self-Improvement Loop
1. Inspect the next router's failure paths (force each error class).
2. Identify the highest-impact deviation or leak.
3. Make the smallest coherent normalization.
4. Validate (router tests + full suite — normalization breaks tests that asserted old shapes; fix them deliberately).
5. Update the inventory.
6. Repeat until the inventory is uniform.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q`
- `make test-policy` (policy errors must keep their exact semantics)
- `cd apps/web && pnpm typecheck && pnpm test && pnpm build` (mapper compatibility)
- `pnpm test:e2e`
- Manual: stop minio → hit a resume upload → designed 503; restart → recovery without API restart.

## Acceptance Criteria
1. One documented envelope; inventory shows every router conforming.
2. No error body leaks internals (test-enforced).
3. Cross-tenant access behavior matches the documented convention everywhere.
4. Downstream outages produce deliberate statuses and `/readyz` truth; recovery needs no restart.
5. All gates green, including unchanged policy suite.

## Documentation Requirements
- `docs/architecture/errors.md` (new, referenced from README).
- `docs/polish-pack/notes/18_error_inventory.md`.

## Git Workflow
`git status` first; commits: doc+handler → per-domain normalization batches; reviewed diffs; bodies with what/why/validation/follow-ups; push after gates.

## Production Guidance
Deploy API + web together after gates pass (the web mapper and envelope move in lockstep). Watch error rates in the admin overview and Sentry (if enabled) for 24h; `bash scripts/railway-smoke.sh` post-deploy.
