# Mission 43 — Analytics, Admin & Ops Excellence

> **Phase:** Perfection pack  
> **Depends on:** M25–M28, M35, M39  
> **Run Mission 99 after**

## Purpose

Make **first-party analytics** and the **admin dashboard** operator-grade: beautiful, truthful, actionable — matching the premium product shell. Cover product insights for users and ops controls for admins.

## Context

In-house analytics + admin sections exist. Gaps: visual polish to 2030 shell; some rollups may lag; cost/attention UX; acquisition funnel clarity; ensure no third-party trackers; consent still respected.

## Scope

### In scope
- User `/analytics` dashboard redesign (workspace family + charts)
- Admin sections polish: overview, acquisition, users, runs, cost, config, system
- Truthful empty states; loading skeletons
- Alerting + attention banners accuracy
- Event taxonomy audit — drop dead events, document live ones
- Performance: chart code-split; no huge bundles on dashboard
- RBAC verification for all admin mutations

### Out of scope
- Replacing with Mixpanel/GA
- Real-time multiplayer admin
- Data warehouse export (beyond existing export tools)

## Starting checklist
- [ ] Read `docs/analytics/event-taxonomy.md` (web) + admin routers
- [ ] Confirm consent gating still suppresses tracking when declined
- [ ] Review chart components from M26

## Tasks

### 1. User analytics
- [ ] KPIs: applications started, submitted, success rate, needs-human rate, letter gens, discover accepts
- [ ] Trends over 7/30/90 days
- [ ] Per-platform outcome breakdown
- [ ] Funnel: discovered → queued → run → verified → submitted
- [ ] Export CSV of personal stats (optional)

### 2. Admin excellence
- [ ] Overview: DAU/WAU/MAU, signups, runs, LLM cost, health, attention list
- [ ] Acquisition: UTM, funnel, waitlist counts
- [ ] Users: search, promote/suspend, support view (no vault secrets)
- [ ] Runs: failure taxonomy, backlog
- [ ] Cost: budget vs actual; spike link to runbook
- [ ] System: readyz, queue depth, audit log filters
- [ ] Config: flags, announcement banner, letter defaults

### 3. Data integrity
- [ ] Reconcile cost rollups with LlmCall
- [ ] Idempotent event ingestion; rate limits held
- [ ] Privacy: no raw vault fields in analytics

### 4. UI
- [ ] Align admin nav with command center shell
- [ ] Chart motion from tokens; reduced-motion safe
- [ ] Mobile admin: usable stacked layout (desktop-primary ok if documented)

### 5. Tests
- [ ] `test_analytics*.py`, `test_admin_*.py` green
- [ ] RBAC denial tests
- [ ] Web vitest for taxonomy constants if present

## Validation
```bash
cd apps/api && pytest tests/test_analytics.py tests/test_analytics_dashboard.py tests/test_admin_dashboard.py tests/test_admin_routes_extended.py tests/test_rbac.py tests/test_ops_alerting.py tests/test_ops_metrics.py -q
cd apps/web && pnpm typecheck && pnpm lint:strict
```

## Acceptance criteria
- [ ] User analytics answers “how is my search going?” in <10s glance
- [ ] Admin can diagnose cost spike + queue backup from UI
- [ ] Consent-off → no client product analytics emitted
- [ ] Design Council ≥19/20 analytics + admin
- [ ] Taxonomy doc updated

## Production guidance
- Ops webhook configured before relying on alerts
- Re-run restore/ops drills if schema changes
