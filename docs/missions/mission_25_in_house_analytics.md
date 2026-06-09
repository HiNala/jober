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
`ANALYTICS_RETENTION_DAYS` (default 365) — purge job deferred to Mission 26 dashboards.

## Mission 99
Run iteration loop after CI green.
