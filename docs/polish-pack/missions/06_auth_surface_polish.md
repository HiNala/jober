# Mission 06: Auth Surface Polish (Login, Signup, Recovery)

## Purpose
Auth pages currently float "on an empty void — no brand moment, no product preview, no trust strip" (UI-REVIEW screenshots 11–13). These pages are the conversion gate between marketing promise and product; they must carry the brand and reassure at the exact moment a user hands over credentials.

## Context From Audits
UI-REVIEW rows for `11-login.png`, `12-signup.png`, `13-forgot-password.png`; positioning audit §21.6 ("Auth pages carry the brand signature and a trust strip") and §12 (conversion friction). Routes live in `apps/web/src/app/(auth)/`: `login`, `signup`, `forgot-password`, `reset-password`, `link-google`. Native auth is Argon2id + cookie sessions (Mission 20 docs); Google OAuth optional behind `NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED`.

## Scope
- Design a shared `(auth)` layout: brand side-panel or backdrop using the (sparing) brand signature from the design direction, product preview element (static run-console capture is fine here), and a trust strip ("Review-before-submit · No third-party trackers · Your data encrypted").
- Apply to all five auth routes consistently, including the often-forgotten `reset-password` and `link-google`.
- Polish form details: input focus states, error presentation, password visibility toggle, submit pending states, "verification email sent" messaging that is **honest about current email status** (coordinate with Mission 11 — until email works, copy must not promise an email that never comes).
- Google button states when OAuth is disabled (hidden, not broken).

## Out of Scope
- Auth logic, session, CSRF, or cookie changes (Mission 20).
- New auth providers or magic links (feature creep).
- The brand signature's first creation if not yet designed — use a restrained gradient/grid placeholder consistent with tokens; Mission 28 finalizes the signature.

## Starting Checklist
1. Read `apps/web/src/app/(auth)/` layout and each page; note shared vs duplicated markup.
2. Read `apps/web/src/components/auth/` components and their states.
3. Check how auth errors surface from the API (`apps/api/src/jober_api/routers/auth.py` response shapes).
4. Review `docs/architecture/design-tokens.md` and `lib/design/tokens.ts` for the palette/spacing to use.
5. Confirm what the current post-signup screen claims about verification email.

## Tasks
1. Build/extend `(auth)/layout.tsx` with the two-zone composition (form zone + brand zone that collapses on mobile).
2. Add the trust strip component (reuse on marketing later — place it in `components/marketing/` or `components/product/`).
3. Unify form components: identical spacing, error slot, pending button behavior across all five routes.
4. Fix the post-signup verification message to match reality (see scope note); same for `forgot-password` confirmation.
5. Verify deep states: invalid/expired reset token page, OAuth error redirect, `link-google` password confirmation — each gets a designed state, not a raw error.
6. Add axe checks for auth routes to the e2e a11y spec; keyboard-only pass (tab order, focus visible, submit on Enter).
7. Re-capture screenshots 11–13 plus reset-password.

## Self-Improvement Loop
1. Inspect each auth route at 1440px and 375px, light/dark.
2. Identify the highest-impact gap (inconsistency, dead state, dishonest copy).
3. Make the smallest coherent improvement.
4. Validate (gates + manual auth walkthrough including failure paths).
5. Document the result.
6. Repeat until acceptance criteria hold.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion`
- `pnpm test:e2e` (auth a11y additions included)
- Manual: signup → login → logout → forgot-password → reset (use a locally-generated token) → login; Google flow if configured locally; wrong-password and rate-limit error displays.
- `cd apps/api && pytest -q tests/test_auth.py tests/test_auth_cookies.py` (no contract drift)

## Acceptance Criteria
1. All five auth routes share one visual system with brand zone + trust strip; nothing renders "on a void".
2. Every auth error/edge state (bad credentials, expired token, OAuth failure) renders designed UI.
3. Post-signup and forgot-password copy makes no false promises about email delivery.
4. Auth routes pass axe with no new violations and are fully keyboard operable.
5. Design Council gate ≥18/20 on the reworked surfaces (MASTER_PLAN §10).

## Documentation Requirements
- Closure notes + refreshed PNGs in `docs/screenshots/UI-REVIEW.md` for rows 11–13.
- Note in `docs/polish-pack/notes/` if Mission 11 must revisit any copy once email ships.

## Git Workflow
`git status` first; scope commits to `(auth)` + shared components (`feat(auth-ui): branded auth shell with trust strip [pack-06]`). Review diffs, meaningful bodies, push after gates.

## Production Guidance
Deployable after gates pass — visual-only change to auth surfaces with no logic changes. Manually verify production login immediately after deploy (it is the one flow a smoke script failure would hurt most); `bash scripts/railway-smoke.sh`.
