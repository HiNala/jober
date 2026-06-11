# Restore from backup

## Postgres (Railway)

### Symptoms

- Data corruption, accidental delete, need to test restore procedure.

### Diagnosis

- Confirm scope: full DB vs single tenant (tenant restore needs export/import, not full restore).

### Restore drill (staging — run before production launch)

| Step | Action | Result (record date) |
|------|--------|----------------------|
| 1 | Enable automated backups + PITR on Railway Postgres | |
| 2 | Note current `DATABASE_URL` and deployment SHA | |
| 3 | Create **ephemeral** environment clone or new Postgres from snapshot | |
| 4 | Point **staging API** `DATABASE_URL` at restored instance | |
| 5 | `bash scripts/railway-smoke.sh` | |
| 6 | Run `make migrate-check` against restored DB | |
| 7 | Tear down ephemeral instance | |

**Last drill (staging smoke, 2026-06-10):** Verified live `/readyz` (postgres, redis, minio) on `api-staging-a8ca.up.railway.app` after M33 deploy. Full PITR clone-and-repoint drill pending operator window — run steps 1–7 above before production cutover; record second row here when complete.

### Production restore

1. Railway Postgres → Backups → restore to new instance or point-in-time.
2. Update `DATABASE_URL` on **api** and **worker** services.
3. Redeploy api (migrations are idempotent).
4. Smoke + admin overview check.

## Local backup / restore (self-host)

Scripts: `infra/backups/backup.sh`, `infra/backups/restore.sh` (invoked via `make backup` / `make restore`).

### Prerequisites

- Docker Compose v2 with `infra` profile (`postgres`, `minio`, `createbuckets`).
- `.env` at repo root (optional) for non-default host ports (`POSTGRES_HOST_PORT`, `MINIO_API_HOST_PORT`).

### Windows

- **Git Bash** or **WSL** is required for `make backup` / `make restore` (bash + `mc` in the `createbuckets` sidecar).
- From Git Bash at repo root: `make backup` then `make restore SOURCE=infra/backups/latest`.
- PowerShell alone cannot run the Makefile targets unless you call `bash infra/backups/backup.sh` explicitly.
- Volume wipe (`docker compose down -v`) is destructive — only use on local dev data.

### Verify after restore

```bash
make migrate-check
curl -s http://localhost:8000/healthz
curl -s http://localhost:8000/readyz
```

Record timing: backup ~10–30s (empty DB), restore ~15–45s (depends on dump size). See `docs/polish-pack/notes/20_db_hygiene.md` for Mission 20 drill log.

## Object storage

### Railway bucket

- Re-create bucket credentials if rotated.
- Restore objects from offline `mc mirror` backup if maintained.

### MinIO on volume

- Snapshot volume before major changes.
- Restore volume snapshot in Railway; redeploy MinIO service.
- Local restore: `restore.sh` mirrors `minio/` snapshot into `jober-artifacts` via `mc mirror`.

## Verify

- `/readyz` minio check ok
- Presigned URL upload/download smoke test
- Admin cost/reconciliation unchanged for test window
