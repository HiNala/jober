# Mission 25 — In-House Analytics Foundation

## Task list
- [x] **Event model:** `AnalyticsEvent` + daily rollup tables; indexed by `ts`
- [x] **Collector:** `POST /api/events` (batched, beacon-friendly) + server-side `emit_server_event`
- [x] **Client SDK:** `apps/web/src/lib/analytics/sdk.ts` — consent + DNT, anon rotation, batch/beacon
- [x] **Sessionization:** server-side page metrics + time-on-page from event stream
- [x] **Rollup jobs:** Celery `analytics_daily_rollup` → funnel, page, active-user, LLM cost tables
- [x] **Privacy:** no raw IP (coarse geo only), PII blocked in props, consent/DNT opt-out, retention config

## Acceptance criteria
- [x] Page view + custom event land in `AnalyticsEvent` via first-party collector
- [x] Sessions + time-on-page from seeded stream (`test_sessionization_time_on_page_and_bounce`)
- [x] Rollup produces funnel + page + active-user summaries (`test_rollup_daily_summaries`)
- [x] No raw IP/PII; DNT suppresses tracking (`test_dnt_suppresses_tracking`, `test_pii_props_rejected`)
- [x] Gates green

## Event integrity (iteration clause)
- `event_registry.py` — allowlisted event names + per-event prop keys; client vs server sources

## API
| Route | Purpose |
|-------|---------|
| `POST /api/events` | Public collector (requires consent cookie; honors DNT) |

## Retention
`ANALYTICS_RETENTION_DAYS` (default 365). Celery `analytics_retention_purge` runs Sundays 03:30 UTC.

## Mission 99 (post–Mission 25)
- [x] Finish leftovers — retention purge job (was config-only)
- [x] Gates green — ruff, mypy, pytest, web lint/typecheck/build, CI
- [x] Full suite — session_id min-length, consent opt-out, purge tests added
- [x] Policy invariants unchanged (analytics does not touch autofill/submit paths)
- [x] Secrets — detect-secrets clean in CI
- [x] File hygiene — all modules under 2000 lines; per-task commits
- [x] Design Council 20/20 on consent banner + SDK surfaces
- [x] Self-improvement — `server_session_id` length guard + weekly retention purge
- [x] Docs — README, design-review, mission doc updated
- [x] Fixture-for-bug — `test_server_session_id_fallback_meets_schema_min_length`

## CI
Green on [27184269887](https://github.com/HiNala/jober/actions/runs/27184269887) (`48f9ad4`).
