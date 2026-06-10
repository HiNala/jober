# Mission 13: Accessibility Pass (App Routes Included)

## Purpose
Axe currently runs only against marketing routes (`apps/web/e2e/a11y-marketing.spec.ts`); the authenticated app — where users spend their time — has no automated a11y coverage and no documented keyboard path through the golden journey. This mission brings the whole product to a verifiable accessibility bar.

## Context From Audits
Application audit §10: gaps are app-route axe coverage, keyboard path through queue → run → checkpoint → submit, focus management in drawers/command palette, chart text alternatives, low-contrast outline icons (also flagged in UI-REVIEW). Assets in place: `@axe-core/playwright`, Base UI primitives, global `prefers-reduced-motion` support.

## Scope
- Extend e2e a11y coverage to core app routes: `/dashboard`, `/queue`, `/discover`, `/library`, `/search`, `/settings`, `/analytics`, `/runs/[id]` (fixture run), plus the consent sheet and ⌘K palette from Missions 04/09. Use the dev-auth bypass (`NEXT_PUBLIC_DEV_AUTH_BYPASS`) or a seeded session for authenticated specs.
- Fix all serious/critical axe violations; document any deliberate waivers.
- Keyboard: complete golden-path operation keyboard-only (import → batch → run console → resolve checkpoint → submit); fix traps, missing focus styles, unreachable controls; verify focus return on drawer/dialog/palette close.
- Charts (`components/analytics/charts/`): accessible names + data table or text summary alternative.
- Contrast: audit token pairs (especially low-contrast icons and muted text on dark surfaces) against WCAG AA; adjust tokens, not call sites.
- Live regions: run console SSE updates announce meaningfully (aria-live on status transitions, not on every event — avoid screen-reader spam).

## Out of Scope
- WCAG AAA targets; full screen-reader scripting of every page.
- Marketing pages beyond keeping their existing spec green (07–08 maintained it).
- Visual redesign (only token-level contrast corrections).

## Starting Checklist
1. Read `e2e/a11y-marketing.spec.ts` to reuse its harness pattern.
2. Check `playwright.config.ts` for auth/session handling in e2e.
3. `grep -rn "aria-live\|role=" apps/web/src/components/canvas apps/web/src/components/run-console` — current live-region usage.
4. Read token contrast pairs in `lib/design/tokens.ts`; list suspect combinations.
5. Try the keyboard-only golden path once and note every failure before fixing.

## Tasks
1. Create `e2e/a11y-app.spec.ts` covering the routes above; get a first violation report; triage into fix/waiver.
2. Fix violations root-cause-first (shared component > per-page patches).
3. Keyboard sweep: fix tab order, focus visibility (tokens for focus ring), drawer/palette focus trap + return, Escape behavior.
4. Chart alternatives: `aria-label` + visually-hidden summaries or toggleable data tables.
5. Contrast corrections at token level; re-run `check:motion` (motion and reduced-motion unaffected).
6. Live-region tuning in run console.
7. Document the keyboard map (extend the existing shortcuts list in README).

## Self-Improvement Loop
1. Inspect the next route with axe + keyboard + (spot) screen reader.
2. Identify the highest-impact violation.
3. Make the smallest coherent improvement (prefer shared-component fixes).
4. Validate by re-running the spec for that route.
5. Document fixes and waivers.
6. Repeat until specs pass with zero unwaived serious/critical violations.

## Validation
- `cd apps/web && pnpm test:e2e` (both a11y specs green)
- `pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion`
- Manual: keyboard-only golden path completes; spot-check with a screen reader (NVDA on this Windows host) on `/queue` and `/runs/[id]`.

## Acceptance Criteria
1. Axe e2e covers marketing + all core app routes; zero serious/critical violations without a written waiver in `docs/polish-pack/notes/13_a11y_waivers.md`.
2. Golden path is fully keyboard-operable; focus is always visible and correctly restored.
3. Charts have text alternatives; run-console updates are announced without spam.
4. Contrast fixes are token-level and documented.
5. All gates green.

## Documentation Requirements
- `docs/polish-pack/notes/13_a11y_waivers.md` (waivers + rationale).
- README: extended keyboard shortcut documentation.

## Git Workflow
`git status` first; commits per concern (specs → shared fixes → tokens → live regions); reviewed diffs; meaningful bodies; push after gates.

## Production Guidance
Deployable after gates pass — accessibility fixes are low-risk and user-positive. Smoke after deploy.
