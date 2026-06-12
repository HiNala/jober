# Mission 24 — Observability completion

**Date:** 2026-06-12  
**CI:** authoritative for full pytest

## Metric truth table (`GET /api/admin/overview`)

| Metric | Source | Spot-check |
|--------|--------|------------|
| `active_users.dau/wau/mau` | Latest `analytics_daily_active_users` rollup row | Celery `analytics_daily_rollup` |
| `signups.*` | `COUNT(users)` by `created_at` windows | `_signup_counts` |
| `runs.succeeded/failed/total` | `application_runs` grouped by `status` (30d) | `test_admin_overview_run_counts_match_raw_data` |
| `runs.needs_human` | `COUNT` where `status=needs_human` | SQL spot-check |
| `submits_30d` | `job_targets` where `status=applied` + `applied_date` | SQL spot-check |
| `cost.last_30d_usd` | `SUM(analytics_daily_cost.cost_usd)` | Matches rollup table |
| `cost.reconciled` | Rollup sum vs `SUM(llm_calls.cost_usd)` within $0.05 | `get_admin_cost` |
| `health.*` | `readiness_report` live probes | `/readyz` |
| `health.queue.*` | Redis `jober:batch:*` + `celery` LLEN | `queue_snapshot` |
| `ops.recovery_rate_30d` | `succeeded / (succeeded + failed)` | Derived from `_run_counts` |
| `ops.budget` | `monthly_llm_spend` vs `LLM_MONTHLY_BUDGET_USD` | `budget_status` |
| `ops.circuit_trips` | `failure_events` groups ≥ 5 | `global_circuit_trips` |
| `ops.celery_broker_depth` | Redis `LLEN celery` | `celery_broker_depth` |

## Alert drill matrix

| Class | `source` | Trigger | Runbook in payload |
|-------|----------|---------|-------------------|
| Infra down | `readyz` | Failed readiness probe | `docs/runbooks/infra-down.md` |
| Test | `admin_test` | `POST /api/admin/ops/test-alert` | `docs/runbooks/uptime-monitoring.md` |
| Queue paused | `admin_overview` | `globally_paused` | `docs/runbooks/queue-backed-up.md` |
| LLM budget | `admin_overview` | soft/hard budget | `docs/runbooks/cost-spike.md` |
| Circuit breaker | `admin_overview` | failure group ≥ 5 | `docs/runbooks/cost-spike.md` |
| Celery backlog stalled | `admin_overview` | depth ≥ 20, no active runs | `docs/runbooks/worker-stuck.md` |
| Cost rollup mismatch | `admin_overview` | rollup vs `LlmCall` drift | `docs/runbooks/cost-spike.md` |
| **Email send failed** | `email_send_failed` | Celery retries exhausted | `docs/runbooks/email-delivery.md` |
| **Email enqueue failed** | `email_enqueue_failed` | Redis/Celery enqueue error | `docs/runbooks/email-delivery.md` |
| Uptime sustained failure | `uptime_check` | 3× smoke failures | `docs/runbooks/uptime-monitoring.md` |

Production drill: set `OPS_ALERT_WEBHOOK_URL` on Railway → `POST /api/admin/ops/test-alert` (admin session) → confirm webhook receipt.

## Sentry decision

**Optional, env-gated.** `SENTRY_DSN` empty → `init_sentry()` no-op (default). When set, API loads `sentry-sdk[fastapi]` with `send_default_pii=False`, `traces_sample_rate=0.1` in production. Worker does not init Sentry (API boundary). Forced 500s include `correlation_id` in JSON + `X-Correlation-Id` for cross-reference with Railway logs.

## Log usability (three debugging questions)

| Question | Log signal | Fields |
|----------|------------|--------|
| Why did run X fail? | `batch_item_failed` | `run_id`, `tenant_id`, `batch_item_id`, `error` |
| Who hit 402 today? | `llm_budget_exceeded` | `tenant_id`, `correlation_id`, `path` |
| What did tenant Y purge? | `run_purged` | `run_id`, `tenant_id`, `removed_objects`, `correlation_id` |

Railway query (JSON logs): filter `message` contains the event name, then `correlation_id` or `tenant_id`.

## Correlation propagation

1. **Web → API:** client may send `X-Correlation-Id`; middleware echoes on response.
2. **API → Celery:** `enqueue_task()` adds `headers.correlation_id`; email also embeds in payload.
3. **Worker:** `task_prerun` logs `celery_task_start` with `correlation_id` when present.

## Uptime schedule

- Script: `scripts/uptime-check.sh` (5m cadence documented).
- **GitHub Actions:** `.github/workflows/uptime.yml` — runs when repo secrets `UPTIME_API_URL` (+ optional webhook) are set.
- See `docs/runbooks/uptime-monitoring.md`.

## Validation

```bash
cd apps/api && ruff check src tests && mypy src && pytest -q tests/test_observability.py tests/test_ops_alerting.py
cd apps/worker && ruff check src tests && mypy src && pytest -q
```

## Follow-ups

| Item | Owner |
|------|-------|
| Set `UPTIME_*` GitHub secrets for production URL | Operator |
| Enable `SENTRY_DSN` on Railway if desired | Operator |
| Grafana/Prometheus stack | Out of scope |
