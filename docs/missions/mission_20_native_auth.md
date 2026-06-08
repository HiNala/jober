# Mission 20 — Native Authentication

## Task list
- [x] User account model: email (citext unique), password hash, verification, status, role, last_login
- [x] Argon2id password hashing (OWASP-tuned params)
- [x] Redis sessions: httpOnly cookies, CSRF on state-changing routes, refresh rotation
- [x] Flows: sign up, verify, sign in, sign out, forgot/reset, change password
- [x] Rate limiting + lockout on auth endpoints
- [x] Tenant-scoped data access via session (jobs, runs, documents, vault, resumes, imports/exports)
- [x] Cross-account tests for cookie sessions and document routes
- [x] `DEV_AUTH_BYPASS` (dev/test only; production boot guard)
- [x] Auth UI: sign in/up/forgot/reset + password meter + show password
- [x] Session UX: nav identity pill, cookie sessions for SSE, refresh endpoint
- [x] Iteration: sessions list + logout-all (settings UI); TOTP scaffolding endpoint

## Acceptance criteria
- [x] Argon2id hashes in DB; no plaintext passwords in logs
- [x] Sign-up→verify→sign-in→reset cycle (dev tokens via headers in development)
- [x] Cross-account cookie session test
- [x] `DEV_AUTH_BYPASS` production guard test
- [x] Lockout test after repeated failures

## Mission 99 (post–Mission 20)
- [x] Tenant-scope remaining artifact routers (documents, imports, exports, resumes)
- [x] Tenant-scope job-target sub-routes (extract, fill, discover, verify, recovery)
- [x] Shared `tenant_guard` helpers for job/run/observation checks
- [x] Fix flaky Redis session tests in CI
- [x] Re-auth modal on session expiry; silent refresh interval; `authFetch` recovery
- [x] Settings UI for active sessions and sign-out-everywhere
- [x] Cross-tenant tests for documents and job-profile routes

## Configuration
| Variable | Purpose |
|----------|---------|
| `AUTH_MODE` | `dev`, `native`, or `clerk` |
| `DEV_AUTH_BYPASS` | Auto-login seeded user (dev/test only) |
| `NEXT_PUBLIC_DEV_AUTH_BYPASS` | Web middleware skip |
| `SECRET_KEY` | Required outside dev |
