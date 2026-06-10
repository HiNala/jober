# DB / Redis / storage down

## Symptoms

- `/readyz` returns 503
- Web worker-health pill red
- `OPS_ALERT_WEBHOOK_URL` fires `readyz` alert

## Diagnosis

```bash
curl -sS "$API_URL/readyz" | jq .
```

| Check | Typical cause |
|-------|----------------|
| `postgres` | Railway Postgres restart, SSL, wrong `DATABASE_URL` |
| `redis` | Redis password/URL mismatch, outage |
| `minio` | Bucket creds wrong, endpoint, or `MINIO_REGION` |

## Fix

### Postgres

- Verify `${{Postgres.DATABASE_URL}}` reference intact
- Railway dashboard → Postgres → logs
- SSL: app auto-rewrites `postgresql://` → `postgresql+asyncpg://`

### Redis

- Verify `${{Redis.REDIS_URL}}` on api, worker
- Celery broker and app Redis must match deployment

### Storage

- Railway bucket: refresh credentials via `railway bucket credentials`
- Set `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_REGION=auto`, `MINIO_SECURE=true`
- PowerShell: set keys as strings, not JSON objects (see [deploy.md](./deploy.md))

## Verify

```bash
bash scripts/railway-smoke.sh
```

All `checks.*.ok` true in `/readyz`.
