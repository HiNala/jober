# Mission 39 — Workspace Command Center (Hyperagent-Inspired App Shell)

> **Phase:** Perfection pack  
> **Depends on:** M17, M18, M35  
> **Run Mission 99 after**

## Purpose

Rebuild the authenticated app chrome into a **premium command center**: Hyperagent-like sidebar + focus main stage + earned live canvas, Grok-like empty power states, world-class run console and navigation. This is the in-product 2030 identity.

## Context

M17 shell v2 + polish 09 improved layout discipline (split only on runs, ⌘K palette). Still gaps: not Hyperagent-caliber; skeleton loading inconsistent; composer absent on natural surfaces; run console not yet “ops desk of the future”; nav density and visual polish lag marketing.

## Scope

### In scope
- App sidebar redesign (icons + labels, sections, user pill, plan badge)
- Dashboard empty/power state (“Let’s get to work.” + suggestion chips)
- Global command palette depth (nav + actions: import, new batch, settings)
- Run console: StatusLivePill, SkeletonStream, AmbientCanvas idle, ApproveSendBar integration points
- CheckpointCard for human handoffs (wire to existing checkpoint APIs)
- Page headers, loading.tsx/error.tsx consistency
- Library / Queue / Discover visual alignment to workspace family
- Remove residual generic chrome

### Out of scope
- New backend agent types
- Replacing SSE with WebSockets
- Full document engine (M41) or discovery ranking (M40) — only shell affordances

## Starting checklist
- [ ] Map `(app)/layout.tsx`, `app-chrome.tsx`, `workspace-nav.tsx`
- [ ] List all `loading.tsx` / `error.tsx` under `(app)/`
- [ ] Review run console components and checkpoint UI

## Tasks

### 1. Sidebar & chrome
- [ ] Near-black rail; active state pill; grouped: Work (Dashboard, Discover, Queue, Runs), Materials (Documents, Library, Vault), Insights (Analytics), System (Settings, Admin if rbac)
- [ ] “New application” or “Import jobs” primary control near top (like Hyperagent New thread)
- [ ] User pill: name, plan chip (Free/Pro), sign out
- [ ] Collapse to icons on `md`; mobile bottom tabs (M44 may refine)

### 2. Dashboard command center
- [ ] Grok-style empty: large headline, single primary path (Import tracker / Discover jobs)
- [ ] Suggestion chips: Import XLSX · Resume vault · Start batch · View queue
- [ ] Populated: needs-attention banner, metrics, recent runs — not a wall of equal cards
- [ ] Optional contextual `CommandComposer` that routes intents to real pages (not fake LLM chat)

### 3. Run console excellence
- [ ] Left: event stream with SkeletonStream while connecting
- [ ] Right: AmbientCanvas until first screenshot; then live frames
- [ ] Header: job title, company, StatusLivePill, policy badge
- [ ] CheckpointCard modal/panel for NEEDS_HUMAN
- [ ] Sticky ApproveSendBar when state is REVIEW_AND_SUBMIT
- [ ] Reconnect UX for SSE already from polish 15 — re-verify

### 4. Cross-page consistency
- [ ] Shared `PageHeader` with title, description, actions
- [ ] Tables use workspace surface family
- [ ] Empty states onboard with one CTA each (queue, library, documents, vault, analytics)

### 5. Command palette
- [ ] ⌘K: navigation + “Import jobs”, “Open vault”, “Start batch”, “Go to run…”
- [ ] Recent destinations
- [ ] Keyboard-only complete path

## Validation
```bash
cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm build
pnpm exec playwright test e2e/a11y-app.spec.ts e2e/core-journey.fullstack.spec.ts e2e/recovery.fullstack.spec.ts
node scripts/capture-screenshots.mjs  # app routes
```

## Acceptance criteria
- [ ] Authenticated shell matches north star layout C
- [ ] Split canvas only on earned routes
- [ ] Dashboard empty state feels intentional and premium
- [ ] Checkpoint + ApproveSendBar visible and usable on fixture run
- [ ] Design Council ≥19/20 app chrome + run console
- [ ] No bolted-on fake AI bar on every page

## Production guidance
- Deploy web after visual QA on staging
- Re-capture `docs/screenshots/prod/*` app set
