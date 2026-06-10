# Mission 09: Workspace Layout Discipline (Split-Pane Only Where Earned)

## Purpose
Every in-app route currently shares the same 40/60 split-pane shell, and a bottom "Describe what you want…" bar is "pasted on" every page (UI-REVIEW). The ops-desk layout is the product's best in-app asset — on run/watch surfaces. Reusing it everywhere dilutes it and wastes space on data-dense pages. This mission gives each route the layout it earns.

## Context From Audits
UI-REVIEW generic-pattern rows: "Identical split layout — all in-app routes" and "Bottom 'Describe what you want…' bar — every in-app page; Hyper-style products use ⌘K command palette + contextual prompts." The UI review's P0 list is explicit: the bottom AI bar is **non-functional** — hiding it and adding the command palette is a P0 quick win, so the bar's removal must not wait on full palette feature-parity (verify non-functionality in code first; if any capability is real, fold it into the palette). Theme 2: "split-pane only on run/watch surfaces; other pages get full-width editorial layouts." Positioning audit §19.2. The shell lives in `apps/web/src/components/workspace/` (three-pane: collapsible nav, center work column with command bar, resizable right canvas; prefs in localStorage; shortcuts ⌘B/⌘\\/⌘/), mounted via `apps/web/src/app/(app)/app-chrome.tsx` and `(app)/layout.tsx`.

## Scope
- Define two in-app layout modes: **ops-desk** (nav + work + canvas) for `/runs/[id]` and any live-watch surface, and **editorial full-width** (nav + content) for dashboard, queue, discover, library, search, analytics, settings, admin.
- Convert non-run routes to editorial layouts without breaking their content components; tables and charts get the reclaimed width.
- Replace the persistent bottom command bar with the existing `cmdk` command palette (⌘K) plus contextual primary actions per page; keep the ⌘/ shortcut as palette focus if that matches current muscle memory.
- Preserve all keyboard shortcuts and localStorage layout prefs for the surfaces that keep panes.

## Out of Scope
- Redesigning page content/components (Mission 10 handles component tiering).
- The run console internals (Mission 15).
- New navigation structure or renamed routes.

## Starting Checklist
1. Read `components/workspace/` fully: how panes mount, which routes opt in, where the command bar renders.
2. Read `(app)/app-chrome.tsx` and `(app)/layout.tsx` for the wiring point.
3. `grep -rn "cmdk\|CommandDialog\|command" apps/web/src/components` — what palette infrastructure exists (cmdk is installed).
4. List every `(app)` route and its current canvas usage (which actually stream content to the right pane?).
5. Check `stores/` (Zustand) for layout state that needs migrating.

## Tasks
1. Introduce a per-route layout declaration (e.g., a `layoutMode` constant consumed by `app-chrome.tsx`) — explicit, not inferred.
2. Keep ops-desk on `/runs/[id]`; convert each other route to editorial; fix per-page max-widths, gutters, and table density to use the space well.
3. **P0 first:** verify in code whether the bottom bar does anything real (`grep -rn "Describe what you want" apps/web/src`); if non-functional, remove it immediately as its own commit. Then build/wire the ⌘K palette: navigation entries, page-contextual actions (e.g., on `/queue`: Import spreadsheet, New batch); fold any real bar capability into the palette. Apply the larger-nav-text direction (Mission 07/28) to the in-app nav while touching it.
4. Migrate/clean localStorage prefs so stale pane prefs don't break converted routes.
5. Update any e2e selectors that referenced the old bar.
6. Re-capture screenshots 14–23.

## Self-Improvement Loop
1. Inspect each route in both keyboard and mouse flows.
2. Identify the highest-impact layout misuse or regression.
3. Make the smallest coherent improvement.
4. Validate (gates + manual shortcut pass).
5. Document.
6. Repeat until acceptance criteria hold.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion`
- `pnpm test:e2e` (golden-path smoke must still pass — it traverses these routes)
- Manual: every `(app)` route at 1440px; ⌘K opens palette everywhere; ⌘B nav toggle still works; `/runs/[id]` panes resize and persist; no route renders an empty right pane.

## Acceptance Criteria
1. Only run/watch surfaces use the split-pane; all other routes are editorial full-width with improved density.
2. The bottom bar is gone; ⌘K palette works on every in-app route with at least navigation + page-contextual actions.
3. No keyboard shortcut regressions; layout prefs persist where panes remain.
4. UI-REVIEW rows "identical split layout" and "bottom bar" closed with re-captured screenshots.
5. Design Council gate ≥18/20 on converted surfaces.

## Documentation Requirements
- Update README workspace-shell section (Mission 17 paragraph) to describe the two layout modes and palette.
- Closure notes + refreshed PNGs in `docs/screenshots/`.

## Git Workflow
`git status` first; commits per stage (layout mode plumbing → route conversions → palette → bar removal), each gated; bodies cover what/why/validation/follow-ups; push after gates.

## Production Guidance
Deploy only after Mission 31 has run on this mission — this is the largest structural UI change in the pack. Require: full gates + e2e green, manual pass of all routes, and a re-run of the local golden path before deploying. Then `bash scripts/railway-smoke.sh`.
