# Mission 19: Auth, Session, and Account Flow Hardening

## Purpose
Commit `67e04b7` switched cookies to `SameSite=None` for cross-origin Railway web+api — a production hotfix with security implications (`None` requires `Secure`, broadens CSRF exposure) that has not been systematically reviewed. This mission re-verifies the entire auth/session surface: cookies, CSRF, session lifecycle, OAuth linking, and account-management edges.

## Context From Audits
Application audit §14 ("re-verify SameSite=None implications; confirm CSRF token enforcement covers all mutating routes") and §19 risk #7. Stack: Argon2id native auth, Redis cookie sessions, CSRF protection, optional Google OAuth with `/link-google` password confirmation, RBAC permission registry with startup validation, `DEV_AUTH_BYPASS` refused in production.

## Scope
- **Cookie audit:** every cookie set by the API (session, CSRF, consent): flags (`Secure`, `HttpOnly`, `SameSite`, `Path`, `Max-Age`), and whether `SameSite=None` is actually required (same-site deployment under one domain would allow `Lax` — evaluate, recommend, but implement only the verified-safe option).
- **CSRF coverage:** enumerate all mutating routes (POST/PUT/PATCH/DELETE across 28 routers); prove each is CSRF-protected or deliberately exempt (webhooks with signature verification, the consent-gated `/api/events` collector); add tests for the exempt list.
- **Session lifecycle:** expiry, idle timeout, rotation on login/privilege change, logout invalidation (server-side, not cookie-clear only), concurrent session behavior, session fixation check.
- **OAuth edges:** Google link/unlink with stale tokens, unverified-email linking rules, account-recovery interaction with OAuth-only accounts.
- **Account flows:** password change invalidates other sessions; email-change confirmation (if present) safe; admin role changes take effect without re-login or are documented.
- Rate limiting on login/signup/reset endpoints (verify exists; add minimal Redis-based limits if absent — completion of a security expectation, not a new feature).

## Out of Scope
- New auth providers, MFA/2FA, passkeys (creep — note as future work only).
- UI changes beyond states already designed in Mission 06.
- Clerk-mode removal (flag the dead-code question for the owner; don't delete unilaterally).

## Starting Checklist
1. Read `apps/api/src/jober_api/routers/auth.py`, `services/auth/`, and the session/CSRF middleware end to end.
2. Read `tests/test_auth.py`, `test_auth_cookies.py`, `test_google_oauth.py`, `test_tenant_isolation.py` — the enforced contract today.
3. Read commit `67e04b7` diff (`git show 67e04b7`) and the deploy runbook's domain topology (are web+api on different origins permanently?).
4. `grep -rn "csrf" apps/api/src/jober_api` — where enforcement lives.
5. Read `auth/permissions.py` and `docs/architecture/rbac.md`.

## Tasks
1. Produce the cookie/CSRF/session matrix (`docs/polish-pack/notes/19_auth_matrix.md`) from code reading + live inspection (devtools against local and production).
2. Decide and document the SameSite posture; implement fixes for any flag gaps (`Secure` everywhere `None` is used, `HttpOnly` on session).
3. Write the parametrized CSRF coverage test (all mutating routes from the OpenAPI schema, asserting protection or membership in the documented exempt list).
4. Implement/verify session lifecycle items; add tests for logout invalidation and password-change session revocation.
5. OAuth edge walk + fixes; account-flow verification.
6. Rate-limit verification/addition with tests.
7. Re-run the production login flow after any deploy of these changes.

## Self-Improvement Loop
1. Inspect the next matrix row (probe with curl/devtools, not assumption).
2. Identify the highest-impact gap.
3. Make the smallest coherent fix.
4. Validate (auth test files + full suite + manual probe).
5. Update the matrix with evidence.
6. Repeat until every row is verified-safe.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q` (auth tests + new coverage test)
- `cd apps/web && pnpm test:e2e` (login/signup flows still pass)
- Manual: devtools cookie inspection local + prod; CSRF negative test (mutating request without token → rejected); logout → old session cookie rejected server-side.

## Acceptance Criteria
1. Auth matrix complete with evidence per row; no unverified cells.
2. CSRF coverage is test-enforced across all mutating routes with a documented exempt list.
3. Cookie flags correct everywhere; SameSite decision documented with rationale.
4. Logout and password-change revocation proven by tests.
5. Login/signup/reset rate-limited; all gates green.

## Documentation Requirements
- `docs/polish-pack/notes/19_auth_matrix.md`.
- Update `docs/architecture/threat-model.md` session/CSRF section to current reality.

## Git Workflow
`git status` first; security fixes in small reviewed commits (`fix(auth): … [pack-19]`); never commit secrets or real tokens in tests; push after gates.

## Production Guidance
Deploy promptly once gates pass — session hardening protects live users. Deploy in a window where you can immediately verify production login, OAuth link, and logout; have `docs/runbooks/rollback.md` ready since cookie-flag mistakes lock users out. `bash scripts/railway-smoke.sh` after.
