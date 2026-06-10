# Mission 28: Brand Layer, Motion, and Micro-Interaction Finishing Pass

## Purpose
This is the "every little detail" mission: finalize the single brand signature, sweep the entire product (inside and out) for micro-interaction quality — hover, focus, press, drag, transition, success/failure feedback — and bring sourced best-in-class component patterns (21st.dev, v0, and peer libraries) into the token system. The bar: a designer fluent in Linear, Hyper Agents, Figma, and 21st.dev finds nothing that reads default.

## Context From Audits
UI-REVIEW themes 1 (brand layer: mesh gradient hero, animated grid, or glass agent-orb — pick **one**) and 4 (motion with purpose: staggered hero entrance, LIVE badge pulse, skeleton loaders, chart draw-in). Positioning audit §19.6. Owner design direction (recorded 2026-06-10): **Linear-style focus** — generous type scale, larger navigation text, centered product preview in the hero, calm surfaces, elegant restrained animation; gorgeous modern UI with micro-interactions everywhere they communicate state. Infrastructure: `lib/design/motion.ts` + `pnpm check:motion`, `tw-animate-css`, Missions 07–10/17 already moved major surfaces.

## Scope
- **Brand signature finalization:** choose the one signature (per UI-REVIEW theme 1), implement it as a reusable component/token set, apply to marketing hero + auth brand zone only; remove any placeholder treatment from Mission 06.
- **Component sourcing:** browse 21st.dev, v0.app, and comparable high-quality sources (Aceternity UI, Magic UI, shadcn ecosystem) for: animated hero treatment, border-beam/glow CTA accent, bento cell patterns, stepper connector, skeleton shimmer, chart draw-in. **Adapt, never paste:** every import is rewritten onto our tokens/motion vocabulary, license-checked, and dependency-audited (no new heavy animation deps without a bundle-budget check). If browsing is unavailable in the execution environment, implement from the named patterns' well-known structures and record the limitation.
- **Type and nav scale (Linear direction):** audit the global type scale — body, nav items, section headings; increase nav text and key headings toward the larger, more confident scale the owner requested; verify against all breakpoints (Mission 14 targets still hold).
- **Micro-interaction sweep, full product:** every interactive element gets deliberate hover/focus/active/disabled treatment from one system; buttons press; cards lift only where clickable; inputs focus with the token ring; toasts enter/exit on motion tokens; tab switches animate indicator; table row hover; drag affordances on resizable panels; LIVE badge pulse; chart draw-in on `/analytics`; skeleton shimmer unified. Catalog and fix surface-by-surface.
- **Reduced motion:** every addition has a reduced-motion behavior; `check:motion` and the a11y suite stay green.

## Out of Scope
- New pages or features; layout/structure changes (done in 07–10).
- More than one brand signature; animation for its own sake (every motion names the state change it communicates).
- Heavy animation runtimes (framer-motion adoption only if a sourced pattern requires it AND budgets absorb it — otherwise CSS/`tw-animate-css`).

## Starting Checklist
1. Re-read UI-REVIEW themes 1/4 and the owner direction note above.
2. Read `lib/design/motion.ts`, `docs/architecture/motion.md`, and `scripts/check-motion-tokens.mjs` (what the checker enforces).
3. Walk the entire product (marketing → auth → all app routes) recording a micro-interaction inventory: element × state × current treatment.
4. Check bundle headroom (`pnpm check:bundles`) before sourcing anything.
5. Collect the sourcing shortlist with URLs/licenses in the notes file before implementing.

## Tasks
1. Brand signature: prototype the chosen treatment, apply to hero + auth, re-capture and compare against the north stars side by side.
2. Sourcing round: implement the adapted patterns (hero animation, CTA accent, skeleton shimmer, stepper, chart draw-in), each token-native and license-recorded.
3. Type/nav scale pass with breakpoint verification.
4. Micro-interaction sweep from the inventory, worst-first; promote repeated treatments into the component families (Mission 10's system) so they're defaults, not overrides.
5. Performance trace on the heaviest surfaces (hero, analytics) — compositor-only animation (Mission 22 bar).
6. Full screenshot re-capture (desktop + mobile sets); side-by-side review against the previous capture and the north-star references; iterate.

## Self-Improvement Loop
This mission is explicitly screenshot-driven:
1. Re-capture the surface (`cd apps/web && PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=http://localhost:3000 node scripts/capture-screenshots.mjs` against a local prod build).
2. Compare against the north-star bar (Linear/Hyper/21st.dev) and the inventory; identify the highest-impact detail that still reads default.
3. Make the smallest coherent refinement.
4. Validate: `check:motion`, `check:bundles`, a11y spec, reduced-motion manual pass.
5. Update the inventory and capture set.
6. Repeat until a full product walkthrough yields no default-reading element, then stop — restraint is part of the bar.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles`
- `pnpm test:e2e` (a11y suites green — focus states changed)
- Performance traces on hero + analytics (no main-thread animation jank).
- Before/after screenshot sets archived.

## Acceptance Criteria
1. One brand signature lives on marketing + auth; nothing else uses it; placeholder treatments removed.
2. Sourced patterns are adapted to tokens, license-documented, and within bundle budgets.
3. Nav/type scale reflects the Linear-style direction at all breakpoints.
4. Micro-interaction inventory 100% deliberate (no browser-default focus/hover anywhere); all motion token-driven and reduced-motion safe.
5. Design Council gate ≥18/20 on every surface; full re-captured screenshot set committed; all gates green.

## Documentation Requirements
- `docs/polish-pack/notes/28_sourcing_and_microinteractions.md` (sourcing shortlist with licenses, inventory, before/after).
- Update `docs/architecture/motion.md` and `design-tokens.md` with new vocabulary.
- Refresh `docs/screenshots/` (desktop + mobile) and UI-REVIEW closure notes for themes 1/4.

## Git Workflow
`git status` first; commits: signature → sourced patterns (one per pattern) → type scale → sweep batches; reviewed diffs; bodies note the sourced inspiration + license where applicable; push after gates.

## Production Guidance
Deployable after gates pass. This is the most visible deploy of the pack — deploy in one coherent release (not piecemeal), re-capture production screenshots the same day, and run the 5-second test once more on the live hero. `bash scripts/railway-smoke.sh` after.
