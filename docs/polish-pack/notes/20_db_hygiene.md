# Database hygiene drill log — Mission 20

**Date:** 2026-06-11 · **Head revision:** `r1a2b3c34d65` (17 migrations, linear chain)

## 1. Fresh-DB replay

| Step | Command | Result |
|------|---------|--------|
| CI (authoritative) | `alembic upgrade head && python scripts/check_migration_drift.py` | **Green** — runs in `.github/workflows/ci.yml` backend job before pytest |
| Local drill (2026-06-11) | Postgres `localhost:5435`, `pip install -e ./apps/api[dev]`, `alembic upgrade head && python scripts/check_migration_drift.py` | **Green** — after registering `ProWaitlistEntry` in drift script; downgrade `-1` / re-upgrade on `r1a2b3c34d65` reversible |
| Local pytest (focused) | `RUN_DB_TESTS=1` — drift, hot paths, purge, retention, tenant isolation, analytics | **26 passed** |

**Chain:** single linear path `42c29075a206` → … → `q9r0s1t32u63` → `r1a2b3c34d65`. No branch labels.

## 2. Downgrade audit (last 10 revisions)

| Revision | Summary | Downgrade | Notes |
|----------|---------|-----------|-------|
| `r1a2b3c34d65` | Queue composite indexes | **Reversible** | `drop_index` ×2 |
| `q9r0s1t32u63` | `pro_waitlist_entries` table | **Reversible** | `drop_table` |
| `p8q9r0s31t62` | Analytics/batch/llm indexes | **Reversible** | `drop_index` ×3 |
| `o7c5p6q28b60` | `product_config` table | **Reversible** | |
| `n6b3o4r27a59` | RBAC `users.role` | **Reversible** | Enum column |
| `m5a2n3l25y48` | Analytics rollup tables | **Reversible** | `drop_table` |
| `l4h1i2d23e47` | Discovery `saved_searches` | **Reversible** | |
| `k3g9h0c12d36` | `user_preferences` | **Reversible** | |
| `j2f8g9b01c25` | Google OAuth identities | **Reversible** | |
| `i1e7f8a90b14` | Native auth tables | **Reversible** | Drops auth tokens/identities |

**Irreversible (earlier chain — do not downgrade in prod):**

| Revision | Reason |
|----------|--------|
| `h0c5d6e67f03` | Tenancy backfill: seeds default tenant/user and adds `tenant_id` to existing rows — downgrade drops columns/tables and **loses tenant assignment data** |

## 3. Index / EXPLAIN audit

### Hot paths reviewed

| Path | Query pattern | Index (before → after) | Evidence |
|------|---------------|------------------------|----------|
| Queue / library | `job_targets` WHERE `tenant_id` + `status` | separate `tenant_id`, `status` → **+** `ix_job_targets_tenant_status` | `test_db_hot_paths.py` |
| Admin runs | `application_runs` WHERE `tenant_id` + `status` | separate columns → **+** `ix_application_runs_tenant_status` | `test_db_hot_paths.py` |
| Run console SSE | `run_events` WHERE `run_id` + `seq` | `ix_run_events_run_id_seq` (mission 11) | EXPLAIN test |
| Analytics retention | `analytics_events` WHERE `tenant_id` + `ts` | `ix_analytics_events_tenant_ts` (mission 32) | `pg_indexes` test |
| Batch preview | `batch_items` WHERE `batch_id` + `status` | `ix_batch_items_batch_status` (mission 32) | `pg_indexes` test |

**Planner note:** On small tables Postgres may prefer `ix_job_targets_status` over the composite index; `test_job_targets_tenant_status_uses_index_scan` asserts any `job_targets` index scan (not seq scan). Composite presence is enforced by `test_hot_path_index_exists`.

**Production deploy:** New indexes are plain `CREATE INDEX` (not `CONCURRENTLY`). Safe while row counts are low on Railway; re-evaluate `CONCURRENTLY` if `job_targets` > ~100k rows.

## 4. Retention drills

| Job | Code | Test | Deletes |
|-----|------|------|---------|
| Analytics events | `purge_stale_analytics_events` | `test_purge_stale_analytics_events` | DB rows older than `ANALYTICS_RETENTION_DAYS` |
| Run artifacts | `purge_stale_run_artifacts` | `test_purge_stale_terminal_runs_respects_retention` | Terminal runs + MinIO prefix via `cleanup_runs` |
| Per-run purge API | `purge_run` | `test_purge_run_and_export_all`, **`test_purge_run_removes_object_storage_prefix`** | DB row + `ObjectStorage.remove_prefix` |

## 5. Tenant / FK integrity

Tenant-scoped tables (all have `tenant_id` FK → `tenants.id` CASCADE): `job_targets`, `application_runs`, `application_batches`, `resume_assets`, `user_profiles`, `saved_searches`, `company_boards`, `job_lists`, `audit_log_entries`, `analytics_events`, `users`, etc. Cross-tenant access covered by `test_tenant_isolation.py`.

## 6. Connection pool (Railway)

| Setting | Default | Rationale |
|---------|---------|-----------|
| `DATABASE_POOL_SIZE` | `5` | API engine `pool_size` |
| `DATABASE_MAX_OVERFLOW` | `5` | Burst connections |
| **Max API connections** | **10** | Leaves headroom for worker + migrations on Hobby (~20 conn limit) |

Configured in `jober_api.config.Settings` → `db/session.py`. Worker uses short-lived engines in batch runner (separate from API pool).

## 7. Backup / restore drill

| Environment | Status |
|-------------|--------|
| **CI / Linux** | `make backup` → `infra/backups/backup.sh` (pg_dump + `mc mirror`) |
| **Windows** | Requires **Git Bash** or **WSL** — `backup.sh`/`restore.sh` use bash, `docker compose exec`, and `mc`. PowerShell-native `docker compose` works; `bash make backup` from Git Bash at repo root. |
| **Full destroy-restore loop** | Not run on this host (port conflicts with other compose stacks). Procedure documented in `docs/runbooks/restore-backup.md`. |

**Recommended local drill (Git Bash):**

```bash
docker compose --env-file .env -f infra/compose.yaml --profile infra up -d postgres minio createbuckets
make backup
docker compose -f infra/compose.yaml --profile infra down -v   # destructive
docker compose --env-file .env -f infra/compose.yaml --profile infra up -d postgres minio createbuckets
make restore SOURCE=infra/backups/latest
make migrate-check
```

## 8. Migration added this mission

`r1a2b3c34d65_pack20_queue_indexes.py` — composite `(tenant_id, status)` on `job_targets` and `application_runs`.
