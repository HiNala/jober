# Mission 13 — Batch Ops, Scheduling & Rate Limits

## Task list

### Batch builder
- [x] Filter preview (priority, ATS, status, location)
- [x] Create batch with policy (`dry_run` / `review_before_submit` / `auto_submit` with opt-in)
- [x] Enqueue + scheduled start hook

### Queue control
- [x] Pause-all / resume-all / cancel-run
- [x] Per-batch pause/resume
- [x] Reorder + per-job skip

### Concurrency & pacing
- [x] Configurable max concurrency (default 1) in Redis
- [x] Per-domain lock — never parallel applications to same ATS domain
- [x] Per-site cooldown + action delay (server-friendliness, documented)

### Scheduling
- [x] Celery beat orchestrator tick
- [x] Quiet-hours gate for non-dry-run batches

### Idempotency & cost
- [x] Skip already-applied + prior successful runs at preview
- [x] Monthly LLM budget hard-stop via `assert_generation_budget`

### Dashboard
- [x] Live metrics, worker capacity, batch panel, quick actions

### Iteration clause
- [x] Daily plan generator (`GET /api/batches/daily-plan`)

## Acceptance criteria
- [x] Same-domain serialization via Redis domain lock (tests)
- [x] Cooldown spacing recorded in events / redis timing (tests)
- [x] Re-enqueue refused for applied / succeeded jobs (preview)
- [x] Budget hard-stop (test)
- [x] Pause/resume API + dashboard wiring

## Mission 99
- [ ] Run full gates; push to `origin/main`
