# Mission 22 — Web performance baseline

**Date:** 2026-06-12  
**Environment:** Windows dev host; production spot-check `https://jober.app`

## Summary

Marketing first paint no longer pulls TanStack Query, auth session bootstrap, or the hero run-preview chunk on the critical path. App routes keep a tuned query cache and existing dynamic imports for charts and the run console. Total client chunk pool is slightly larger (+10 KB) because `dynamic()` splits `HeroRunPreview` into its own chunk; the win is **route-level deferral**, not shrinking the global pool.

## Bundle gate (`.next/static/chunks`)

| Phase | Budget (KB) | Measured (KB) | Marketing import guard |
|-------|-------------|---------------|------------------------|
| **Before** (monolithic `Providers` on root layout) | 2800 | 2550 | not enforced |
| **After** (Mission 22) | 2650 | 2560 | green — no `recharts` / `react-resizable-panels` / `cmdk` in marketing/auth trees |

Command: `cd apps/web && pnpm build && pnpm check:bundles`

> Next.js 16 build output no longer prints per-route “First Load JS” tables. Regression protection is `check-bundle-budget.mjs` (total pool + static-import guard) plus the optimizations listed below.

## Optimizations shipped

| Area | Change | Rationale |
|------|--------|-----------|
| Providers | `ShellProviders` (theme, analytics, toaster) on root; `AppProviders` (QueryClient, auth, prefs) on `(app)` + `(auth)` only | Avoid session/query work on marketing/legal/blog first paint |
| Hero | `HeroRunPreview` via `next/dynamic` + pulse placeholder | LCP element is copy + background; preview loads after hero text |
| Fonts | Geist Sans `display: "swap"`, `preload: true`; mono `preload: false` | Reduce FOIT on LCP text |
| Query cache | `staleTime: 60s`, `gcTime: 5m`, `refetchOnWindowFocus: false` | Route switches feel instant without stale-data storms |
| Budget script | Total cap 2800 → 2650 KB; marketing import guard for heavy app deps | CI fails on chunk regression or marketing leaks |
| Already in place | `/analytics` panels + `/runs/[id]` `RunConsole` use `dynamic()` | Verified unchanged this mission |

## Lighthouse / Core Web Vitals

**Targets (mission acceptance):** marketing LCP &lt; 2.5s, CLS &lt; 0.1 on simulated mid-tier mobile (production).

| Route | Env | Strategy | LCP | CLS | INP | TBT | Perf score | Notes |
|-------|-----|----------|-----|-----|-----|-----|------------|-------|
| `/` | production | mobile | — | — | — | — | — | Automated CLI blocked (see below) |
| `/features` | production | mobile | — | — | — | — | — | Manual PSI post-deploy |
| `/pricing` | production | mobile | — | — | — | — | — | Manual PSI post-deploy |
| `/signup` | production | mobile | — | — | — | — | — | Manual PSI post-deploy |
| `/` | local (`pnpm build && pnpm start`) | mobile | — | — | — | — | — | Not run this loop (port harness) |

**Automated measurement blocker:** `npx lighthouse https://jober.app` (headless Chrome) failed with *“Chrome prevented page load with an interstitial”* — likely bot/WAF or certificate interstitial on unattended Chrome. PageSpeed Insights API fetch also timed out from the agent environment.

**Operator follow-up (post-deploy):**

1. [PageSpeed Insights](https://pagespeed.web.dev/analysis?url=https://jober.app) — mobile + desktop for `/`, `/features`, `/pricing`, `/signup`.
2. Paste results into the table above on the next continuation loop or Mission 30 release candidate pass.
3. If LCP &gt; 2.5s persists, next candidates: below-fold `dynamic()` on `DifferentiatorBento` / `HowItWorks` on home (not done — smallest fix first).

## Animation trace summary

Surfaces reviewed: marketing hero (`hero.tsx`, `animated-background.tsx`), motion tokens (`lib/design/motion.ts`).

| Surface | Properties animated | Layout thrash risk |
|---------|---------------------|-------------------|
| Hero stagger (`motionHeroStagger`) | `opacity`, `transform: translateY` | Low — compositor-friendly |
| Hero background (`jober-drift`) | `transform: translate + scale` on blurred orbs | Low for layout; blur is paint cost only |
| Hero preview float (`jober-hero-float`) | `transform: translateY` | Low |
| Button press (`motionPress`) | `transform: scale` | Low |

`pnpm check:motion` — green (no ad-hoc duration literals in feature components).

## Validation (Mission 22)

| Gate | Result |
|------|--------|
| `pnpm typecheck` | green |
| `pnpm lint:strict` | green |
| `pnpm test` | 108 passed |
| `pnpm build` | green |
| `pnpm check:motion` | green |
| `pnpm check:bundles` | 2560 KB / 2650 KB budget, import guard green |
| `pnpm test:e2e` | **71 passed** (after freeing port 3000; `CI=true` fresh `pnpm start`) |

## Acceptance criteria mapping

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Marketing LCP &lt; 2.5s, CLS &lt; 0.1 (prod mobile) | **Deferred** — automated PSI/Lighthouse blocked; manual PSI required post-deploy |
| 2 | No app-only heavy deps in marketing/auth first-load | **Green** — static import guard |
| 3 | `/analytics` + `/runs/[id]` dynamically imported | **Green** — verified in source |
| 4 | Budgets tightened; `check:bundles` protective | **Green** — 2650 KB cap |
| 5 | Compositor-clean animations; gates green | **Green** — motion audit + web gates (e2e via CI) |

## Follow-ups

| Item | Owner |
|------|-------|
| Fill Lighthouse table from PSI after deploy | Mission 31 after 22 / operator |
| Below-fold marketing `dynamic()` if LCP still high | Mission 22 continuation or 28 |
| `/kitchen-sink` lacks `AppProviders` if it ever needs React Query | note only — no current usage |
