# Email delivery failures

## Symptoms

- Users report missing verification or password-reset emails
- Admin webhook alert `email_send_failed` or `email_enqueue_failed`
- Worker logs `email.enqueue_failed` or Celery task `send_transactional_email` exhausted retries

## Diagnosis

1. Railway API + worker: `EMAIL_BACKEND=smtp`, `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM` set on **both** services
2. Worker logs: search `celery_task_start` + `email.sent` or `email_send_failed`
3. Correlation id from the user's error screen → grep API/worker logs for the same `correlation_id`
4. Resend/SMTP dashboard for bounces or rate limits

## Fix

| Cause | Action |
|-------|--------|
| `EMAIL_BACKEND=none` or missing SMTP | Set SMTP vars per [deploy.md](./deploy.md); redeploy API + worker |
| Worker not running | Restart worker; verify Celery consumes `send_transactional_email` |
| Invalid `EMAIL_FROM` domain | Align SPF/DKIM with provider; use verified sender |
| Enqueue failure (Redis down) | Fix Redis per [infra-down.md](./infra-down.md) |

## Verify

- `POST /api/admin/ops/test-alert` still works (webhook path)
- Trigger signup or forgot-password on staging; confirm inbox delivery
- Worker log line `email.sent` with masked `to=` address
