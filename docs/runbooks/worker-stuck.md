# Worker stuck

## Symptoms

- Runs stay `queued` / `in_progress` forever
- Admin overview: Celery backlog high, **active runs = 0**
- Worker `/readyz` fails or worker logs show crash loop

## Diagnosis

```bash
railway logs --service worker --lines 100
railway service status --service worker --json
```

- Playwright/Chromium missing → build image issue
- `psycopg` SSL errors → check `DATABASE_URL` driver (`postgresql+psycopg` or Railway URL with `ssl=disable` stripped correctly)
- Import errors in Celery task module

Check admin **Celery backlog** and **active runs** on `/admin/overview`.

## Fix

1. **Restart worker:** `railway restart --service worker --yes`
2. **Redeploy** if image stale: `railway up --service worker`
3. Confirm env: `PLAYWRIGHT_HEADED=false`, `CELERY_BROKER_URL`, `REDIS_URL`
4. Scale concurrency down if OOM: `CELERY_WORKER_CONCURRENCY=1`
5. Clear poison message: inspect Redis `celery` list; purge only if identified bad task (destructive)

## Verify

- Worker `/readyz` returns ready (private network)
- `make ping-worker` or enqueue test batch item
- Backlog drains; active runs > 0 during work
