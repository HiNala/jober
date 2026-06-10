# Deploy runbook (Railway)

One-command deploy flow for staging and production on Railway.

## Prerequisites

- [Railway CLI](https://docs.railway.com/cli) installed and authenticated (`railway login`)
- Project linked or IDs known (`railway status --json`)
- Secrets set in Railway only — **never** in the repo (see `infra/railway/variables.example.env`)

## Storage choice

**Default: MinIO on a Railway volume** (self-hosted container, private networking).

- Persistent object storage for run artifacts and presigned URLs
- Attach a volume at `/data`; keep the service off the public internet
- Wire `MINIO_ENDPOINT` to `${{minio.RAILWAY_PRIVATE_DOMAIN}}:9000`

**Alternative: Railway native storage buckets**

- Create with `railway bucket create jober-artifacts`
- Set `MINIO_*` variables from `railway bucket credentials --bucket jober-artifacts --json`
- No volume management; backups follow Railway bucket policies

## One-command staging deploy

From the monorepo root, with project/environment linked:

```bash
railway up --service api --environment staging --detach -m "deploy api"
railway up --service worker --environment staging --detach -m "deploy worker"
railway up --service web --environment staging --detach -m "deploy web"
```

API runs `alembic upgrade head` in its entrypoint **before** uvicorn binds to `$PORT`.

## Service layout

| Service | Dockerfile | Public? | Health |
|---------|------------|---------|--------|
| `api` | `infra/docker/Dockerfile.api` | Yes (domain) | `/healthz`, `/readyz` |
| `web` | `infra/docker/Dockerfile.web.prod` | Yes (domain) | `/api/health` |
| `worker` | `infra/docker/Dockerfile.worker` | No | `/readyz` (Celery ping) |
| `Postgres` | Managed | No | Railway-managed |
| `Redis` | Managed | No | Railway-managed |
| `minio` | `minio/minio` + volume | No | Console optional, private only |

Attach per-service config: `infra/railway/*.railway.toml` in Railway Settings.

## Required variables (production)

- `JOBER_ENV=production`
- `DEV_AUTH_BYPASS=false`
- `AUTH_MODE=native` (not `dev`)
- `DATABASE_URL` as `postgresql+asyncpg://...` (rewrite Railway's `postgresql://` if needed)
- `REDIS_URL`, `SECRET_KEY`, `VAULT_ENCRYPTION_KEY`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
- `CORS_ORIGINS` = public web origin(s), comma-separated
- `WEB_APP_URL`, `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SITE_URL` = public URLs
- Worker: `PLAYWRIGHT_HEADED=false`

Boot **fails** if production secrets are placeholders or `DEV_AUTH_BYPASS` is set.

## Domains

```bash
railway domain --service web --json
railway domain --service api --json
```

Set `NEXT_PUBLIC_API_URL` to the **public** API URL at **web build time** (Docker build arg or Railway variable wired into the web Dockerfile).

Browsers cannot use `*.railway.internal` — only server-side services may.

## Staging → production

1. Clone environment: `railway environment new production --duplicate staging`
2. Run smoke on staging (below)
3. Promote by redeploying the same commit to production services
4. Re-run smoke on production

## Post-deploy smoke

```bash
export API_URL=https://<api-domain>
export WEB_URL=https://<web-domain>
bash scripts/railway-smoke.sh
```

The script checks `/healthz`, `/readyz`, web `/api/health`, landing HTML, and `/signup` (marketing funnel entry). The authenticated fixture pipeline (discover → fill → verify) is covered in CI by `test_golden_path_integration.py`; run it locally before promoting if you changed worker or API batch paths.

**Setting bucket credentials (CLI pitfall):** on PowerShell, pass credential strings explicitly — `railway variable set "MINIO_ACCESS_KEY=$($creds.accessKeyId)"` — not the whole `ConvertFrom-Json` object, or Railway stores a corrupted value and `/readyz` minio checks fail.

## Backups and restore

### Postgres

- Enable automated backups and point-in-time recovery in the Railway Postgres service settings.
- **Restore test (staging):** create a new environment from backup snapshot, point `DATABASE_URL` at the restored instance, run `bash scripts/railway-smoke.sh`, then tear down.

### Object storage

**MinIO on volume:** snapshot the attached volume before major migrations; export critical buckets with `mc mirror` to offline storage periodically.

**Railway buckets:** rely on Railway bucket durability; document bucket name and credentials in your secrets manager for re-provisioning.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Application failed to respond | Ensure process binds `0.0.0.0:$PORT` |
| API 503 on `/readyz` | Check Postgres SSL (`DATABASE_SSL=require` or `postgresql+asyncpg` URL), Redis, MinIO private host |
| Web "Cannot reach API" | `NEXT_PUBLIC_API_URL` must be the **public** API URL, rebuilt into the web image |
| Migrations failed | Check API deploy logs before uvicorn start; fix drift locally with `make migrate` |
| Worker restart loop | Confirm `PLAYWRIGHT_HEADED=false`, Chromium deps in image, `/readyz` after Celery ping |

## Usage budgets & alerts

Set Railway workspace usage alerts. Tie worker concurrency and batch limits to the cost governor.

| Variable | Purpose |
|----------|---------|
| `OPS_ALERT_WEBHOOK_URL` | Slack/Discord/PagerDuty incoming webhook for `/readyz` + admin attention |
| `OPS_ALERT_COOLDOWN_SECONDS` | Dedup window (default 900) |
| `LOG_FORMAT=json` | Structured logs for Railway log drains |
| `SENTRY_DSN` | Optional error tracking (install `sentry-sdk` in API image) |
| `LLM_MONTHLY_BUDGET_USD` | Monthly LLM cap; soft warn at 80% in admin |

Verify: `POST /api/admin/ops/test-alert` (admin session required).

## Related runbooks

- [launch-checklist.md](./launch-checklist.md)
- [rollback.md](./rollback.md)
- [restore-backup.md](./restore-backup.md)
- [worker-stuck.md](./worker-stuck.md)
- [queue-backed-up.md](./queue-backed-up.md)
- [cost-spike.md](./cost-spike.md)
- [infra-down.md](./infra-down.md)
- [rotate-secrets.md](./rotate-secrets.md)
