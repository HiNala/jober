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

## Object storage

### Railway bucket

- Re-create bucket credentials if rotated.
- Restore objects from offline `mc mirror` backup if maintained.

### MinIO on volume

- Snapshot volume before major changes.
- Restore volume snapshot in Railway; redeploy MinIO service.

## Verify

- `/readyz` minio check ok
- Presigned URL upload/download smoke test
- Admin cost/reconciliation unchanged for test window
