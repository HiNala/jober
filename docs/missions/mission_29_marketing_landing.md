# Mission 29 — Marketing Site: Home / Landing

## Task list
- [x] Hero — headline, signup CTA, product visual, reduced-motion
- [x] How it works — 4 steps, human-in-the-loop honest copy
- [x] Value sections — time, ATS quality, tracking, live console
- [x] Social proof placeholder
- [x] Pricing teaser → `/pricing`
- [x] Footer — nav, legal stubs, contact
- [x] Conversion instrumentation — `feature.use` on CTAs; `page.view` via analytics provider
- [x] Performance + SEO — metadata, OG/Twitter, `sitemap.ts`, `robots.ts`
- [x] Design Council ≥18/20 (see `design-review.md`)

## Acceptance criteria
- [x] `/` renders full landing (not empty)
- [x] Primary CTAs route to `/signup` with analytics events
- [x] Footer links resolve (`/pricing`, `/privacy`, `/terms` stubs until M30)
- [x] `lint:strict` / `typecheck` / `build` green

## Analytics events (landing)
| Surface | Event | `feature` prop |
|---------|-------|----------------|
| Header | `feature.use` | `landing_header_signup` |
| Hero primary | `feature.use` | `landing_hero_signup` |
| Hero secondary | `feature.use` | `landing_hero_how_it_works` |
| Pricing teaser | `feature.use` | `landing_pricing_signup`, `landing_pricing_view` |
| Pricing stub | `feature.use` | `pricing_stub_signup` |

Signup funnel: `signup.start` fires on `/signup` mount (existing).

## Iteration clause
Interactive demo sandbox **deferred** — static product visual mock ships in v1.

**CI:** [run 27238599456](https://github.com/HiNala/jober/actions/runs/27238599456) (green on `7e00eed`).

## Mission 99
- [x] `trackMarketingCta` helper + vitest fixture (regression lock on `feature.use` shape)
- [x] `getSiteUrl` unit tests for sitemap/OG base URL resolution
- [x] Mobile header shows Pricing link; How it works visible from `md` up
- [x] README + `.env.example` document `NEXT_PUBLIC_SITE_URL`
- [x] Web gates green: `typecheck`, `lint:strict`, `build`, vitest
