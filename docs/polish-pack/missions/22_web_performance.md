# Mission 22: Web Performance Optimization

## Purpose
Polish is perceived through speed: the Linear-grade feel the design direction targets requires fast first paint on marketing and instant-feeling navigation in-app. The repo has budgets (`pnpm check:bundles`) but no recorded Core Web Vitals baseline. This mission measures, fixes the verified offenders, and locks results into budgets.

## Context From Audits
Application audit §12: verify Recharts/canvas code-splitting out of marketing/auth bundles; LCP on `/` with the hero media (Mission 07 added a loop — measure its cost); SSE volume handled in Mission 15. Tools in place: `scripts/check-bundle-budget.mjs`, Next 16 App Router (RSC, `next/image`, `next/font`), Tailwind 4.

## Scope
- **Measure first:** Lighthouse (or equivalent) on `/`, `/features`, `/pricing`, `/signup` (desktop + simulated mobile) and against production; record LCP/CLS/INP/TBT + route-level bundle sizes (`pnpm build` output table) into a baseline doc.
- **Marketing:** hero media loading strategy (poster, lazy loop, preload only the LCP asset), font loading (`next/font`, no FOIT), image optimization via `next/image`, zero app-only dependencies (recharts, resizable-panels, cmdk, canvas components) in marketing/auth chunks — verify via `next build` route table and bundle analysis.
- **App:** dynamic-import heavy components (charts on `/analytics`, canvas on `/runs/[id]`); TanStack Query cache settings audit (stale-while-revalidate where safe so route switches feel instant); avoid client-component overuse on editorial pages converted in Mission 09 (RSC where possible).
- **Lock-in:** tighten `check-bundle-budget.mjs` budgets to post-fix sizes; add any new heavy route to the budget file.
- Animation performance: micro-interactions from Missions 07/08/17 run on compositor-friendly properties (transform/opacity); no layout-thrash loops (verify with devtools performance trace on the hero).

## Out of Scope
- API latency (Mission 23), SSR caching infrastructure/CDN changes (note recommendations only).
- Visual changes; removing features for speed.
- Chasing scores beyond the targets below.

## Starting Checklist
1. `cd apps/web && pnpm build` — read the full route/chunk table; flag routes >150 kB first-load JS.
2. Read `scripts/check-bundle-budget.mjs` (current budgets and how they're enforced).
3. `grep -rn "use client" apps/web/src/app | wc -l` and sample the converted editorial pages for unnecessary client components.
4. `grep -rn "recharts\|react-resizable-panels" apps/web/src` — import locations vs dynamic imports.
5. Run baseline Lighthouse locally (`pnpm build && pnpm start`) and against production.

## Tasks
1. Write the baseline (`docs/polish-pack/notes/22_perf_baseline.md`): metrics × route × environment.
2. Fix marketing offenders (media strategy, fonts, images, chunk leaks) — re-measure after each fix; keep evidence.
3. Fix app offenders (dynamic imports, RSC conversion where cheap, query cache tuning).
4. Performance-trace the hero and one micro-interaction-heavy surface; fix any non-compositor animation.
5. Tighten budgets; ensure `check:bundles` fails on regression of fixed routes.
6. Re-run full measurement set; record final table beside baseline.

## Self-Improvement Loop
1. Inspect the worst remaining metric in the table.
2. Identify its dominant cause (trace/bundle-analyze — never guess).
3. Make the smallest coherent fix.
4. Validate by re-measuring that route + `pnpm build` table + budgets.
5. Update the table.
6. Repeat until targets hold or remaining causes are documented as platform-level (Railway cold starts etc.).

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles`
- `pnpm test:e2e`
- Lighthouse runs recorded before/after, local + production.

## Acceptance Criteria
1. Marketing routes: LCP < 2.5s and CLS < 0.1 on simulated mid-tier mobile against production (or documented platform blockers with evidence).
2. No app-only heavy dependency appears in marketing/auth first-load chunks (build-table-proven).
3. `/analytics` and `/runs/[id]` heavy components dynamically imported.
4. Budgets tightened to post-fix sizes; `check:bundles` green and meaningfully protective.
5. Animations compositor-clean on traced surfaces; all gates green.

## Documentation Requirements
- `docs/polish-pack/notes/22_perf_baseline.md` (before/after tables, traces summary).
- Budget rationale comment in `check-bundle-budget.mjs` if budgets changed.

## Git Workflow
`git status` first; one commit per optimization with the measurement delta in the body (`perf(web): lazy-load analytics charts, -84kB first load [pack-22]`); push after gates.

## Production Guidance
Deployable after gates pass. Re-run Lighthouse against production post-deploy to confirm the wins survive the platform; `bash scripts/railway-smoke.sh`.
