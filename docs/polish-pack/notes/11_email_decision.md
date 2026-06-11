# Mission 11 — Email delivery decision

## Provider choice

**SMTP relay** (not a proprietary HTTP-only API) via `smtplib` in `jober_api.services.email.smtp`.

| Option | Why |
|--------|-----|
| **Chosen: SMTP** | Provider-agnostic; works with Resend SMTP, SendGrid, Mailgun, Postfix; Railway egress on 587 is standard |
| HTTP-only APIs | Rejected for v1 — would fork the `EmailSender` interface per vendor |

Recommended production setup: **Resend SMTP** (`smtp.resend.com:587`, user `resend`, password = API key) or equivalent.

## Backends

| `EMAIL_BACKEND` | Behavior |
|-----------------|----------|
| `console` | Default dev/CI — logs full message, no network |
| `smtp` | Real inbox delivery when `SMTP_HOST` + `EMAIL_FROM` set |
| `none` | Dispatch skipped; UI shows honest unavailable state |

## Architecture

1. API creates token → `dispatch_*` enqueues `jober_worker.tasks.send_transactional_email`
2. Worker imports `jober_api.services.email.sender.deliver_email_payload`
3. Dev fallback: if Celery broker unavailable, sync console send in `development` only

## Rollback

1. Set `EMAIL_BACKEND=console` on API + worker (stops outbound SMTP instantly)
2. Redeploy previous image if code regression
3. Users can still verify via support-issued tokens / dev headers in staging

## Security

- No tracking pixels or open analytics in templates
- `SMTP_PASSWORD` registered for log redaction
- Resend rate limit: `jober:auth:resend:` Redis bucket (3/hour default)
