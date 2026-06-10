# Mission 07: Homepage Hero and Landing Page Implementation

## Purpose
The landing page is correct but indistinguishable from "hundreds of AI SaaS landings" (UI-REVIEW 01). The positioning audit defines the target structure (§18): a hero that *shows the product working*, the differentiator visually elevated, honest proof. This mission implements it on `/`.

## Context From Audits
Positioning audit §7 (issues), §8 (messaging hierarchy), §18 (recommended structure + **binding owner direction: Linear-style hero — centered copy with the product preview centered beneath it, larger navigation text and a larger, more confident type scale overall, focused calm composition**), trust strip, 2× differentiator cell, stepper teaser, honest proof, pricing teaser, objection-ordered FAQ teaser, final CTA. UI-REVIEW 01 specifics: tighten H1 tracking (-0.02em, weight 600), mono uppercase eyebrow, radial gradient behind mockup, stagger children 50ms, mockup float animation, replace placeholder testimonials.

## Component Sourcing
Fetch and study best-in-class patterns before building: an animated hero treatment from **21st.dev**, hero/marketing blocks from **v0**, and comparable libraries (Aceternity UI, Magic UI, shadcn ecosystem) for border-beam CTAs, animated grids/gradients, and bento cells. Rules: **adapt, never paste** — every sourced pattern is rebuilt on `lib/design/tokens.ts` + `lib/design/motion.ts`, license-checked, and bundle-budget-checked; no new heavy animation dependency without measuring `pnpm check:bundles`. If browsing is unavailable in the execution environment, state that in the mission notes and implement from the named patterns' well-known structures.

## Scope
- Rebuild `/` (`apps/web/src/app/page.tsx` + `components/marketing/`) to the §18 structure using existing design/motion tokens.
- Produce the hero product visual: a looping capture (video/animated frames) of the run console; source it from a local fixture run recorded via the screenshot script or a screen capture — an animated-typed terminal component is an acceptable fallback if a capture pipeline is too heavy.
- Elevate "review before submit" into the large bento cell with a fill-diff visual.
- Replace placeholder social proof with the founder story + real run stats; remove fake testimonials entirely.
- Trust strip (shared component from Mission 06).
- Motion: staggered hero entrance, mockup float, all via `lib/design/motion.ts` tokens (must pass `pnpm check:motion`), reduced-motion safe.

## Out of Scope
- Other marketing pages (Mission 08).
- New claims, pricing changes, or testimonial fabrication — if real proof doesn't exist, the section shrinks honestly.
- Heavy animation libraries beyond what's installed; keep bundle budgets green.

## Starting Checklist
1. Read `apps/web/src/app/page.tsx` and every component it imports from `components/marketing/`.
2. Read `lib/design/motion.ts` and `docs/architecture/motion.md` for the sanctioned vocabulary.
3. Check `pnpm check:bundles` budget config (`scripts/check-bundle-budget.mjs`) — the hero media must fit.
4. Review `docs/screenshots/prod/01-home.png` against positioning audit §18 section by section.
5. Confirm CTA analytics events (`feature.use`) and UTM persistence code paths so the rebuild preserves them.

## Tasks
1. Implement the section sequence from §18 top-to-bottom; reuse/extend marketing components rather than forking new one-offs.
2. Hero (Linear-style, per owner direction): **centered** composition — mono uppercase eyebrow, large tightened H1, one-line subhead, dual CTA (Start free → `/signup`, Watch a run → anchor to the differentiator block or `/how-it-works`) — with the **product preview (run-console loop) centered directly beneath the copy**, brand-signature glow/gradient behind it. Increase marketing nav text size and weight presence (fewer, larger, focused items); audit the whole page's type scale upward to match.
3. Build the run-console loop asset (source animated-hero techniques per Component Sourcing); lazy-load it; provide poster frame + reduced-motion static fallback.
4. Differentiator bento with fill-diff mock (use redacted real markup, not lorem).
5. Proof section: founder story block; delete placeholder quotes.
6. Wire CTA events; verify UTM → signup attribution still records.
7. SEO/meta: confirm `NEXT_PUBLIC_SITE_URL`-driven OG tags, `robots.ts`, `sitemap.ts` still correct after restructure.
8. Re-capture `01-home.png`; run the 5-second test from positioning audit §21.1 (a person unfamiliar with Jober reads hero+strip and states what it does).

## Self-Improvement Loop
Screenshot-driven — judge like a designer, not a diff:
1. Re-capture the page (`cd apps/web && PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=http://localhost:3000 node scripts/capture-screenshots.mjs` against a local `pnpm build && pnpm start`).
2. Compare section-by-section against §18 and the north stars (Linear's centered focus, Hyper Agents' live-product hero, 21st.dev's component depth) at 1440/1024/375 widths; identify the highest-impact element that still reads generic.
3. Make the smallest coherent improvement.
4. Validate (gates, bundle budget, reduced-motion, manual).
5. Document and keep the before/after captures.
6. Repeat until acceptance criteria hold and a fresh capture reads distinctly Jober, not template.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles`
- `pnpm test:e2e` (marketing a11y spec must stay green)
- Manual: LCP sanity in devtools (hero media must not tank it — target <2.5s on Fast 3G-throttled desktop emulation is aspirational; record the number); reduced-motion mode shows static hero; consent sheet (Mission 04) does not overlap final CTA.

## Acceptance Criteria
1. `/` matches the §18 structure: centered Linear-style hero with the product preview centered beneath the copy; larger nav/type scale applied page-wide; the differentiator is visually dominant.
2. Hero shows the product working (loop or animated terminal), with poster + reduced-motion fallbacks; any sourced pattern is token-adapted and license-noted.
3. Zero placeholder testimonials or fake proof anywhere on `/`.
4. `check:motion` and `check:bundles` pass; marketing axe spec passes.
5. CTA/UTM analytics verified end-to-end (event row lands in Postgres locally).
6. Design Council gate ≥18/20; UI-REVIEW row 01 closed with re-captured screenshot.

## Documentation Requirements
- Refresh `docs/screenshots/prod/01-home.png` + closure note in UI-REVIEW.
- Record the 5-second-test result in `docs/polish-pack/notes/07_landing_notes.md`.

## Git Workflow
`git status` first; commit per section where possible (`feat(marketing): bento hero with live run loop [pack-07]`); review diffs; bodies cover what/why/validation/follow-ups; push after gates.

## Production Guidance
Deployable once gates + e2e pass — high-visibility but logic-free. Deploy during a low-traffic window, re-run `bash scripts/railway-smoke.sh`, and re-capture production screenshots the same day.
