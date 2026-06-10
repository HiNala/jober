# Mission 14: Responsive and Mobile Refinement

## Purpose
All 23 production screenshots are 1440×900; nothing below desktop has been verified. Marketing pages must convert on phones (where job seekers read links), and the app must at minimum be *usable* — not necessarily optimal — on tablet and phone. This mission verifies and fixes responsive behavior with explicit per-surface targets.

## Context From Audits
Application audit §11: marketing presumed-but-unverified responsive; the three-pane workspace shell (`components/workspace/`) is desktop-first with resizable panels and undocumented small-viewport behavior; no viewport-parameterized e2e. Mission 09's editorial layouts make this tractable: full-width pages collapse naturally; only run surfaces need bespoke handling.

## Scope
- **Targets:** marketing + auth: fully designed at 375/768/1024/1440. App editorial routes (dashboard, queue, discover, library, search, settings, analytics): usable at 768+, functional-with-scrolling at 375 (tables may scroll horizontally with sticky key columns). Run console `/runs/[id]`: at <1024 the canvas becomes a tabbed/stacked view rather than side panes — watching a run on a tablet must work; phone gets a read-only-leaning but functional layout.
- Fix overflow, tap-target (≥44px), and viewport-meta issues found.
- Mobile nav: collapsible nav becomes a drawer/sheet at small widths; ⌘K palette gets a visible trigger on touch devices (no keyboard).
- Add viewport-parameterized e2e smoke (key routes render without horizontal body overflow at 375/768).

## Out of Scope
- Native/mobile-app features, touch gestures beyond taps, PWA work.
- Redesigning desktop layouts.
- Pixel-perfect phone versions of admin/analytics (usable is the bar).

## Starting Checklist
1. Read `components/workspace/` breakpoint handling (any existing `useMediaQuery`/CSS breakpoints).
2. Check `app/layout.tsx` viewport meta.
3. Run the app locally and walk every route at 375/768/1024 via devtools; record findings in a table first — fix second.
4. Check `react-resizable-panels` docs/usage for conditional rendering patterns already in the code.
5. Review marketing pages at 375 (post-07/08 state).

## Tasks
1. Produce the findings table (`docs/polish-pack/notes/14_responsive_findings.md`): route × breakpoint × issue.
2. Marketing + auth fixes to fully-designed state (hero media scaling, bento stacking order, trust strip wrap, auth brand zone collapse).
3. App editorial routes: container/table strategies (sticky first column, horizontal scroll affordance, card-list fallback where tables are hopeless at 375).
4. Run console: implement the stacked/tabbed sub-1024 layout (Work | Canvas tabs), preserving checkpoint resolution actions.
5. Mobile nav drawer + touch palette trigger.
6. Add `e2e/responsive-smoke.spec.ts` with viewport projects asserting no horizontal overflow and visible primary actions on key routes.
7. Capture a small set of mobile screenshots (extend `capture-screenshots.mjs` with a 375×812 viewport option) into `docs/screenshots/mobile/`.

## Self-Improvement Loop
1. Inspect the next route × breakpoint cell from the findings table.
2. Identify the highest-impact breakage.
3. Make the smallest coherent improvement (prefer CSS/layout over conditional component forks).
4. Validate at all four breakpoints (fixes at 375 often break 768).
5. Update the table.
6. Repeat until all cells meet their per-surface target.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles`
- `pnpm test:e2e` (incl. new responsive spec)
- Manual: full route walk at 375/768/1024 in devtools + at least one real phone-sized check against the local network or production.

## Acceptance Criteria
1. Findings table fully resolved to the per-surface targets defined in Scope.
2. No route exhibits horizontal body overflow at 375 or 768 (e2e-proven).
3. Run console is operable on tablet (checkpoint resolve works at 768).
4. Mobile nav and touch palette trigger work.
5. Mobile screenshot set captured; all gates green.

## Documentation Requirements
- `docs/polish-pack/notes/14_responsive_findings.md` (final state).
- `docs/screenshots/mobile/` + README note in `docs/screenshots/README.md`.

## Git Workflow
`git status` first; commits per surface group; reviewed diffs; bodies with what/why/validation/follow-ups; push after gates.

## Production Guidance
Deployable after gates pass. After deploy, check `/` and `/signup` on a real phone against production, then `bash scripts/railway-smoke.sh`.
