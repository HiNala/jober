# Mission 08: Marketing Subpages Polish (Features, How-it-works, Pricing, FAQ, Blog)

## Purpose
The marketing subpages share the "default shadcn card grid" problem: equal-weight cards, no hierarchy, no product proof (UI-REVIEW 02–06). This mission carries the Mission 07 visual language through the rest of the funnel so the site reads as one designed product, not a template.

## Context From Audits
UI-REVIEW per-screen rows: 02-features (bento with 2×2 "Live-watch canvas" cell + embedded loop, mono spec labels), 03-how-it-works (stepper with gradient connector, step 3 dominant with mini browser chrome, scroll-highlight), 04-pricing (large price numeral, feature table below cards, Pro → inline waitlist capture, border-beam on Free CTA), 05-faq (two-column category split, chevron rotation + height transition, anchor links to legal), 06-blog (minimal is fine pre-launch — typography pass only). Positioning audit §12.4 (Pro dead card wastes intent) and §16 ("coming soon" reads as abandonment).

## Scope
- `/features`: bento layout, hero cell with the run-console loop from Mission 07 (reuse the asset), mono spec sublabels, deep links into `/how-it-works` anchors.
- `/how-it-works`: 4-step stepper, step 3 visually dominant, scroll-driven highlight via IntersectionObserver, FAQ accordion below.
- `/pricing`: typographic price treatment, shared feature comparison table (mirrors API plan limits in `routers/billing.py` — Free 20 runs/mo / 5 batch / $5 LLM; Pro 500/100/$50), **Pro waitlist email capture** replacing the dead card (store via existing analytics event or a minimal `waitlist` mechanism — prefer the lightest thing that records an email + consent; if no backend exists, an explicit discovery task decides between an `AnalyticsEvent`-based capture and a tiny table).
- `/faq`: category columns (Product | Trust & billing), open/close affordance animation, anchors into `/privacy` and `/terms`.
- `/blog`: typography/spacing pass only.
- Footer + nav consistency across all marketing routes.

## Component Sourcing
Same rules as Mission 07: pull pattern references from 21st.dev, v0, Aceternity/Magic UI (bento grids, border-beam, stepper connectors, accordion transitions), rebuild on tokens/motion vocabulary, check licenses and bundle budgets. Carry Mission 07's larger nav/type scale through every subpage so the funnel reads as one product.

## Out of Scope
- Stripe checkout (explicitly deferred; waitlist is the sanctioned alternative).
- CMS, new blog posts, new FAQ content beyond reordering/categorizing.
- New feature claims.

## Starting Checklist
1. Read each route under `apps/web/src/app/{features,how-it-works,pricing,faq,blog}/` and shared `components/marketing/`.
2. Confirm plan limits in `apps/api/src/jober_api/routers/billing.py` so pricing copy stays truthful.
3. Inventory which Mission 07 components (bento cell, trust strip, section header) are reusable here.
4. Check `pnpm check:bundles` margins before adding media to `/features`.
5. Decide and record the waitlist storage mechanism (discovery task above).

## Tasks
1. Features bento + embedded loop + spec labels + deep links.
2. How-it-works stepper with dominant step 3 and scroll highlight (honor reduced motion: highlight without animation).
3. Pricing rework incl. waitlist capture wired end-to-end (submission → stored → confirmation state → duplicate-submission handled).
4. FAQ restructure + animation + anchors.
5. Blog typography pass.
6. Cross-page QA: consistent section rhythm, heading scale, CTA styles; sitemap/OG still correct.
7. Re-capture screenshots 02–06; extend marketing e2e route list (`apps/web/e2e/marketing-routes.ts`) if any route changed paths/anchors.

## Self-Improvement Loop
Screenshot-driven, like Mission 07:
1. Re-capture all marketing pages (`cd apps/web && PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=http://localhost:3000 node scripts/capture-screenshots.mjs`).
2. Compare each capture against its UI-REVIEW row and the north stars at 1440/768/375; identify the highest-impact element that still reads template-y.
3. Make the smallest coherent improvement.
4. Validate (gates + manual + reduced motion).
5. Document with before/after captures.
6. Repeat until every row's issues are closed and the funnel reads as one designed product.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles`
- `pnpm test:e2e` (marketing a11y across all routes)
- Manual: waitlist capture round-trip (submit, verify storage, resubmit dedupe); pricing numbers vs `billing.py` limits; anchor links land correctly; reduced-motion pass.

## Acceptance Criteria
1. UI-REVIEW rows 02–06 closed with re-captured screenshots.
2. Pricing shows no dead card: Pro captures intent via working waitlist; displayed limits match the API source of truth.
3. All marketing routes pass axe and keep bundle budgets green.
4. Visual language is continuous with the Mission 07 homepage (same families, spacing, type scale).
5. Design Council gate ≥18/20 per reworked page.

## Documentation Requirements
- Closure notes + refreshed PNGs (02–06) in `docs/screenshots/`.
- Document the waitlist mechanism (storage, retrieval, privacy note) in README's marketing section and `docs/polish-pack/notes/08_waitlist.md`.

## Git Workflow
`git status` first; one commit per page plus one for shared components (`feat(marketing): pricing waitlist capture [pack-08]` etc.); review diffs; meaningful bodies; push after gates.

## Production Guidance
Deployable after gates pass. The waitlist capture is the only behavioral change — verify it in production immediately after deploy (submit a test email, confirm storage), then `bash scripts/railway-smoke.sh`.
