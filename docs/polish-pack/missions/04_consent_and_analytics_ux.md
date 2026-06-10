# Mission 04: Consent UX Repair (Analytics Banner → One-Time Bottom Sheet)

## Purpose
The analytics consent toast floats over nearly every production screen, overlapping the footer CTA on the landing page and "breaking immersion" across the app (UI-REVIEW, cross-cutting theme 6). It is the single most pervasive UX defect because it degrades every other surface. Fix it once, correctly, before polishing the screens it sits on.

## Context From Audits
UI-REVIEW executive summary: "Floating analytics toast — nearly every screen — breaks immersion; competes with primary content" and theme 6: "Consent UX — bottom sheet once per device, not a persistent toast over product UI." Positioning audit §12.3 and §21.5. Constraints from Mission 25 docs: analytics is first-party only, collector requires the `jober_analytics_consent=1` cookie, honors DNT, events batch via `apps/web/src/lib/analytics/sdk.ts` with `sendBeacon`.

## Scope
- Replace the persistent toast with a bottom sheet (the repo already ships `vaul` for sheets) shown **once per device** until answered, with Accept / Decline and a link to `/privacy`.
- Persist the decision (cookie `jober_analytics_consent` plus a local "prompted" marker) so neither choice re-prompts; expose a "Change analytics consent" control in `/settings` so decline is reversible.
- Ensure zero overlap with primary content: sheet is modal-light at the viewport bottom, dismissible, never rendered above run-console controls.
- Verify the SDK behaves correctly for all three states (unset / accepted / declined): no events sent before accept, DNT still wins, UTM attribution from Missions 29–30 still records on accept.

## Out of Scope
- Any change to the collector (`POST /api/events`), retention, or rollups.
- Cookie-law geo logic or a CMP integration (feature creep).
- Redesigning the settings page beyond adding the consent control.

## Starting Checklist
1. Locate the current banner: `grep -rn "consent" apps/web/src/components apps/web/src/lib/analytics`.
2. Read `apps/web/src/lib/analytics/sdk.ts` — how consent is read, when batches flush, anon-id rotation.
3. Read `apps/api/src/jober_api/routers/analytics.py` collector requirements (cookie name, DNT handling).
4. Check existing tests touching consent: `grep -rn "consent" apps/web/src --include="*.test.*"` and `apps/api/tests/test_analytics.py`.
5. Review screenshots `01-home.png` and `14-dashboard.png` in `docs/screenshots/prod/` for the current placement.

## Tasks
1. Build `ConsentSheet` (suggested: `apps/web/src/components/product/consent-sheet.tsx`) using `vaul` + design tokens; copy: one sentence on first-party-only analytics, Accept / Decline, privacy link.
2. Gate rendering on "never answered on this device"; mount once in the root layout (`apps/web/src/app/layout.tsx`) so marketing, auth, and app all share it.
3. Wire Accept → set consent cookie + flush SDK queue; Decline → marker only, SDK stays silent.
4. Add the consent toggle to `/settings` (`apps/web/src/app/(app)/settings/`), reusing the same state helpers.
5. Delete the old toast component and all imports; run `pnpm lint:strict` to catch strays.
6. Add vitest coverage for the three consent states of the SDK gate, and extend an e2e spec to assert the sheet appears once and never again after choice.
7. Re-capture affected screenshots (`cd apps/web && PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=http://localhost:3000 node scripts/capture-screenshots.mjs`; use the production URL post-deploy) and confirm no overlap remains.

## Self-Improvement Loop
1. Inspect the sheet on marketing, auth, and app routes at desktop and 375px width.
2. Identify the highest-impact gap (overlap, re-prompt, missed event, a11y issue).
3. Make the smallest coherent improvement.
4. Validate with the commands below plus a manual pass.
5. Document the result.
6. Repeat until acceptance criteria hold.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion`
- `pnpm test:e2e` (including the new consent spec)
- `cd apps/api && pytest -q tests/test_analytics.py` (collector contract unchanged)
- Manual: fresh browser profile → sheet appears once; accept → events flow (check Network tab for `/api/events`); decline → no events; DNT on → no events even after accept; keyboard: sheet is focus-trapped and Escape-dismissible.

## Acceptance Criteria
1. No route renders a persistent consent toast; the sheet appears at most once per device until answered.
2. Both choices persist across reloads and are changeable in `/settings`.
3. SDK sends zero events pre-consent, post-decline, or with DNT — proven by tests.
4. Re-captured screenshots show no content overlap; footer CTA on `/` is fully visible on first paint.
5. Sheet passes axe (no new violations) and honors `prefers-reduced-motion`.

## Documentation Requirements
- Update the Mission 25 section of README (consent banner → consent sheet, settings control).
- Closure note in `docs/screenshots/UI-REVIEW.md` against the "floating analytics toast" row; refresh affected PNGs.

## Git Workflow
`git status` first; keep the work to consent-related files. Review `git diff` before staging; commit as `fix(analytics): one-time consent bottom sheet replaces persistent toast [pack-04]` with what/why/validation/follow-ups. Push after gates pass.

## Production Guidance
Deployable: this is a self-contained, consent-strengthening change. Deploy only if Mission 02 gates and `pnpm test:e2e` are green and `bash scripts/railway-smoke.sh` passes post-deploy; otherwise batch with the next deployable mission.
