# Uptime monitoring

## What runs

`scripts/uptime-check.sh` wraps `scripts/railway-smoke.sh` (API `/healthz`, `/readyz`, optional web URL). After **3** consecutive failures it POSTs to `OPS_ALERT_WEBHOOK_URL` with `source: uptime_check`.

## Required env

| Variable | Example |
|----------|---------|
| `API_URL` | `https://api.jober.app` |
| `WEB_URL` | `https://jober.app` (optional) |
| `OPS_ALERT_WEBHOOK_URL` | Slack/Discord incoming webhook |
| `JOBER_ENV` | `production` |

## Schedule options

### GitHub Actions (repo default)

Workflow `.github/workflows/uptime.yml` runs every 5 minutes when repository secrets are set:

- `UPTIME_API_URL` — public API base URL
- `UPTIME_WEB_URL` — public web URL (optional)
- `UPTIME_OPS_ALERT_WEBHOOK_URL` — same webhook as Railway `OPS_ALERT_WEBHOOK_URL`

Enable: GitHub → Settings → Secrets and variables → Actions → add the secrets above.

### External cron

Any host with bash + curl:

```bash
*/5 * * * * API_URL=https://api.example.com WEB_URL=https://app.example.com \
  OPS_ALERT_WEBHOOK_URL=https://hooks... JOBER_ENV=production \
  /path/to/jober/scripts/uptime-check.sh
```

### Manual verify

```bash
API_URL=https://api.example.com WEB_URL=https://app.example.com bash scripts/uptime-check.sh
```

## Alert payload

Includes `runbook: docs/runbooks/uptime-monitoring.md` when fired from the script (see script body).

## Related

- [deploy.md](./deploy.md) — observability env vars
- [infra-down.md](./infra-down.md) — sustained outage response
