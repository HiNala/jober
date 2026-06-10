# Mission 05: Page States as Onboarding (Empty / Loading / Error / Success)

## Purpose
A new production user lands on an empty `/dashboard` and a `/queue` whose empty state says `make seed` — dev copy in production (UI-REVIEW). Empty states are the first-run experience; this mission turns every empty/loading/error/success state into onboarding that names the next action, using the existing shared state components.

## Context From Audits
UI-REVIEW theme 5 ("Empty states as onboarding — illustrated steps, primary CTA, sample data toggle, Figma-style") and the per-screen notes for dashboard (14), queue (15), discover (16), library (17–20), search (21), analytics (22). Application audit §9 (first-run experience weak) and positioning audit §19.4 ("Empty states onboard… never dev copy"). The shared primitives already exist: `apps/web/src/components/states/page-states.tsx`.

## Scope
- Inventory every empty, loading, error, and success state across `(app)` routes: dashboard, queue, discover, library (4 tabs), search, analytics, settings, runs.
- Rewrite empty states to: one-line value statement → primary CTA (the real next action: "Import your tracker", "Connect a board", "Generate your first letter") → optional secondary "load sample data" where seeding exists.
- Remove all dev copy from user-facing strings — the UI review's P0 list names three concretely: the queue empty state (`make seed`), the **settings/vault dropzone showing wrong text**, and CMS placeholder notes leaking on the blog index.
- First-run dashboard onboarding (P0): an empty `/dashboard` must present the "import your tracker → run your first dry-run batch" path as its primary content, not empty metric cards.
- Ensure loading states use skeletons (not spinners-only) and error states offer retry, via `page-states.tsx` so the fix is systemic.
- Wire a "sample data" path only if an API mechanism already exists (the seed script logic can back a dev-flagged endpoint **only if trivial**; otherwise CTA points to import).

## Out of Scope
- New onboarding wizards, tours, or checklists (feature creep).
- Redesigning page layouts (Mission 09).
- Marketing pages (Missions 07–08).

## Starting Checklist
1. Read `apps/web/src/components/states/page-states.tsx` — current API of Empty/Loading/Error components.
2. `grep -rn "make seed\|seed" apps/web/src --include="*.tsx"` to find dev copy.
3. For each `(app)` route, find how empty data is detected and which component renders (e.g., `apps/web/src/app/(app)/queue/`, `components/jobs/`, `components/library/`).
4. Check `apps/api/scripts/seed.py` for what demo data exists, to judge the sample-data option.
5. Review screenshots 14–23 in `docs/screenshots/prod/` for current states.

## Tasks
1. Build the state inventory table (route × {empty, loading, error, success}) in `docs/polish-pack/notes/05_states_inventory.md`; mark each compliant/deficient.
2. Extend `page-states.tsx` if needed (icon/illustration slot, primary + secondary CTA, helper text) — one component family, token-styled.
3. Fix each deficient state, worst-first — P0s first: queue dev copy, settings/vault dropzone text (find via `grep -rn "drop" apps/web/src/components/vault apps/web/src/components/settings`), blog CMS-note leak, dashboard first-run onboarding (empty metrics → "Import your tracker / Run your first batch" path); then discover, library tabs, search, analytics (empty charts → explain when data appears).
4. Standardize error states: human message, retry button, no raw error strings; confirm route-level `error.tsx` boundaries exist for `(app)` segments and add missing ones.
5. Verify success/confirmation states for import, batch creation, and submit show next-step guidance.
6. Add/extend vitest tests for `page-states.tsx` variants; snapshot the queue empty state to lock out dev copy regressions.
7. Re-capture screenshots of fixed routes.

## Self-Improvement Loop
1. Inspect the next route's four states (force them: empty DB, throttled network, failing API via devtools).
2. Identify the highest-impact deficient state.
3. Make the smallest coherent improvement.
4. Validate (gates + manual forcing).
5. Document in the inventory table.
6. Repeat until every cell of the inventory is compliant.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion`
- `pnpm test:e2e`
- Manual: fresh account against local stack (`make up`, **no** `make seed`) — walk every `(app)` route and confirm each empty state names a real next action; kill the API container and confirm error states render with retry.
- `grep -rn "make seed" apps/web/src` returns nothing.

## Acceptance Criteria
1. The state inventory shows every route × state compliant.
2. Zero dev-only copy in any user-facing string.
3. Every empty state has a working primary CTA that advances the golden path.
4. Every data surface has a skeleton loading state and an error state with retry.
5. Re-captured screenshots confirm the changes; UI-REVIEW "dev copy in empty states" row closed.

## Documentation Requirements
- `docs/polish-pack/notes/05_states_inventory.md` (new).
- Closure notes + refreshed PNGs in `docs/screenshots/`.

## Git Workflow
`git status` first. Commit per route-group (`feat(states): queue empty state as onboarding [pack-05]` etc.); review diffs before staging; bodies cover what/why/validation/follow-ups. Push after gates pass.

## Production Guidance
Deployable after gates pass — this is safe polish that improves first-run UX. Run `bash scripts/railway-smoke.sh` after deploy and re-capture prod screenshots.
