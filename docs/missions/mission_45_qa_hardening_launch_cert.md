# Mission 45 — Integration Hardening, Full QA & Launch Certification

> **Phase:** Perfection pack (capstone)  
> **Depends on:** M35–M44, polish 29–30 if still open  
> **Run Mission 99 after (final)**

## Purpose

Ship the **absolute best version of Jober**: all integrations healthy, no known critical bugs, zero lint/type debt in CI, performance budgets met, security/privacy verified, docs/runbooks current, release tagged and deployable.

## Context

M34 and polish 30 aimed at launch. Perfection pack changes surface area significantly. This mission re-certifies the whole product as a 2030-grade commercial app.

## Scope

### In scope
- Full gate matrix (API, worker, web, e2e, policy, secrets)
- Bug bash of golden path + billing + auth + admin
- Fix residual defects found in M35–44
- Performance budgets (web + API)
- Security checklist re-run (threat model)
- Legal draft status explicit (block public marketing claims if counsel pending)
- CHANGELOG + version tag `v1.0.0-perfection` or `v0.2.0`
- Screenshot pack refresh (prod + mobile)
- Operator README / runbook links
- Mission index status green

### Out of scope
- New features not required to close defects
- Scope creep from “nice ideas” during bug bash

## Starting checklist
- [ ] Collect open items from M35–44 notes + AUDIT residual P2 legal
- [ ] Ensure staging has Stripe test, Google OAuth, SMTP, Browserless

## Tasks

### 1. Quality gates (must all pass)
```bash
# API
cd apps/api && ruff check src tests && mypy src && pytest -q
# Worker
cd apps/worker && ruff check src tests && mypy src && pytest -q
# Packages as in CI
# Web
cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundle
# Secrets
detect-secrets scan --baseline .secrets.baseline
# E2E (stack up)
cd apps/web && pnpm exec playwright test
# Policy
# (CI policy job / make policy)
```

### 2. Integration matrix

| Integration | Verify |
|-------------|--------|
| Postgres + migrations | upgrade from prior prod revision |
| Redis sessions/queue | auth + celery |
| MinIO/S3 | upload resume, letter, screenshot |
| SMTP/email | verify + reset |
| Google OAuth | staging real login |
| Stripe | test checkout + webhook |
| Browserless/Playwright | headless run |
| Ops webhook | test-alert |
| Analytics | consent on/off |

### 3. Bug bash focus
- [ ] Middleware auth gaps
- [ ] Tenant isolation spot checks
- [ ] SSE reconnect
- [ ] Checkout race / double webhook
- [ ] Mobile approve path
- [ ] Empty LLM / 402 honest UI
- [ ] Admin RBAC negative tests

### 4. Performance
- [ ] Marketing LCP budget
- [ ] API p95 hot paths within M32 baselines
- [ ] No N+1 regressions on queue/admin

### 5. Docs & release
- [ ] Update README with 2030 product story + mission index pointer
- [ ] CHANGELOG section for perfection pack
- [ ] Launch checklist executed (`docs/runbooks/launch-checklist.md`)
- [ ] Tag release; deploy staging → smoke → production decision
- [ ] Mark polish-pack 29–30 done if completed here

### 6. Design sign-off
- [ ] Design Council ≥19/20 on all primary surfaces listed in design-review.md
- [ ] North star checklist signed in `design-review.md` addendum

## Acceptance criteria
- [ ] CI green on release commit
- [ ] Staging golden path + Stripe test + Google OAuth verified
- [ ] No open Critical/High defects without owner waiver in writing
- [ ] Screenshots + mobile pack refreshed
- [ ] Tag pushed; runbooks accurate
- [ ] Mission 99 final loop clean

## Production guidance
- Backup before migrate
- Follow deploy + rollback runbooks
- `bash scripts/railway-smoke.sh` post-deploy
- Monitor ops alerts 48h post-launch

## Exit: Definition of Done (whole product)

1. Discover or import jobs into a list with fit explanations  
2. Tailor resume + cover letter; approve/lock  
3. Run apply pipeline with live visibility  
4. Review fill diff; Approve/Send  
5. Confirmation archived; tracker status updated  
6. Analytics reflect activity; admin can operate  
7. Auth (email + Google) and Pro checkout work  
8. Mobile + desktop polished; a11y gates green  
9. No lint/type/test red; secrets clean  
