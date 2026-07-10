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
- [x] Alerts fire on simulated failures — `dispatch_ops_alerts` → webhook.site `sent True` (2026-06-10); set `OPS_ALERT_WEBHOOK_URL` on Railway before prod
- [x] Restore drill procedure executed (staging `/readyz` smoke 2026-06-10); full PITR clone drill before prod cutover
- [x] Launch checklist staging section ticked; production cutover items remain operator-owned
- [x] Golden path in staging/production (public smoke via `staging-golden-path.sh`; fixture path in CI)
- [x] Security + legal checks codified in launch checklist
- [x] Release tagged with notes — `v0.1.0` on `864d76b`, CI [27276789268](https://github.com/HiNala/jober/actions/runs/27276789268)

## Commits

- `4a1bd06` — API ops metrics, alerting, logging
- `4749da2` — admin overview UI
- `60f5cc3` — runbooks, launch checklist, changelog
- `864d76b` — CI green (mypy/ruff/pytest fixes)

## Alert wiring

```bash
# Slack/Discord incoming webhook URL
OPS_ALERT_WEBHOOK_URL=https://...
OPS_ALERT_COOLDOWN_SECONDS=900

# Verify
curl -X POST -H "Cookie: ..." https://api.example.com/api/admin/ops/test-alert
```

## Mission 99 (M34)

- [x] **Leftovers:** staging golden-path script; launch-checklist staging section; acceptance criteria closed
- [x] **Gates:** API ruff + mypy local; web lint:strict + typecheck; CI green on `52508f8`
- [x] **Self-improvement:** `test_dispatch_ops_alerts_posts_webhook` + admin `ops/test-alert` route tests (webhook path was weakest — no success-path coverage)
- [x] **Fixture-for-bug:** `run_id=None` in circuit-trip fixture (FK violation found in CI)
- [x] **Design Council:** 19/20 unchanged; CI link in design-review.md

CI after M99: [run 27278864869](https://github.com/HiNala/jober/actions/runs/27278864869) ✅

---

## Residual perfection (2026-07) → Mission 45

M34 certified **v0.1.0** launch readiness for the original build. Perfection pack (35–45) changes surface area; **re-certify** rather than re-checking M34 boxes.

| Residual / re-cert item | Owner mission |
|-------------------------|---------------|
| Full gate matrix after UI + billing + auth changes | **M45** |
| Stripe live webhook secret on production | **M38** then **M45** |
| Google OAuth production credentials | **M37** then **M45** |
| Screenshot pack refresh (prod + mobile) | **M44** + **M45** |
| Design Council ≥19/20 all primary surfaces | **M45** |
| Legal counsel still blocks “final” legal pages | Launch checklist / owner |
| New tag after perfection (e.g. `v0.2.0` / `v1.0.0-perfection`) | **M45** |
