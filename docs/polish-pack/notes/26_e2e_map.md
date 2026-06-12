# Mission 26 — E2E coverage map

**Date:** 2026-06-12  
**Playwright projects:** `marketing` (default CI web job) · `fullstack` (dedicated CI `e2e-fullstack` job)

## Tier summary

| Tier | Project | When it runs | Stack required |
|------|---------|--------------|----------------|
| Marketing / a11y / funnel | `marketing` | Every PR (`web` job) | Web only (`pnpm start` via Playwright) |
| Authenticated product journeys | `fullstack` | Every PR (`e2e-fullstack` job) | Postgres, Redis, MinIO, API, worker, fixture ATS, seeded tenant |

Full-stack specs call `requireFullStack()` and skip unless `E2E_FULL_STACK=1`.

## Flow × spec × assertions

| Flow | Spec file | Key assertions | Fixtures / setup |
|------|-----------|----------------|------------------|
| Import → queue → dry-run batch | `core-journey.fullstack.spec.ts` | `job-queue-row` count; `batch-preview-dialog` + `batch-enqueue`; library runs > 0 | `e2e/fixtures/jobs.xlsx`, `seed_e2e.py` resume |
| Run console checkpoint + reconnect | `core-journey.fullstack.spec.ts` | `checkpoint-card`, `checkpoint-skip`, `run-event-stream` survives reload | API helper `seedReviewCheckpointRun` |
| Login gate → failure report | `recovery.fullstack.spec.ts` | extract 409 `gate=login`; `failure-report-panel` in drawer | `gates/login` fixture HTML |
| Document studio cycle | `document-studio.fullstack.spec.ts` | `studio-generate`, `letter-preview`, `paragraph-lock-0`, `paragraph-regen-1`, PDF download | `LLM_PROVIDER=template` |
| Settings policy → batch default | `settings-effect.fullstack.spec.ts` | `#run-policy` persists; `preview-batch-tenant-default` opens dialog with `batch-policy=dry_run` checked | Tenant policy PATCH via UI |
| Auth signup → verify → login → logout | `auth-journey.fullstack.spec.ts` | register + `X-Jober-Verify-Token`; session cookies; logout → `/login` | **Optional:** `E2E_AUTH_NATIVE=1`, `AUTH_MODE=native`, no dev bypass |

## Selector conventions

Documented in `apps/web/AGENTS.md`: `{area}-{action}` `data-testid` values. Full-stack specs avoid marketing copy assertions where a testid exists.

## Local invocation

```bash
# Infra + services (see gates.md §8)
docker compose --profile infra up -d postgres redis minio createbuckets
cd apps/api && alembic upgrade head && python scripts/seed_e2e.py
python apps/web/e2e/scripts/build-e2e-workbook.py
make fixture-serve   # terminal 1
# API + worker in terminals 2–3 (or docker compose --profile full)

cd apps/web && pnpm build
E2E_FULL_STACK=1 LLM_PROVIDER=template DEV_AUTH_BYPASS=true pnpm test:e2e:fullstack
```

Re-run **3×** at mission boundaries for flake hunting.

## CI artifacts

On failure, `playwright-traces-marketing` and `playwright-traces-fullstack` upload `apps/web/test-results` (trace `retain-on-failure` in `playwright.config.ts`).

## Waivers

| Item | Rationale |
|------|-----------|
| Auth journey in default CI | Requires `AUTH_MODE=native` + no web dev bypass; skipped unless `E2E_AUTH_NATIVE=1` |
| Visual regression | Manual screenshot loop (`capture-screenshots.mjs`) |
| Real ATS / live LLM | Policy + fixture-only |
