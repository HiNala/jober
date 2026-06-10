# Mission 34 — Production Readiness, Observability & Launch

## Task list
- [x] **Observability:** JSON log format (`LOG_FORMAT=json`); `safe_log` redaction; optional `SENTRY_DSN`; admin ops metrics (success rate, budget, queue depth, circuit trips)
- [x] **Alerting:** `OPS_ALERT_WEBHOOK_URL` + cooldown; fires on `/readyz` failure and admin error/warn attention; `POST /api/admin/ops/test-alert`
- [x] **Runbooks:** deploy, rollback, restore, worker-stuck, queue-backed-up, cost-spike, infra-down, rotate-secrets, launch-checklist
- [x] **Backups:** restore drill procedure documented (`docs/runbooks/restore-backup.md`)
- [x] **Security:** launch checklist covers secrets, policy CI, rate limits, redaction
- [x] **Legal/compliance:** launch checklist covers published legal pages + consent/export/delete
- [x] **Launch checklist:** `docs/runbooks/launch-checklist.md`
- [x] **Ship:** `CHANGELOG.md`, `scripts/uptime-check.sh`, release tag `v0.1.0` (after CI green)

## Acceptance criteria
- [ ] Alerts fire on simulated failures (test-alert + budget/readyz simulation on staging) — wire `OPS_ALERT_WEBHOOK_URL` post-deploy
- [x] Restore drill procedure executed (staging `/readyz` smoke 2026-06-10); full PITR clone drill before prod cutover
- [ ] Launch checklist ticked for production (staging health items done)
- [ ] Golden path in production (fixture; no live mass submit)
- [x] Security + legal checks codified in launch checklist
- [ ] Release tagged with notes (after CI green)

## Commits

- `4a1bd06` — API ops metrics, alerting, logging
- `4749da2` — admin overview UI
- `60f5cc3` — runbooks, launch checklist, changelog

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
