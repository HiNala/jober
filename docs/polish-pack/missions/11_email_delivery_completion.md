# Mission 11: Email Delivery Completion (Verification and Password Reset)

## Purpose
Signup verification tokens are created but never sent, and password reset is a dead end in production (README: "email verification tokens are created but outbound email is not configured yet"). This is the largest broken flow in the product and the explicit exception to the no-new-features rule: it completes an existing, half-built flow that the product promise requires.

## Context From Audits
Application audit §7.2, §19 risk #2; positioning audit §12.1 ("a signup-killing defect"); golden-path findings from Mission 03 (the production walkthrough recorded the exact dead-end UX). Auth internals: native auth from build-mission 20 (`apps/api/src/jober_api/routers/auth.py`, `services/auth/`), token creation already exists.

## Scope
- Choose and integrate one transactional email provider behind a thin, swappable interface (an SMTP-based implementation keeps it provider-agnostic and self-host friendly; a provider HTTP API is acceptable if SMTP is impractical on Railway — record the decision and rationale).
- Send: signup verification, password reset, and (if tokens already exist for it) email-change confirmation. Nothing else — no marketing email, no digests.
- Plain, branded, text-first templates (HTML optional; text part mandatory); links use the production web URL from config.
- Local/CI behavior: console/log backend (emails printed/captured, never sent) — CI must stay green with zero external calls.
- Honest fallback: when no email backend is configured, the UI states verification is unavailable rather than promising an email (coordinates with Mission 06 copy).
- Config: env vars added to `.env.example` and `infra/railway/variables.example.env`; production boot validation extended if email is required-for-launch.
- Rate-limit resend endpoints; tokens expire; resend UX on the "check your email" screen.

## Out of Scope
- Email analytics, open tracking (contradicts the no-tracker stance), queued digests, marketing email, inbound email.
- Replacing the auth flow itself.

## Starting Checklist
1. Read `apps/api/src/jober_api/routers/auth.py` and `services/auth/` — where tokens are created, current TTLs, what a "send" hook would attach to.
2. `grep -rn "verification\|reset_token\|email" apps/api/src/jober_api/services/auth` — existing stubs or TODOs.
3. Read `apps/api/src/jober_api/config.py` (or settings module) for the env-var pattern and production boot validation (the README documents boot refusal on placeholder secrets).
4. Check worker/Celery availability for async sending (sending should not block the request thread; a Celery task fits the existing architecture).
5. Check Railway constraints in `docs/runbooks/deploy.md` (SMTP egress availability).

## Tasks
1. Implement `EmailSender` interface + two backends: `console` (default, dev/CI) and the chosen real backend; select via env (`EMAIL_BACKEND`, `EMAIL_FROM`, provider creds).
2. Dispatch sends as Celery tasks with retry/backoff; log redacted (address partially masked) per `LOG_MODE` conventions.
3. Wire into signup, resend-verification, and password-reset paths; add resend rate limiting (Redis, consistent with existing pacing utilities).
4. Templates: verification + reset, text-first, tokens in links to `/(auth)` routes; verify `reset-password` consumes the link correctly end-to-end.
5. Web: "check your email" states with resend button + cooldown; unconfigured-backend honest state.
6. Tests: unit tests for the sender interface + console backend capture; API tests asserting send-task enqueue on signup/reset; rate-limit test. No network in tests.
7. Update `.env.example`, `infra/railway/variables.example.env`, README auth section, and `docs/runbooks/deploy.md`.
8. Configure the provider in Railway (staging first if available), send a real verification to a test address, complete the full verify + reset loop in production.

## Self-Improvement Loop
1. Inspect the flow end-to-end (signup → email → verify → login; forgot → email → reset → login).
2. Identify the highest-impact gap (unsent case, broken link, missing state).
3. Make the smallest coherent improvement.
4. Validate (tests + manual loop).
5. Document.
6. Repeat until both loops complete in production.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q` (incl. new email tests)
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build`
- `pnpm test:e2e`
- Local manual: console backend prints both email types with working localhost links.
- Production manual: real verification + reset emails received and links complete the loops.

## Acceptance Criteria
1. Signup verification and password reset work end-to-end in production with a real inbox.
2. Dev/CI never attempt network email; CI green.
3. Resend is rate-limited; tokens expire; all related UI states are designed and honest.
4. Env/docs updated; boot validation reflects the email requirement decision.
5. No tracking pixels or third-party analytics in emails.

## Documentation Requirements
- README auth section + `docs/runbooks/deploy.md` (provider setup, env vars, failure runbook pointer).
- `docs/polish-pack/notes/11_email_decision.md`: provider choice rationale and rollback plan.
- Update Mission 03 findings file: mark the dead-end finding resolved.

## Git Workflow
`git status` first; commits: interface+backends → wiring+rate-limit → web states → docs/env. Bodies cover what/why/validation/follow-ups. Secrets never committed — verify with the pre-commit detect-secrets hook. Push after gates.

## Production Guidance
Deployment is the point of this mission, but gate it: full gates green, console-backend behavior verified locally, provider creds set in Railway only (never in repo), deploy API + web together, then immediately run the production verify + reset loops and `bash scripts/railway-smoke.sh`. Roll back via `docs/runbooks/rollback.md` if sends fail.
