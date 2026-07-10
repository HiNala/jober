# Mission 36 — Marketing Site v3 (Hero, Sales, Conversion 2030)

> **Phase:** Perfection pack  
> **Depends on:** M35  
> **Run Mission 99 after**

## Purpose

Rebuild the public funnel so Jober looks like a **premium 2030 product** — dark Hyperagent/Grok elegance, not generic light AI SaaS. Hero, features, how-it-works, pricing, FAQ, and conversion paths must sell the real product: perfect job lists, tailored docs, filled forms, **you hit Approve**.

## Context

M29–M30 and polish 07–08 shipped a Linear-style light hero and solid IA. Gaps: still reads “template SaaS”; Pro checkout incomplete (honest waitlist only); product preview underuses live console magic; no cinematic brand moment comparable to Grok unlock / Hyperagent canvas ambient.

## Scope

### In scope
- Dark-first marketing shell (nav, footer, pages)
- Hero redesign with ambient canvas + looping product proof
- Differentiator bento (fill-diff + review-before-submit dominant)
- Pricing page ready for Stripe (M38 wires checkout; this mission UI + honest CTAs)
- Sales copy hierarchy from positioning audit
- Generated ambient/OG art assets under `apps/web/public/images/`
- Mobile marketing perfection (375+)
- SEO metadata, JSON-LD, sitemap refresh
- Analytics CTA events retained/expanded

### Out of scope
- Stripe session API (M38)
- App shell (M39)
- Legal counsel rewrite (keep draft banners until counsel; polish layout only)

## Starting checklist
- [ ] Read north star §2–3 and positioning audit §17–18
- [ ] Inventory `components/marketing/*`
- [ ] Confirm current plans in `lib/marketing/plans.ts` match API entitlements

## Tasks

### 1. Marketing shell
- [ ] Dark nav: larger type, fewer items, glass/blur optional, Start free border-beam
- [ ] Footer: product / company / legal columns; trust line
- [ ] Mobile full-screen nav sheet (not cramped hamburger list)

### 2. Home hero
- [ ] Headline hierarchy: “Apply to every job on your list — at your quality bar.”
- [ ] Subhead emphasizes **You review and submit. Always.**
- [ ] Dual CTA: Start free · Watch how it works (scroll or `/how-it-works`)
- [ ] Center or split: `AmbientCanvas` + `HeroRunPreview` / code-built product mock (prefer live-looking UI over static PNG)
- [ ] Trust strip immediately below hero
- [ ] Optional ambient image backdrop (generated) at low opacity

### 3. Mid-funnel
- [ ] Differentiator bento: 2× cell for review + fill-diff mock; supporting cells for discover, vault, recovery
- [ ] How-it-works 5-step: Import/discover → Tailor resume+letter → Fill forms → Verify → **You approve**
- [ ] Founder proof with real numbers (155 leads story); no fake testimonials
- [ ] Pricing teaser + FAQ teaser + final CTA band

### 4. Subpages
- [ ] `/features` — same visual language; deep links into product concepts
- [ ] `/how-it-works` — scroll-linked stepper; dominant review step
- [ ] `/pricing` — Free concrete limits; Pro CTA slot for Checkout (fallback waitlist if flag off)
- [ ] `/faq` — objection order: bot? ATS flag? data? pricing?
- [ ] Blog index: editorial dark cards (no CMS required)

### 5. Assets & SEO
- [ ] Place hero ambient + OG image in `public/images/`
- [ ] Update `opengraph-image` / metadata helpers
- [ ] JSON-LD SoftwareApplication + FAQPage accurate

### 6. Conversion instrumentation
- [ ] Preserve `feature.use` + UTM persistence
- [ ] Add events: `landing_hero_watch`, `pricing_pro_checkout_click`, `pricing_pro_waitlist_submit`

## Validation
```bash
cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm build
pnpm exec playwright test e2e/a11y-marketing.spec.ts e2e/responsive-smoke.spec.ts e2e/mobile-smoke.mobile.spec.ts
# screenshot pack
PLAYWRIGHT_BASE_URL=http://localhost:3000 node scripts/capture-screenshots.mjs
```

## Acceptance criteria
- [ ] `/` dark 2030 hero; no generic light-template feel
- [ ] All marketing routes pass a11y + responsive smoke
- [ ] Pro CTA is either Checkout (when enabled) or waitlist — never disabled dead button labeled “Coming soon” with equal weight to Free
- [ ] Design Council ≥19/20 marketing surfaces
- [ ] Screenshots updated under `docs/screenshots/`

## Copy checklist
| Surface | Must say |
|---------|----------|
| Hero | Quality bar + human approve |
| Trust | No CAPTCHA bypass · Encrypted vault · First-party analytics |
| Pricing | Concrete Free limits; Pro benefits honest |
| FAQ | Differentiates from auto-apply bots |

## Production guidance
- Deploy with M35 tokens
- Verify CWV after deploy (LCP image priority, font display)
