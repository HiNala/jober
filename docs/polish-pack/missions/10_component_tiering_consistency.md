# Mission 10: Component Tiering and Consistency (Three Families, Not One Card)

## Purpose
One `Card` treatment currently serves marketing bentos, data tables, and terminal surfaces — "same border, same radius, same padding on every block" (UI-REVIEW). This mission establishes three deliberate component families and sweeps the app for consistency, reuse, and dead variants.

## Context From Audits
UI-REVIEW theme 3: "'marketing bento' ≠ 'data table' ≠ 'terminal' — three distinct component families, not one Card everywhere." Positioning audit §19.1. Inputs that already exist: tokens (`lib/design/tokens.ts`, `docs/architecture/design-tokens.md`), `components/ui/` (shadcn base), `/kitchen-sink` component catalog, custom eslint rules (`apps/web/eslint-rules/`).

## Scope
- Codify three families with distinct surface treatments (radius, border, elevation, density, type scale):
  1. **Marketing/bento** (`components/marketing/`) — expressive, larger radius, gradients allowed.
  2. **Workspace data** (`components/ui` + feature dirs) — dense, quiet borders, table-first.
  3. **Terminal/live** (`components/canvas/`, run console) — mono, dark-on-dark, status accents.
- Express the families as tokens/variants (CVA is installed — use `class-variance-authority` variants, not forks).
- Sweep all feature component dirs (`admin`, `analytics`, `dashboard`, `discover`, `documents`, `import`, `jobs`, `library`, `run-console`, `settings`, `vault`, `workspace`) for: off-family styling, duplicated one-off components, inline hex values bypassing tokens, inconsistent spacing.
- Update `/kitchen-sink` to display the three families side by side as the living reference.
- Optionally add an eslint rule (the repo already has custom rules) banning raw color literals in feature components.

## Out of Scope
- Visual redesign of individual screens beyond family alignment.
- New components without an existing consumer.
- Marketing page restructuring (done in 07–08).

## Starting Checklist
1. Read `lib/design/tokens.ts` and the kitchen-sink page to see the current catalog.
2. `grep -rn "#[0-9a-fA-F]\{6\}" apps/web/src/components --include="*.tsx" | grep -v tokens` — raw color usage.
3. Inventory `Card`/surface usage: `grep -rln "Card" apps/web/src/components | sort`.
4. Read `apps/web/eslint-rules/` to learn the custom-rule pattern.
5. Skim each feature dir for near-duplicate components (e.g., multiple stat-card or list-row implementations).

## Tasks
1. Define family variants in the design system layer (token additions + CVA variants on the base surface components); document in `docs/architecture/design-tokens.md`.
2. Migrate components family-by-family: terminal/live first (smallest), then workspace data (largest), then confirm marketing already complies from 07–08.
3. Consolidate duplicates found in the sweep (keep one, delete others, update imports).
4. Replace raw color literals with tokens; add the eslint rule if practical and wire into `lint:strict`.
5. Rebuild `/kitchen-sink` sections per family; ensure it is excluded from production nav/sitemap/robots.
6. Snapshot-test the base family components in vitest.

## Self-Improvement Loop
1. Inspect one feature dir at a time against the family definitions.
2. Identify the highest-impact inconsistency or duplication.
3. Make the smallest coherent improvement.
4. Validate (gates + visual check of affected routes).
5. Document in the migration table.
6. Repeat until the sweep table shows every dir compliant.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles`
- `pnpm test:e2e`
- Manual: walk `/kitchen-sink`, then every `(app)` route, confirming family coherence; raw-color grep returns only token files.

## Acceptance Criteria
1. Three families are defined in code (variants + tokens) and documented.
2. Migration table in `docs/polish-pack/notes/10_component_sweep.md` shows every feature dir migrated; duplicates consolidated with net component count reduced or equal.
3. No raw color literals outside the token layer (grep-proven or lint-enforced).
4. `/kitchen-sink` reflects the system and is production-hidden.
5. All gates green.

## Documentation Requirements
- `docs/polish-pack/notes/10_component_sweep.md` (inventory → action → result).
- Update `docs/architecture/design-tokens.md` with the family definitions.

## Git Workflow
`git status` first; commit per family migration, then per consolidation batch; review diffs carefully (wide mechanical changes hide regressions); bodies cover what/why/validation/follow-ups; push after gates.

## Production Guidance
Deployable after gates + a manual all-routes pass; visually wide but behaviorally inert. Prefer batching with Mission 09's deploy so production changes layout and components coherently, then re-capture all 23 screenshots.
