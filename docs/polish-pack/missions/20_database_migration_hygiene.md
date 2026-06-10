# Mission 20: Database, Migration, and Data-Lifecycle Hygiene

## Purpose
The schema grew across ~20 migration-bearing missions (vault, extraction, observations, batches, tenants, analytics rollups, run events…). This mission verifies the database layer is production-trustworthy: migrations replay cleanly, models match reality, hot queries are indexed, retention jobs actually delete, and backup/restore provably works.

## Context From Audits
Application audit §6 (drift check exists: `make migrate-check`), §12 (rollup duration as `AnalyticsEvent` grows), §18 (backup/restore scripts exist but Windows-constrained). Assets: Alembic in `apps/api/alembic/`, `scripts/check_migration_drift.py`, `tests/test_migration_drift.py`, retention jobs (`analytics_retention_purge`, artifact retention per `test_artifact_retention.py`), `infra/backups/backup.sh`/`restore.sh`.

## Scope
- **Migration replay:** from empty DB, `alembic upgrade head` → drift check green; `alembic downgrade -1` + re-upgrade for recent migrations (or document irreversible ones explicitly).
- **Index audit:** EXPLAIN the hot paths — queue list/filter (`job_targets` by tenant+status), run events by run+seq, analytics rollup source scans, library queries, batch preview exclusions. Add missing indexes via a new migration; measure before/after.
- **Retention truth:** run `analytics_retention_purge` and artifact retention against seeded old data; verify rows/objects actually deleted and MinIO keys removed; confirm purge endpoints (`/api/privacy/*`) leave no orphans (DB rows without MinIO objects and vice versa).
- **Data integrity:** FK/constraint audit on tenant-scoped tables (every tenant-owned table has `tenant_id` + appropriate constraints — cross-check with `test_tenant_isolation.py` coverage list).
- **Backup/restore drill:** `make backup` → destroy local volumes → `make restore` → app works and a known record survives. Document Windows caveats precisely (Git Bash/WSL).
- Connection-pool settings sanity for Railway (pool size vs Railway Postgres limits).

## Out of Scope
- Schema redesign or table renames (creep + risk).
- New retention policies (verify configured ones work).
- Postgres version changes.

## Starting Checklist
1. `ls apps/api/alembic/versions | wc -l` and skim the chain for branching/merge points.
2. Read `scripts/check_migration_drift.py` and `tests/test_migration_drift.py`.
3. Read retention task code (`services/analytics/`, artifact retention service) and their Celery beat schedule.
4. Read `infra/backups/*.sh`.
5. Identify hot queries from routers + the admin runs/analytics services (several were formatting-touched in Mission 01: `services/admin/runs.py`, `services/analytics/rollups.py`).

## Tasks
1. Fresh-DB replay test (new throwaway database in the local Postgres container): upgrade, drift check, seed, smoke the API.
2. Downgrade audit for the last ~10 migrations; mark irreversible ones in a migration-notes file.
3. EXPLAIN audit → index migration(s) with before/after timings recorded.
4. Retention drill with backdated seed data; fix any non-deleting job; add a test if a gap is found.
5. Orphan audit: script or test that cross-checks `GeneratedDocument`/artifact rows vs MinIO keys on a purged tenant.
6. Backup/restore drill; update `docs/runbooks/restore-backup.md` with exact observed steps and timing.
7. Pool-size review against Railway plan limits; adjust env defaults if needed.

## Self-Improvement Loop
1. Inspect the next scope item with a real drill (never by code-reading alone).
2. Identify the highest-impact defect.
3. Make the smallest coherent fix (each schema change is its own migration).
4. Validate (drill re-run + `make migrate-check` + full API suite).
5. Document timings/evidence.
6. Repeat until all drills pass.

## Validation
- `make migrate-check`
- `cd apps/api && ruff check src tests && mypy src && pytest -q` (incl. `test_migration_drift.py`, `test_artifact_retention.py`, `test_tenant_isolation.py`)
- Fresh-DB replay log, retention drill log, backup/restore drill log — all captured in the notes file.

## Acceptance Criteria
1. Fresh-DB replay + drift check green; downgrade behavior documented.
2. Hot paths indexed with measured improvements (or measured as already-fine).
3. Retention jobs proven to delete (DB + MinIO); zero orphans after purge.
4. Backup → restore drill succeeded end-to-end with documentation matching reality.
5. All gates green.

## Documentation Requirements
- `docs/polish-pack/notes/20_db_hygiene.md` (drill logs, timings, index rationale).
- `docs/runbooks/restore-backup.md` corrections.

## Git Workflow
`git status` first; migrations in dedicated commits (`feat(db): index hot queue and run-event paths [pack-20]`); never edit applied migrations — always add new ones; reviewed diffs; push after gates.

## Production Guidance
Index migrations are deployable after gates pass (verify `CREATE INDEX` choices won't lock large tables — use `CONCURRENTLY` semantics if table sizes warrant; check Railway row counts first via admin/system). Take a production backup **before** deploying any migration from this mission (`docs/runbooks/deploy.md` flow), then smoke.
