# Auth / session / CSRF matrix — Mission 19

**Date:** 2026-06-11 · **Evidence:** code review + `test_csrf_coverage.py`, `test_auth.py`, `test_auth_cookies.py`

## Deployment topology (SameSite decision)

| Environment | Web origin | API origin | `COOKIE_SECURE` | SameSite | Rationale |
|-------------|------------|------------|-----------------|----------|-----------|
| Local dev | `http://localhost:3000` | `http://localhost:8000` | `false` | `Lax` | Same registrable domain not required; lax is sufficient for localhost cross-port |
| Railway prod | `https://*.up.railway.app` (web) | `https://*.up.railway.app` (api) | `true` (required) | `None` | **Cross-origin** cookies: web and API are different sites; `None` + `Secure` required for `credentials: include` (commit `67e04b7`) |
| Future same-site | `https://app.jober.example` + API at `https://app.jober.example/api` | shared | `true` | `Lax` (candidate) | If reverse-proxied to one origin, can tighten to `Lax` — not implemented until topology changes |

Production boot **refuses** `JOBER_ENV=production` without `COOKIE_SECURE=true` (`secrets_check.py`).

## Cookies set by API

| Cookie | Purpose | HttpOnly | Secure (prod) | SameSite | Path | Max-Age | Set by |
|--------|---------|----------|---------------|----------|------|---------|--------|
| `jober_session` | Redis session id | yes | yes | None/Lax | `/` | `session_ttl_seconds` (24h) | `set_auth_cookies` |
| `jober_refresh` | Refresh rotation id | yes | yes | None/Lax | `/` | `refresh_ttl_seconds` (7d) | `set_auth_cookies` |
| `jober_csrf` | Double-submit CSRF token | **no** (JS reads) | yes | None/Lax | `/` | `session_ttl_seconds` | `set_auth_cookies` |
| `jober_analytics_consent` | Client-only consent flag | n/a (web) | n/a | n/a | n/a | n/a | **Web** (`analytics` UI), not API |

## CSRF enforcement

| Control | Implementation | Evidence |
|---------|----------------|----------|
| Global middleware | `CsrfMiddleware` on mutating `/api/*` when `jober_session` cookie present | `auth/csrf.py`, `main.py` |
| Algorithm | Header `X-CSRF-Token` == `jober_csrf` cookie == Redis session `csrf` field | `verify_csrf()` |
| Web client | `apiFetch` / `auth.ts` attach header from cookie on non-GET | `apps/web/src/lib/api/client.ts` |
| Exempt prefixes | `PUBLIC_API_PREFIXES` in `auth/deps.py` | Parametrized `test_csrf_coverage.py` |
| Dev/test without cookies | Header auth (`X-Jober-*`) — no session cookie → CSRF skipped | `test_dev_header_mutations_skip_csrf_without_session_cookie` |

### CSRF exempt routes (documented)

All paths under:

- `/api/events` — consent-gated analytics collector (no session auth)
- `/api/waitlist/` — public marketing signup
- `/api/webhooks/` — Stripe/signature-verified
- `/api/health`
- `/api/auth/register`, `/login`, `/verify-email`, `/forgot-password`, `/reset-password`, `/refresh`
- `/api/auth/google/start`, `/callback`, `/confirm-link`
- `/api/auth/email-delivery` (GET only in practice)

Webhooks verify provider signatures separately. Auth bootstrap routes run before a CSRF token exists.

## Session lifecycle

| Concern | Behavior | Evidence |
|---------|----------|----------|
| Absolute TTL | Redis `SETEX` on session + refresh keys | `sessions.py` |
| Idle timeout | **Not separate** — absolute TTL only; documented residual | `session_ttl_seconds` |
| Rotation on login | New `create_session` per login/register | `auth.py` login/register |
| Rotation on refresh | `refresh_session` revokes old, creates new | `sessions.py` |
| Logout | `revoke_session` in Redis + `clear_auth_cookies` | `test_logout_invalidates_session_server_side` |
| Logout all | `revoke_all_sessions` | `auth.py` `/logout-all` |
| Password change | `revoke_other_sessions` keeps current session | `test_password_change_revokes_other_sessions` |
| Password reset | `revoke_all_sessions` on reset | `service.py` `reset_password` |
| Session fixation | New session id on login/OAuth issue | `create_session` uses `secrets.token_urlsafe` |
| Concurrent sessions | Allowed; listed via `/api/auth/sessions` | `list_active_sessions` |
| Admin role change | Role read from DB each request (`get_auth_context`) — **no re-login required** | `auth/deps.py` |

## OAuth edges

| Scenario | Behavior |
|----------|----------|
| Link while signed in | `/google/link/start` requires auth; attaches identity |
| Email collision on sign-in | Pending link + `/google/confirm-link` requires password | `oauth_service.confirm_oauth_link` |
| Unlink only provider | Blocked if last sign-in method | `unlink_provider` → 400 |
| Unlink native | Blocked at router | `auth.py` |
| OAuth callback errors | Redirect to web with `?error=` | `google_oauth_callback` |

## Rate limiting

| Endpoint bucket | Mechanism | Default |
|-----------------|-----------|---------|
| register, login, verify-email, forgot-password, reset-password, google/* | `check_rate_limit` per IP+path | 20 / 5 min |
| resend-verification | `check_resend_rate_limit` per email | 3 / hour |
| failed logins | `record_failed_login` → lockout | 5 failures / 15 min lock |

## Account / production guards

| Check | Production |
|-------|------------|
| `DEV_AUTH_BYPASS` | Refused |
| `AUTH_MODE=dev` | Refused |
| `COOKIE_SECURE` | Required |
| Clerk mode | **Flagged** — `auth_mode=clerk` path exists; owner decision on removal (out of scope) |

## Open / future

- MFA / passkeys — not in scope (Mission 19)
- Tighten SameSite to `Lax` if single-origin deploy
- Separate idle timeout (optional hardening)
