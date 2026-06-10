# Cost spike / LLM budget

## Symptoms

- Admin attention: LLM soft warn or hard stop
- HTTP 402 on batch enqueue or document generation
- `OPS_ALERT_WEBHOOK_URL` fires budget message

## Diagnosis

1. `/admin/overview` — **LLM budget (month)** line
2. `/admin/cost` — spend by model/agent/day
3. Check anomalous batch concurrency or runaway retries

## Fix

### Soft warn (≥80% of `LLM_MONTHLY_BUDGET_USD`)

- Pause non-essential batches
- Lower `CELERY_WORKER_CONCURRENCY`
- Review failed retry loops on same job

### Hard stop (budget exceeded)

- Generation blocked until next month or budget raised
- Set `LLM_MONTHLY_BUDGET_USD` higher in Railway (temporary)
- Enable BYOK for heavy tenants (Settings)

### Simulate alert (staging test)

1. Set `LLM_MONTHLY_BUDGET_USD=0.01` on staging API
2. Trigger one LLM call → expect 402
3. Load `/admin/overview` → error attention + webhook (if configured)

## Verify

- `budget_status` shows expected spend
- Admin attention clears after budget increase or month rollover
