# Changelog

## [Unreleased] — Perfection Pack 35–45 (2026-07)

### Design & marketing
- Design system 2030: AmbientCanvas, SkeletonStream, StatusLivePill, CommandComposer, SuggestionChips, ApproveSendBar, UnlockModal
- Near-black Hyperagent-grade tokens (`--live`, canvas ambient gradients)
- Dark-first marketing site with ambient hero, glass nav, honest Pro pricing
- Default theme: dark

### Monetization & auth
- Stripe Checkout + Customer Portal APIs; pricing/settings CTAs with waitlist fallback
- Post-checkout unlock modal; env docs for `STRIPE_*` / `NEXT_PUBLIC_STRIPE_ENABLED`
- Auth surfaces on 2030 tokens; Google button remains hidden when OAuth disabled

### Product loops
- Discovery fit explainability (`fit_reasons` chips)
- Resume variant generation (no-fabrication guards) + Document Studio “Tailor resume”
- Review package sticky ApproveSendBar; run console StatusLivePill
- Dashboard “Let’s get to work.” empty state + Discover primary nav CTA
- Mobile bottom tab bar (Home / Discover / Queue / Docs / More)

### Docs
- Missions 35–45, design-north-star-2030, residual notes on primary missions

## [Unreleased] — Polish Pack 01-28 (2026-06-10 → 2026-06-12)

### Foundation (Missions 01-03)

- Landed in-flight work cleanly; `main` stabilized
- Canonical quality gates documented and enforced (`docs/polish-pack/notes/gates.md`)
- Golden path verified local + production; fixture pipeline + fullstack e2e in CI

### UX & UI (Missions 04-10, 27-28)

- Consent bottom sheet replaces overlapping toast; analytics opt-in gated
- Empty/loading/error states designed as onboarding moments; zero dev copy
- Branded auth pages with trust strip and `AuthBrandPanel`
- Homepage hero centered with product preview; Linear-style nav + type scale
- Marketing subpages (features, how-it-works, pricing, FAQ, blog) rebuilt
- Workspace layout discipline: split-pane (ops-desk) only on `/runs/[id]`
- Command palette (⌘K) replaces bolted-on AI bottom bar
- Component tiering: marketing bento / workspace data panels / terminal surfaces
- Brand signature (`BrandSignature` mesh+grid) on hero + auth only
- Motion tokens + micro-interactions (Button, Input, Table, Tabs, Skeleton, charts)
- `prefers-reduced-motion` honored globally; `check:motion` gate enforced

### Flow completion (Missions 11-12, 15-17)

- Email delivery: SMTP + console backends; verification + password reset via Celery
- Forms & validation: uniform 422 mapping, pending states, no input loss
- Run console reliability: SSE reconnect from `Last-Event-ID`, 15s heartbeat, checkpoint conflict UI, end-state summary
- Discover → queue journey: seamless import/batch/dry-run flow; XLSX round-trip proven
- Document studio: friction-free letter cycle; honest stub/402 states; lock guarantee tested

### Hardening (Missions 18-21)

- API error contract: one envelope, no leaks, truthful `/readyz`, downstream mapping
- Auth/session hardening: cookie/CSRF/session matrix verified; lifecycle test-enforced
- Database hygiene: replay/drift/index/retention/backup all drilled
- Security & privacy validation: threat-model controls probe-verified; dependency audit

### Performance (Missions 22-23)

- Web performance: marketing LCP path cleaned; `ShellProviders`/`AppProviders` split; `dynamic()` on heavy chunks; bundle budget tightened to 2650 KB
- API & worker performance: latency baselines; pagination everywhere; Redis lock serialization

### Observability & testing (Missions 24-26)

- Observability: metrics truthful; 10 alert classes fire; correlation IDs web→API→worker; log questions answerable
- Critical path test coverage: web + api coverage maps; zero flakes; mutation spot-checks
- E2E expansion: 71 marketing e2e + 5 fullstack specs (core, recovery, studio, settings, auth) in CI

### Copy & brand (Mission 27)

- Voice guide + sweep table; P0 copy bugs eliminated
- Per-route metadata, JSON-LD, sitemap, robots, canonicals

### Security (Mission 21)

- API `SecurityHeadersMiddleware` (`X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`)
- Web report-only CSP and matching baseline headers in `next.config.ts`
- Security regression probes in `tests/test_security_controls.py` (Stripe signature, presigned TTL, tenant library/resume gates)
- Verification matrix: `docs/polish-pack/notes/21_security_matrix.md`

## [0.1.0] — 2026-06-10 — Launch

First production-ready release of Jober: assisted job-application autopilot with human-in-the-loop review.

### Highlights

- **Stack:** Next.js web, FastAPI api, Celery/Playwright worker, Postgres, Redis, S3-compatible storage
- **Railway:** Staging + production layout, migrate-on-deploy, health probes, smoke scripts
- **Ops:** Admin dashboard with budget, queue depth, circuit-breaker attention; webhook alerts
- **Safety:** Policy CI, redacted logs, production secret guards, review-before-submit default

### Deploy

See [docs/runbooks/deploy.md](docs/runbooks/deploy.md) and [docs/runbooks/launch-checklist.md](docs/runbooks/launch-checklist.md).

### Post-launch

Schedule a 7-day review: reliability (run success rate), LLM cost vs budget, signup → first batch funnel in admin analytics.
