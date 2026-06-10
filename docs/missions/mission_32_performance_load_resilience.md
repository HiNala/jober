# Mission 32 — Performance, Load & Resilience Testing

## Task list
- [x] **Frontend perf budgets:** bundle-size CI gate (`check:bundles`); analytics route code-split; lazy filmstrip thumbs
- [x] **API/DB load:** SQL `count_by_status` aggregate; batched presign map for console snapshot; perf indexes migration
- [x] **Streaming under load:** SSE `retry`, heartbeat, 50-event/poll cap; auto-reconnect in `useRunStream`
- [x] **Worker throughput:** Celery `--concurrency` default 2 (headless-safe); documented in worker entrypoint
- [x] **Resilience / chaos:** `/readyz` degrades when Redis down; `/healthz` stays live; load + SSE burst tests
- [x] **Cost under load:** concurrent budget hard-stop test (`test_budget_hard_stop_under_concurrent_checks`)
- [x] **Memory/leak checks:** weekly `run_artifact_retention_purge` Celery task (tenant `retention_days` + default 90d)

## Acceptance criteria
- [x] Load smoke passes hot paths concurrently (`test_load_smoke.py`, `pytest -m load`)
- [x] No N+1 on batch status counts; console presign batched
- [x] Indexes: `analytics_events(tenant_id,ts)`, `batch_items(batch_id,status)`, `llm_calls(created_at)`
- [x] SSE backpressure + reconnect fixtures green
- [x] Budget governor holds under concurrent checks
- [x] CI: bundle budget after `pnpm build`; load tests in default API pytest

## CI jobs
| Job | M32 additions |
|-----|----------------|
| `backend` | load smoke, resilience, perf batch/SSE tests, migration |
| `web` | `pnpm check:bundles` after build |

## Perf budgets (initial)
| Surface | Budget |
|---------|--------|
| Client JS chunks (total) | ≤ 2800 KB (`JOBER_MAX_CLIENT_JS_KB`) |
| Hot API reads (30 concurrent) | p99 < 3s (CI smoke) |
| SSE burst | ≤ 50 events per poll |

## Mission 99 (post–M32)

- [x] Model `Index()` definitions synced with `p8q9r0s31t62` migration (drift check was failing CI)
- [x] `test_artifact_retention.py` — terminal run purge respects `run_artifact_retention_days`
- [x] `.env.example` documents `CELERY_WORKER_CONCURRENCY` and `RUN_ARTIFACT_RETENTION_DAYS`

**M99 CI:** [run 27264475631](https://github.com/HiNala/jober/actions/runs/27264475631) (green on `10fbfc8`).

## Iteration clause
Perf indexes must live in both Alembic **and** SQLAlchemy `__table_args__` or `check_migration_drift.py` fails.
