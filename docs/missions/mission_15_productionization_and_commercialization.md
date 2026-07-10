# Mission 15 — Productionization & Commercialization Readiness

## Task list

### Auth & multi-tenancy
- [x] Dev-header auth (`X-Jober-Tenant-Id` / `X-Jober-User-Id`) + Clerk JWT path; `AuthMiddleware` on `/api/*`
- [x] `tenant_id` on core entities; repository-level tenant scoping
- [x] Cross-tenant isolation tests (`test_tenant_isolation.py`)
- [x] Per-tenant MinIO key prefixes (`tenants/{id}/…`)

### Billing
- [x] Plan entitlements (Free vs Pro) with batch size + monthly run gates
- [x] Stripe webhook router (`/api/webhooks/stripe`)
- [x] Usage dashboard API (`GET /api/billing/usage`)

### Policy & compliance
- [x] Settings policy API with usage guidance and `auto_submit` disclosure
- [x] Tenant-scoped export / delete / purge; audit log on sensitive actions
- [x] `docs/architecture/product.md` positioning note

### Managed workers & deploy
- [x] Worker `BROWSERLESS_URL` CDP connect for headless servers; headed local mode unchanged
- [x] Config hooks for Railway/staging (`jober_env`, Stripe, Clerk env vars in `config.py`)

## Acceptance criteria
- [x] Two tenants cannot read each other's jobs or runs (tested)
- [x] Free plan blocks batch > 5 items; Pro allows 6+
- [x] Export/delete scoped per tenant
- [x] Headless server path via browserless URL; local headed default preserved

## Mission 99
- [x] Run-console tenant isolation + Stripe upgrade fixture tests
- [x] Full gates: API/worker pytest, web lint/typecheck/build, policy suite, `detect-secrets`
- [x] Design Council 19/20 in `design-review.md`
- [x] Pushed to `origin/main` at mission boundary

---

## Residual perfection (2026-07) → Mission 38

Build mission closed entitlements + webhook **hooks**, not full self-serve monetization.

| Residual gap | Owner mission |
|--------------|---------------|
| Stripe Checkout Session API + web CTAs | **M38** |
| Customer Portal for manage/cancel | **M38** |
| Webhook signing required in production (verify held) | **M38** + audit C6 |
| Pricing “Coming soon” / waitlist-only Pro card | **M36** UI + **M38** wire |
| Unlock / post-upgrade experience | **M38** |
| Usage meters + upgrade in Settings | **M38** + **M39** shell |

Do **not** re-open M15 task checkboxes; track residual work only in M38 acceptance criteria.
