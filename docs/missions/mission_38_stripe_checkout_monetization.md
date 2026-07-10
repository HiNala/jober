# Mission 38 — Stripe Checkout & Monetization Completion

> **Phase:** Perfection pack  
> **Depends on:** M15, M36 (pricing UI), audit P1  
> **Run Mission 99 after**  
> **Owner green-light:** Explicit — monetization is now in scope for perfection pack

## Purpose

Complete the **self-serve Pro path**: Stripe Checkout → webhook → entitlements → UI plan state → Grok-style unlock moment. No more “Coming soon” Pro dead ends when Stripe is configured.

## Context

Backend has plan entitlements, usage API, and Stripe webhook handler. Gaps:
- No Checkout Session creation endpoint / web client
- Webhook must require signing secret in production (audit C6 — verify held)
- Pricing page still waitlist-oriented
- Settings “Upgrade to Pro” incomplete
- Idempotent event application required

## Scope

### In scope
- API: create Checkout Session, Customer Portal session, webhook hardening
- Web: pricing + settings upgrade CTAs; success/cancel routes
- Entitlement refresh after success
- `UnlockModal` post-checkout celebration
- Tests: webhook signature, idempotency, plan upgrade, free limits still enforced
- Waitlist remains fallback when `STRIPE_SECRET_KEY` unset (honest)

### Out of scope
- Annual plans / multi-seat teams
- Usage-based metered billing beyond existing run limits
- Invoice customization beyond Stripe defaults

## Starting checklist
- [ ] Read billing routers, `PLAN_ENTITLEMENTS`, webhook handler
- [ ] Confirm Stripe products/prices exist or create in test mode
- [ ] List env vars: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO_MONTHLY`, success/cancel URLs

## Tasks

### 1. API
- [ ] `POST /api/billing/checkout-session` (auth required) → Stripe Checkout URL
- [ ] `POST /api/billing/portal-session` → Customer Portal for manage/cancel
- [ ] Webhook: require secret outside test; reject unsigned; idempotent `event.id` store
- [ ] Map `checkout.session.completed`, `customer.subscription.updated|deleted` → tenant plan
- [ ] Startup guard: production warns or fails if webhook secret missing when Stripe key set
- [ ] Entitlements recompute on plan change; usage endpoint reflects plan

### 2. Web
- [ ] `createCheckoutSession()` / `createPortalSession()` client helpers
- [ ] Pricing Pro card: **Upgrade** opens Checkout when Stripe configured; else waitlist
- [ ] Settings billing section: current plan, usage meters, Upgrade / Manage
- [ ] `/pricing/success` and `/pricing/cancel` (or query on `/pricing`) with analytics
- [ ] `UnlockModal`: Best apply limits · Priority support copy · Full analytics — CTA “Open dashboard”
- [ ] Feature flag or runtime config: `billing.stripe_enabled` derived from env

### 3. Copy & UX honesty
- [ ] Free limits explicit (batch size, monthly runs, LLM budget)
- [ ] Pro benefits explicit and true to entitlements
- [ ] Failed payment / past_due states in settings

### 4. Tests
- [ ] API unit: unsigned webhook rejected; signed upgrade applies once
- [ ] Entitlement gate: free batch limit still blocks
- [ ] Web vitest for plan card CTA branching
- [ ] Optional e2e with Stripe test clock / mocked checkout

## Validation
```bash
cd apps/api && pytest tests/test_billing_entitlements.py -q
# webhook signature tests as applicable
cd apps/web && pnpm typecheck && pnpm lint:strict
# manual Stripe test mode checkout on staging
```

## Acceptance criteria
- [ ] Free user can complete Stripe test Checkout → tenant `plan=pro` → raised limits
- [ ] Portal allows cancel/manage
- [ ] Unsigned webhooks never change plan in production-like config
- [ ] Pricing/settings never show fake “coming soon” when Stripe enabled
- [ ] Unlock modal Design Council ≥19/20

## Security
- Never trust client-reported plan
- Webhook signature mandatory in prod
- No price amounts solely from client

## Production guidance
- Create live Stripe webhook endpoint before prod cutover
- Set `STRIPE_WEBHOOK_SECRET` on Railway API
- Run one real $0 or test-clock verification on staging first
