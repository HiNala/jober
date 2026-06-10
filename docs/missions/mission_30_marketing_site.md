# Mission 30 — Marketing Site: Features, Pricing, Legal & SEO

## Task list
- [x] **Features page** (`/features`) — discovery, letters, live canvas, analytics, safety posture
- [x] **Pricing page** — Free/Pro entitlements mirroring `PLAN_ENTITLEMENTS`; billing FAQ; BYOK vs managed LLM
- [x] **How it works / FAQ** — `/how-it-works` depth + `/faq` with honest auto-submit/CAPTCHA/privacy answers
- [x] **Legal & compliance** — Privacy, Terms, Acceptable Use (draft banners; legal review required before launch)
- [x] **Cookie/consent** — banner links to Privacy `#cookies-and-analytics`; decline gates SDK + API
- [x] **SEO** — per-page metadata/OG, FAQ JSON-LD, sitemap, robots, canonical URLs
- [x] **Conversion paths** — page-scoped `feature.use` CTAs; UTM session persistence into signup funnel
- [x] **Consistency** — shared `MarketingShell`, tokens, motion, `marketingMetadata()` helper
- [x] **Blog scaffold** — `/blog` + `/blog/[slug]` from `content/blog/posts.ts`

## Acceptance criteria
- [x] All marketing routes responsive; metadata/OG per page; sitemap includes blog slugs
- [x] Pricing reflects API entitlements (5/20/$5 Free; 100/500/$50 Pro)
- [x] Legal pages linked from footer; draft review banners visible
- [x] Consent decline = no client events; API `tracking_suppressed` unchanged from M25
- [x] Design Council ≥18/20 (see `design-review.md`)
- [x] `lint:strict` / `typecheck` / `build` / vitest green

## Analytics CTA keys (sample)
`features_cta_signup`, `pricing_free_signup`, `faq_cta_signup`, `how_it_works_cta_signup`, `blog_header_signup`, etc.

**CI:** [run 27241226129](https://github.com/HiNala/jober/actions/runs/27241226129) (green on `470104d`).

## Iteration clause
Blog/changelog scaffold shipped.

## Mission 99
- [x] CI green after UTM SDK follow-up commit (`470104d`)
- [x] `marketingMetadata` vitest for canonical/OG URLs
- [x] Footer + pricing teaser aligned with live `/pricing` entitlements
- [x] Web gates: `typecheck`, `lint:strict`, `build`, vitest

**M99 CI:** [run 27247296231](https://github.com/HiNala/jober/actions/runs/27247296231) (green on `b6c8e74`).

### M99 pass 2
- [x] Stale “Mission 30” copy removed from social proof + pricing FAQ
- [x] `marketingSitemapPaths` regression fixture for public routes + blog slugs
- [x] `readPersistedUtmParams` test — signup funnel attribution after navigation
- [x] Web gates re-run: typecheck, lint:strict, build, vitest (51 tests)

**M99 pass 2 CI:** [run 27247909805](https://github.com/HiNala/jober/actions/runs/27247909805) (green on `5283f04`).

## Notes
- Legal text is **draft** — requires counsel sign-off before public launch.
- Pro Stripe checkout not wired on web yet; pricing copy is honest about “coming soon”.
