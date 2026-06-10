# Mission 23: API and Worker Performance Validation

## Purpose
Build-mission 32 did a perf/load/resilience pass; this mission re-validates it post-changes (new indexes from Mission 20, error handling from Mission 18) and closes the loop on the backend paths users feel: queue/list endpoints, dashboard summary, SSE fan-out, rollup duration, and worker throughput under batch pacing.

## Context From Audits
Application audit §12 ("to verify: SSE event volume on long runs; Celery rollup duration as AnalyticsEvent grows") and §6. Assets: `tests/test_load_smoke.py`, batch pacing with per-domain locks, worker pool capacity surfaced on `/api/dashboard/summary`, admin system view (`/api/admin/system`).

## Scope
- **Baseline latencies** (local full stack, seeded with realistic volume — generate ~150 job targets, ~50 runs, ~10k analytics events via a seed extension or script): p50/p95 for `GET /job-targets` (filtered), `GET /api/dashboard/summary`, `GET /api/application-runs/{id}/console`, `GET /api/batches/preview`, admin analytics endpoints.
- Fix verified hot spots: N+1 queries (SQLAlchemy async lazy-load traps), missing eager loads, unnecessary per-request MinIO/Redis round trips, oversized payloads (pagination presence and limits on list endpoints — verify every list endpoint paginates).
- **Rollup duration:** time `analytics_daily_rollup` against the seeded event volume; ensure it's batched/indexed, not quadratic.
- **Worker throughput:** a 10-item dry-run batch against the fixture server completes within pacing expectations; per-domain lock contention behaves (two batches, same host → serialized).
- **SSE fan-out:** N concurrent consumers on one active run (script with `curl`/Python) → no event loss, API stays responsive.
- Re-run and, if needed, extend `test_load_smoke.py` to encode the fixed baselines as regression guards (generous thresholds — CI variance).

## Out of Scope
- Horizontal scaling architecture, caching layers (Redis response caches), DB engine tuning beyond pool settings (recommend only).
- Web rendering performance (Mission 22).
- Premature optimization of endpoints with no measured problem.

## Starting Checklist
1. Read `tests/test_load_smoke.py` — existing methodology and thresholds.
2. Read build-mission 32's doc (`docs/missions/mission_32_performance_load_resilience.md`) for what was already measured and the tools used.
3. Check list endpoints for pagination: `grep -rn "limit\|offset\|cursor" apps/api/src/jober_api/routers/job_targets.py library.py batches.py`.
4. Plan the realistic-volume seed (extend `scripts/seed.py` behind a `--volume` flag or a separate script).
5. Confirm Mission 20's indexes landed (they change every measurement here).

## Tasks
1. Build the volume seed; record the dataset shape in the notes file.
2. Measure the baseline latency table; profile the worst offenders (SQLAlchemy echo or `EXPLAIN ANALYZE` from Mission 20 tooling).
3. Fix verified issues (eager loading, query consolidation, pagination gaps); re-measure after each fix.
4. Rollup timing + fix if super-linear.
5. Worker batch + lock-contention drill against the fixture server.
6. SSE fan-out drill.
7. Encode guards into `test_load_smoke.py`; document final table.

## Self-Improvement Loop
1. Inspect the worst remaining p95.
2. Identify the dominant cause by profiling (never guess).
3. Make the smallest coherent fix.
4. Validate by re-measuring + full API suite.
5. Update the table.
6. Repeat until targets hold or causes are documented as out-of-scope architecture.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q` (incl. updated `test_load_smoke.py`)
- `cd apps/worker && ruff check src tests && mypy src && pytest -q`
- `make test-fixtures`
- Before/after latency tables in the notes file.

## Acceptance Criteria
1. Latency table recorded; every fixed endpoint shows a measured improvement; p95 targets: list endpoints < 300ms, dashboard summary < 500ms at the seeded volume locally (adjust with rationale if hardware-bound — record the machine).
2. Every list endpoint paginates with enforced limits.
3. Rollup is linear-ish in event count with evidence.
4. Worker pacing/lock drills pass; SSE fan-out loses zero events at N=10 consumers.
5. Regression guards in `test_load_smoke.py`; all gates green.

## Documentation Requirements
- `docs/polish-pack/notes/23_backend_perf.md` (dataset, tables, profiles, fixes).
- Update `docs/runbooks/queue-backed-up.md` if throughput characteristics changed.

## Git Workflow
`git status` first; one commit per measured fix with the delta in the body; seed/measurement tooling committed under `apps/api/scripts/`; push after gates.

## Production Guidance
Deployable after gates pass. Pagination additions can change client behavior — confirm the web app handles paginated responses on every touched endpoint before deploying (deploy API + web together if response shapes gained pagination metadata). Smoke after.
