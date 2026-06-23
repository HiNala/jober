# Audit Remediation Task List

**Source:** `AUDIT_FINDINGS.md` (Passes 1–6)  
**Updated:** 2026-06-22  
**Legend:** ☐ open · 🔄 in progress · ✅ done · ⏭ defer

---

## Critical (fix first)

| # | Task | Status |
|---|------|--------|
| C1 | Worker `fill_context.py` — tenant-scoped profile/resume + fix sensitive column names | ✅ |
| C2 | Worker `job_context.py` — tenant-scoped resume skills join | ✅ |
| C3 | Batch enqueue tenant IDOR | ✅ |
| C4 | Batch skip/reorder tenant IDOR | ✅ |
| C5 | Batch pause/resume tenant ownership; tenant-scoped pause-all | ✅ |
| C6 | Stripe webhook — require secret in production; reject unsigned | ✅ |
| C7 | API auth fail-closed (no header fallback in prod) | ✅ |
| C8 | Web middleware — protect all `(app)` routes including `/admin` | ✅ |

## High

| # | Task | Status |
|---|------|--------|
| H1 | `uploadFetch()` + vault/library/jobs multipart uploads | ✅ |
| H2 | `ReviewPackageRead` + nested `cover_letter` schema | ✅ |
| H3 | SSRF `validate_outbound_url()` for discovery/extraction | ✅ |
| H4 | Stripe webhook `event.id` idempotency table | ✅ |
| H5 | Batch orchestrator Redis claim before Celery dispatch | ✅ |
| H6 | SSE same-origin proxy for run events | ✅ |
| H7 | API upload size limits (resumes/imports) | ✅ |
| H8 | Celery dispatch failure → rollback batch / surface error | ✅ |
| H9 | Batch preview N+1 — bulk-load prior runs | ✅ |
| H10 | Admin-only global queue concurrency patch | ✅ |

## Medium

| # | Task | Status |
|---|------|--------|
| M1 | Web lint — `use-media-query.ts`, `job-kanban.tsx` | ✅ |
| M2 | Search job links → `/queue?job={id}` | ✅ |
| M3 | `/kitchen-sink` 404 in production | ✅ |
| M4 | Index on `tenants.stripe_customer_id` | ✅ |
| M5 | Rate limit `POST /api/events` | ✅ |
| M6 | Auth rate limit — trusted proxy for `X-Forwarded-For` | ✅ |
| M7 | Health probes → `/readyz` (Railway/Docker) | ✅ |
| M8 | `fetchReadiness` parse `/readyz` checks | ✅ |
| M9 | Env templates sync (STRIPE, security vars) | ✅ |
| M10 | CI pip-audit + pnpm audit | ✅ |
| M11 | pnpm 10 in `Dockerfile.web.prod` | ✅ |
| M12 | Test cross-tenant batch enqueue blocked | ✅ |
| M13 | Hide notification toggles until implemented | ✅ |
| M14 | `global-error.tsx` | ✅ |
| M15 | Google OAuth — hide block when disabled | ✅ |
| M16 | `/readyz` reuse DB pool | ✅ |

## Low

| # | Task | Status |
|---|------|--------|
| L1 | Vault in main nav | ✅ |
| L2 | Review API real `resume_filename` | ✅ |
| L3 | Fill sandbox Windows timeout | ✅ |
| L4 | JsonLd static-data comment | ✅ |
| L5 | Notification settings → FormField pattern | ⏭ N/A (replaced with honest copy) |
| L6 | Central date formatter | ✅ |
| L7 | Web Sentry (optional) | ⏭ defer |

## Product / defer (needs product/legal decision)

| # | Task | Status |
|---|------|--------|
| P1 | Stripe Checkout + Pro upgrade flow | ☐ (user — last) |
| P2 | Legal pages — counsel review, remove draft banner | ☐ |
| P3 | Notification delivery implementation | ☐ |
| P4 | Demo workspace / sample data mode | ☐ |
| P5 | TUI stub menu cleanup | ✅ |
| P6 | Enforcing CSP (post report-only burn-in) | ✅ (env toggle `CSP_ENFORCE`) |
| P7 | Session idle timeout | ✅ |
| P8 | Automated CD workflow | ✅ (staging CD; needs `RAILWAY_TOKEN` secret) |

---

## Pre-deploy checklist

- [x] Run migration `s1t2r3i4p5e67_stripe_idempotency_and_index.py` (staging deploy 2026-06-23)
- [x] Set `TRUST_PROXY_HEADERS=true` on Railway API (staging + production)
- [ ] Set `STRIPE_WEBHOOK_SECRET` in production (requires Stripe Dashboard webhook — see below)
- [x] Commit + push audit remediation (`6a46500`)
- [x] Deploy staging (api/worker/web)
