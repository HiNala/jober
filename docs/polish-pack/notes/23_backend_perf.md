# Mission 23 — API / worker performance baseline

**Date:** 2026-06-12  
**Host:** Windows dev + GitHub Actions `backend` job (CI authoritative for full pytest)

## Dataset shape

Seeded via `jober_api.services.dev.perf_volume.seed_perf_volume` / `python scripts/seed_perf_volume.py`:

| Entity | Count | Notes |
|--------|------:|-------|
| Job targets | 150 | Mixed status/priority A–C, ranked |
| Application runs | 50 | Mix of active + terminal statuses |
| Analytics events | 10,000 | Single UTC day, ~120 sessions / ~400 anon ids |

## Fixes shipped

| Area | Before | After | Evidence |
|------|--------|-------|----------|
| Dashboard `queue_depth_priority_a` | Loaded up to 2000 priority-A rows, counted in Python | `JobTargetRepository.count_filtered` SQL `COUNT` | `test_dashboard_queue_depth_uses_sql_count` |
| Analytics WAU/MAU in rollup | Fetched all rows into Python for distinct actors | `COUNT(DISTINCT actor_key)` SQL | `test_analytics_rollup_scales_linearly` |
| Library / job-lists / documents / resumes lists | Implicit or hardcoded limits | `limit`/`offset` query params (`max 200`) | router + service changes |
| Load regression guards | Health + 2 hot reads | Volume seed + p95 latencies, rollup timing, SSE fan-out, domain lock | `test_load_smoke.py` |

## Latency table (local pytest, seeded volume)

Thresholds encoded in `test_load_smoke.py` (generous for CI variance):

| Endpoint | p95 target | Guard |
|----------|------------|-------|
| `GET /api/job-targets?priority=A&limit=100` | &lt; 300 ms | `test_hot_paths_at_perf_volume` |
| `GET /api/dashboard/summary` | &lt; 500 ms | same |
| `GET /api/application-runs/{id}/console` | &lt; 300 ms | same |
| `POST /api/batches/preview` | &lt; 600 ms | same |
| `rollup_analytics_day` 2k events | &lt; 2 s | `test_analytics_rollup_scales_linearly` |
| `rollup_analytics_day` 10k events | &lt; 8 s, &lt; 8× 2k time | same |

## Rollup scaling

Rollup loads one day's events once (`_fetch_events`), computes funnel/pages in memory, and uses SQL `COUNT(DISTINCT …)` for WAU/MAU windows — **O(n)** in day event count, not quadratic.

## Worker / SSE drills

| Drill | Result |
|-------|--------|
| Domain lock serialization (same host) | `test_domain_lock_serializes_same_host` + existing `test_batch_ops` |
| SSE fan-out N=10 consumers, 30 events | Zero loss — `test_sse_fanout_no_event_loss` |
| 10-item dry-run batch vs fixture | Covered by existing `test_create_and_enqueue_batch` (`test_batch_ops.py`) |

## Pagination inventory

| Endpoint | `limit` / `offset` |
|----------|-------------------|
| `GET /job-targets` | yes (max 2000) |
| `GET /library/*` | yes (max 200) |
| `GET /job-lists` | yes (max 200) |
| `GET /documents` | yes (max 200) |
| `GET /resumes` | yes (max 200) |
| Admin lists | yes (existing) |
| `GET /console/recent-events` | `limit` capped at 100 |

Web clients read `items` only — added `limit`/`offset` metadata is backward compatible.

## Validation

```bash
cd apps/api && ruff check src tests && mypy src && pytest -q
cd apps/worker && ruff check src tests && mypy src && pytest -q
```

Load-marked tests run in default API pytest on CI (`pytestmark.load`).

## Follow-ups

| Item | Owner |
|------|-------|
| Production latency sampling (Railway) | Mission 24 / operator |
| Redis response caching for dashboard | Out of scope (Mission 23) |
| `job-targets` `total` field (currently page size, not DB count) | Future API hygiene |
