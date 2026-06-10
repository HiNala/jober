# Mission 27: Content, Microcopy, and SEO Polish

## Purpose
Words are interface: the queue empty state said `make seed`, the settings dropzone shows wrong text, blog copy leaks CMS notes (UI-REVIEW P0 list). Beyond bug-level copy, every label, tooltip, confirmation, and error should sound like one confident product — and the marketing pages should be technically excellent SEO citizens so the positioning work actually gets found.

## Context From Audits
UI-REVIEW P0 quick wins: "fix user-facing copy bugs (queue empty state, settings dropzone)"; per-screen notes flag placeholder quotes and dev copy. Positioning audit §8 (messaging hierarchy), §17 (one-liner and pillars — copy must implement them verbatim-or-better), §21.2. SEO assets in place: `robots.ts`, `sitemap.ts`, `NEXT_PUBLIC_SITE_URL`-driven OG; depth unverified.

## Scope
- **Copy sweep, in-app:** every user-facing string in `apps/web/src` — empty states (re-verify post-Mission 05), buttons/labels (verb-first, consistent casing), tooltips, confirmations (state consequence: "Submit application to Acme — this cannot be undone"), toasts, error messages (human cause + next step), settings descriptions (incl. the **settings dropzone text bug**), checkpoint prompts. Build and apply a one-page voice guide (confident, precise, zero hype, no "oops").
- **Copy sweep, marketing:** align hero/pillars/FAQ to positioning audit §17/§18 wording; remove all placeholder/CMS-note leakage (blog); legal pages get a plain-language summary box at top (with "draft — not legal advice" honesty until counsel review).
- **SEO technical pass:** per-route unique `<title>`/description via Next metadata API; OG/Twitter images per marketing route (generated OG image route if cheap, static otherwise); canonical URLs; `sitemap.ts` covers all public routes and excludes app/auth/kitchen-sink; `robots.ts` correct; structured data (JSON-LD: `SoftwareApplication` on `/`, `FAQPage` on `/faq`, `BlogPosting` on posts); verify with a crawler-eye pass (fetch each route, inspect head).
- **Email copy** (Mission 11's templates) gets the same voice pass.

## Out of Scope
- New pages, blog posts, or content marketing.
- Keyword-stuffing or programmatic SEO pages.
- Visual changes (copy lengths must respect existing layouts; flag overflow to Mission 28 if a string needs design support).

## Starting Checklist
1. Extract the string inventory: `grep -rn "\"[A-Z][a-z].*\"" apps/web/src/components --include="*.tsx"` is too noisy — instead walk route-by-route in the browser with the voice guide, screenshotting offenders; check for any central strings/i18n file first (`ls apps/web/src/content`).
2. Read `apps/web/src/content/` (exists — likely marketing/blog content source) and the blog post files for CMS-note leakage.
3. Read `robots.ts`, `sitemap.ts`, and the root `layout.tsx` metadata export.
4. Re-read positioning audit §17–18 — the approved message set.
5. Find the settings dropzone component (`grep -rn "drop" apps/web/src/components/settings apps/web/src/components/vault`).

## Tasks
1. Write the voice guide (`docs/polish-pack/notes/27_voice_guide.md`, one page).
2. In-app sweep route-by-route; fix the two named P0 bugs first (queue empty state if anything remains post-05; settings dropzone).
3. Marketing copy alignment to §17/§18; blog/CMS-leak cleanup; legal summary boxes.
4. SEO: metadata per route, OG images, canonicals, JSON-LD, sitemap/robots verification; validate JSON-LD with a schema validator and OG with a preview tool (or manual head inspection if tooling is unavailable — note the limitation).
5. Email template voice pass.
6. Re-capture all screenshots (`cd apps/web && PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=<env> node scripts/capture-screenshots.mjs`) and proof-read the captures end to end — reading screenshots catches what code review misses.

## Self-Improvement Loop
1. Inspect the next route's strings against the voice guide in a real browser.
2. Identify the highest-impact off-voice, unclear, or buggy string.
3. Make the smallest coherent rewrite.
4. Validate (gates — e2e uses testids so copy changes are safe per Mission 26; re-read in browser).
5. Log in the sweep table.
6. Repeat until a full product read-through surfaces zero off-voice strings.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build`
- `pnpm test:e2e`
- Head inspection of every public route (title/description/OG/JSON-LD present and unique).
- Full screenshot re-capture proof-read.

## Acceptance Criteria
1. Both named P0 copy bugs fixed; zero dev/CMS/placeholder copy anywhere (grep + screenshot proof).
2. Marketing copy implements the positioning one-liner and pillars.
3. Every public route has unique metadata, valid JSON-LD where specified, correct sitemap/robots/canonical state.
4. Voice guide exists; product read-through clean.
5. All gates green.

## Documentation Requirements
- `docs/polish-pack/notes/27_voice_guide.md` + sweep table.
- Refresh `docs/screenshots/` set; closure notes in UI-REVIEW for copy rows.

## Git Workflow
`git status` first; commits: P0 fixes → in-app sweep → marketing → SEO → email; reviewed diffs; bodies with what/why/validation/follow-ups; push after gates.

## Production Guidance
Deployable after gates pass — copy and metadata are low-risk, high-polish. Deploy, then fetch production routes to confirm metadata rendered (SSR), and re-capture prod screenshots; `bash scripts/railway-smoke.sh`.
