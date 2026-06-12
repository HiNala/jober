# Launch checklist

Tick every item before promoting staging → production or announcing publicly.

## Staging (verified 2026-06-10)

- [x] API `/readyz` green (postgres, redis, storage)
- [x] Public smoke: `bash scripts/staging-golden-path.sh` (or `railway-smoke.sh` with staging URLs)
- [x] CI golden path: `test_golden_path_integration.py` (fixture ATS, no live mass submit)
- [x] Release `v0.1.0` tagged; `CHANGELOG.md` updated
- [ ] `OPS_ALERT_WEBHOOK_URL` on Railway API (set your webhook, then `POST /api/admin/ops/test-alert`)

## Production cutover — domains & SSL

- [ ] Web public domain + SSL (Railway or custom)
- [ ] API public domain + SSL
- [ ] `NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_SITE_URL` match public URLs (web image rebuilt)
- [ ] `CORS_ORIGINS` and `WEB_APP_URL` match web origin
- [ ] `GOOGLE_REDIRECT_URI` matches API callback (if OAuth enabled)

## Health & deploy

- [x] `bash scripts/railway-smoke.sh` green on staging (API `/readyz` verified 2026-06-10)
- [ ] `bash scripts/uptime-check.sh` green; GitHub `uptime.yml` secrets set (see [uptime-monitoring.md](./uptime-monitoring.md))
- [x] API `/readyz` — postgres, redis, storage ok (staging)
- [ ] Worker `/readyz` — Celery ping ok (private)
- [x] Migrations applied (`alembic upgrade head` in API entrypoint logs)

## Observability & alerts

- [ ] `LOG_MODE=redacted`, `LOG_FORMAT=json` on API/worker (recommended)
- [ ] `OPS_ALERT_WEBHOOK_URL` set (Slack/Discord/PagerDuty incoming webhook) — verified locally via `dispatch_ops_alerts` 2026-06-10
- [ ] `POST /api/admin/ops/test-alert` returns `{"sent": true}` (after webhook var on Railway + admin session)
- [ ] Railway workspace usage budget + alert configured
- [ ] `SENTRY_DSN` set (optional but recommended for production)

## Security & secrets

- [ ] All secrets in Railway only — none in repo
- [ ] `JOBER_ENV=production`, `DEV_AUTH_BYPASS=false`, `AUTH_MODE=native`
- [ ] `REQUIRE_SECRETS=true`; placeholder secrets refuse boot
- [ ] `detect-secrets` clean in CI
- [ ] Rate limits active (`auth_rate_limit_*`)
- [ ] Policy CI green (`pytest -m policy`)

## Backups & restore

- [ ] Postgres automated backups + PITR enabled (Railway dashboard)
- [ ] Restore drill completed — see [restore-backup.md](./restore-backup.md)
- [ ] Object storage backup story documented (bucket or MinIO volume)

## Legal & privacy

- [ ] `/privacy`, `/terms`, `/acceptable-use` published (counsel review if public launch)
- [ ] Analytics consent banner live; tracking off until opt-in
- [ ] Export/delete flows tested (`/api/privacy/*`)

## Product posture (production)

- [ ] Default run policy: **review before submit** (not auto-submit)
- [ ] `AUTO_SUBMIT_OPT_IN=false` unless explicitly enabled per tenant
- [ ] Golden path green: CI `test_golden_path_integration.py` + staging smoke

## Admin & cost

- [ ] `/admin/overview` loads; budget + queue metrics visible
- [ ] `LLM_MONTHLY_BUDGET_USD` set; soft warn appears in admin when ≥80%
- [ ] `CELERY_WORKER_CONCURRENCY` aligned with budget (see deploy runbook)

## Release

- [x] Git tag created (`v0.1.0`) with release notes
- [x] `CHANGELOG.md` updated
- [ ] Post-launch review scheduled (reliability + cost + funnel, 7 days) — **target: 2026-06-17**
