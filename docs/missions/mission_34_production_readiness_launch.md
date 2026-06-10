# Mission 34 — Production Readiness, Observability & Launch

## Task list
- [x] **Observability:** JSON log format (`LOG_FORMAT=json`); `safe_log` redaction; optional `SENTRY_DSN`; admin ops metrics (success rate, budget, queue depth, circuit trips)
- [x] **Alerting:** `OPS_ALERT_WEBHOOK_URL` + cooldown; fires on `/readyz` failure and admin error/warn attention; `POST /api/admin/ops/test-alert`
- [x] **Runbooks:** deploy, rollback, restore, worker-stuck, queue-backed-up, cost-spike, infra-down, rotate-secrets, launch-checklist
- [x] **Backups:** restore drill procedure documented (`docs/runbooks/restore-backup.md`)
- [x] **Security:** launch checklist covers secrets, policy CI, rate limits, redaction
- [x] **Legal/compliance:** launch checklist covers published legal pages + consent/export/delete
- [x] **Launch checklist:** `docs/runbooks/launch-checklist.md`
- [x] **Ship:** `CHANGELOG.md`, `scripts/uptime-check.sh`, release tag `v0.1.0`

## Acceptance criteria
- [ ] Alerts fire on simulated failures (test-alert + budget/readyz simulation on staging)
- [ ] Restore drill executed and recorded in restore-backup.md
- [ ] Launch checklist ticked for production
- [ ] Golden path in production (fixture; no live mass submit)
- [x] Security + legal checks codified in launch checklist
- [x] Release tagged with notes

## Alert wiring

```bash
# Slack/Discord incoming webhook URL
OPS_ALERT_WEBHOOK_URL=https://...
OPS_ALERT_COOLDOWN_SECONDS=900

# Verify
curl -X POST -H "Cookie: ..." https://api.example.com/api/admin/ops/test-alert
```

## Mission 99

Run after CI green on M34 commits.
