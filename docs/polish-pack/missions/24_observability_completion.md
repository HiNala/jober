# Mission 24: Observability Completion and Alert Drill

## Purpose
Build-mission 34 added ops metrics, webhook alerts, structured logs, and an optional Sentry hook. This mission verifies the whole observability chain actually fires end-to-end in production — metrics are truthful, alerts arrive, logs are queryable and redacted, dashboards reflect reality — and closes instrumentation gaps found by earlier missions.

## Context From Audits
Application audit §6/§18: `/admin/overview` shows LLM budget, run success rate, Celery backlog, circuit-breaker attention; `OPS_ALERT_WEBHOOK_URL` + `POST /api/admin/ops/test-alert`; `scripts/uptime-check.sh`; Sentry via importlib (commits `0831dbf`, `8ebc152`); structured logging with `LOG_MODE` redaction. New surfaces since M34: email sending (Mission 11), error envelope + correlation ids (Mission 18). **Mission 15** defers `/runs/[id]` and `/admin` screenshot capture into `docs/screenshots/` when a seeded fixture run is available — include admin overview in the capture pass if an admin account exists.

## Scope
- **Truth audit of `/admin/overview`:** each metric traced to its source query and spot-verified against raw data (run success rate, backlog depth, LLM spend vs `LlmCall`).
- **Alert drill:** configure `OPS_ALERT_WEBHOOK_URL` (real destination the owner reads — webhook to Discord/Slack/etc. as configured), fire `POST /api/admin/ops/test-alert`, then force each real alert class locally/staging where safe: circuit-breaker trip, LLM budget threshold, queue backlog, **email-send failure (new — add this alert class if missing, it guards Mission 11's flow)**.
- **Sentry decision:** enable it (DSN in Railway) or explicitly decide against it; if enabled, verify a forced exception lands with redacted context and correlation id from Mission 18.
- **Log usability:** pick three real debugging questions ("why did run X fail", "who hit 402 today", "what did tenant Y purge") and verify each is answerable from Railway logs with the current structure; fix log fields if not.
- **Uptime:** verify `scripts/uptime-check.sh` runs on a real schedule (Railway cron or external monitor) and alerts on failure — a script with no scheduler is not monitoring.
- Correlation id propagation: web request → API log → Celery task log for one golden-path run.

## Out of Scope
- New observability platforms (Grafana/Prometheus stack) — recommend only.
- Metrics beyond what the admin dashboard already promises.
- Log retention/shipping infrastructure changes.

## Starting Checklist
1. Read `services/ops/` and the admin overview service; list every displayed metric and its query.
2. Read the alert dispatch code and existing alert classes.
3. `git show 4a1bd06` (ops infrastructure commit) for the intended design.
4. Check Railway for current values of `OPS_ALERT_WEBHOOK_URL`, Sentry DSN, cron config (`railway variables` via the deploy runbook flow).
5. Read `docs/runbooks/` alert-adjacent runbooks (cost-spike, queue-backed-up, worker-stuck) — alerts should reference them.

## Tasks
1. Metric truth table (`docs/polish-pack/notes/24_observability.md`): metric × source × spot-check result.
2. Alert drill matrix: class × trigger method × received? × runbook linked? Fix silent classes; add the email-failure alert.
3. Sentry decision + implementation/verification (forced error → event with redacted payload).
4. Log-usability drill (three questions); add missing structured fields (run_id, tenant_id, correlation_id) where absent.
5. Schedule/verify uptime monitoring with alerting on failure.
6. Correlation trace drill across web → API → worker.
7. Update alert messages to link the relevant runbook.

## Self-Improvement Loop
1. Inspect the next untraced metric/alert/log question.
2. Identify the highest-impact blind spot.
3. Make the smallest coherent fix.
4. Validate by re-firing the drill.
5. Record evidence.
6. Repeat until every drill row passes.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q`
- `cd apps/worker && ruff check src tests && mypy src && pytest -q`
- Drill evidence: received alert payloads (screenshots/links), Sentry event link or decision record, log-query transcripts.

## Acceptance Criteria
1. Every admin-overview metric spot-verified truthful.
2. Every alert class fires to a destination the owner actually reads; email-failure alerting exists.
3. Sentry decision implemented and verified (or documented rejection).
4. The three debugging questions answerable from production logs; correlation ids propagate across all three tiers.
5. Uptime check runs on a schedule with failure alerting; all gates green.

## Documentation Requirements
- `docs/polish-pack/notes/24_observability.md` (truth table, drill matrix, evidence).
- Runbook cross-links in alert payloads documented in the relevant runbooks.

## Git Workflow
`git status` first; commits per drill fix; webhook URLs and DSNs stay in Railway env, never in code; push after gates.

## Production Guidance
This mission inherently touches production configuration. Make env changes one at a time, verify each with its drill, and record before/after in the notes. Deploy code changes (new alert class, log fields) after gates; `bash scripts/railway-smoke.sh` after.
