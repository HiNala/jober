# Queue backed up

## Symptoms

- Many jobs pending; users see slow batch progress
- Admin: **Celery backlog** high; attention banner “broker backlog with no active runs”
- `globally_paused` may be true

## Diagnosis

1. `/admin/overview` — queue paused? active runs vs max concurrency?
2. `/api/dashboard/summary` — `queue_depth_priority_a` is a SQL aggregate (not a full table scan); high depth is real backlog, not a measurement artifact.
3. Worker health — [worker-stuck.md](./worker-stuck.md)
4. Domain locks / cooldown — batch pacing may be intentional (`BATCH_SITE_COOLDOWN_SECONDS`); two batches on the same host serialize via Redis `jober:batch:domain_lock:*`.

## Fix

| Cause | Action |
|-------|--------|
| Global pause | Admin config or API: resume queue |
| Worker down | Restart/redeploy worker |
| Concurrency too low | Raise `CELERY_WORKER_CONCURRENCY` (watch LLM budget) |
| Domain lock stuck | Redis: inspect `jober:batch:domain_lock:*`; release if stale |
| Budget hard stop | Raise budget or wait for month rollover — [cost-spike.md](./cost-spike.md) |

## Verify

- Backlog decreases over 5–10 minutes
- New runs transition to `succeeded` / `needs_human` appropriately
