# Mission 37 — Auth & Google OAuth Production Completion

> **Phase:** Perfection pack  
> **Depends on:** M20, M21, polish 06 & 19  
> **Run Mission 99 after**

## Purpose

Make authentication **production-complete and honest**: native email/password fully reliable, Google OAuth either fully enabled or completely hidden, session lifecycle bulletproof, branded 2030 auth UI, zero fake controls.

## Context

M20–M21 implemented native auth + Google OAuth. Remaining gaps from audits:
- `NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED=false` by default → disabled-looking button history (partially fixed by hide-when-off)
- Email delivery for verify/reset must work in production
- Auth surfaces need M35/M36 dark brand treatment
- Fail-closed API auth in production (audit C7 — verify still held)
- Middleware must protect all `(app)` routes including admin/analytics/discover

## Scope

### In scope
- Production env wiring checklist for Google + SMTP
- Auth UI redesign on 2030 tokens (AmbientCanvas / brand signature)
- Hide Google when unconfigured; enable path documented + tested
- Session UX: re-auth modal, logout-all, idle timeout verification
- Rate limit + lockout re-verification
- E2E auth journey green
- Link-google flow polish

### Out of scope
- Adding GitHub/Apple OAuth (registry may stay ready; do not ship UI)
- Clerk mode expansion (native is primary)

## Starting checklist
- [ ] Read `mission_20`, `mission_21`, polish `06_auth_surface_polish`, `19_auth_session_hardening`
- [ ] Confirm `AUTH_MODE`, cookie names, CSRF double-submit pattern
- [ ] Inventory auth components under `components/auth/`

## Tasks

### 1. Security verification (close residual audit items)
- [ ] Confirm production boot rejects `AUTH_MODE=dev` and header fallback
- [ ] Confirm middleware `PROTECTED_PREFIXES` / matcher covers all app routes
- [ ] Confirm CSRF on all state-changing cookie-auth routes
- [ ] Confirm password reset tokens single-use + TTL

### 2. Google OAuth production path
- [ ] Document Google Cloud Console setup (local/staging/prod redirect URIs)
- [ ] Wire: when API has `GOOGLE_CLIENT_ID` + secret, set web flag true in deploy config
- [ ] Full flow test: signup via Google, login returning, link/unlink, last-method protection
- [ ] Error mapping: `oauth_state`, `oauth_denied`, `email_unverified` → user-visible banners
- [ ] **Never** show disabled “coming soon” Google button

### 3. Email delivery
- [ ] Verify Resend/SMTP (or configured provider) for verify + reset in staging
- [ ] Branded email templates match dark product (simple HTML, logo, single CTA)
- [ ] Dev mode: token header / log path unchanged for CI

### 4. Auth UI 2030
- [ ] Login / signup / forgot / reset / verify-pending: AmbientCanvas, trust strip, large type
- [ ] Password meter + show password retained
- [ ] Mobile: full-width forms, 44px targets, keyboard-friendly
- [ ] Success states clear (check email, password updated, verified)

### 5. Tests
- [ ] API: google oauth unit/integration suite green
- [ ] Web e2e: `auth-journey.fullstack.spec.ts` green
- [ ] Manual: Google real credentials on staging once

## Validation
```bash
cd apps/api && ruff check src tests && mypy src && pytest tests/test_auth.py tests/test_auth_cookies.py tests/test_google_oauth.py tests/test_security_controls.py -q
cd apps/web && pnpm typecheck && pnpm lint:strict
# e2e with stack up
pnpm exec playwright test e2e/auth-journey.fullstack.spec.ts e2e/a11y-auth.spec.ts
```

## Acceptance criteria
- [ ] No visible disabled Google control
- [ ] Staging: email verify + password reset deliver
- [ ] Staging: Google OAuth completes when secrets set
- [ ] Auth UI Design Council ≥19/20
- [ ] All auth-related audit criticals remain closed

## Configuration matrix

| Env | AUTH_MODE | Google | Email |
|-----|-----------|--------|-------|
| local | native or dev | optional | log/header |
| staging | native | on if secrets | real SMTP |
| production | native | on if secrets | real SMTP |

## Production guidance
- Rotate secrets after any leak; follow `docs/runbooks/rotate-secrets.md`
- Deploy API + web together when cookie/domain settings change
