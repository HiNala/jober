# Mission 26: End-to-End Validation Expansion

## Purpose
Two Playwright specs (`a11y-marketing`, `golden-path-smoke`) plus the additions from Missions 04/13/14 still leave the deepest product flows e2e-untested: full import→submit against fixtures, recovery/checkpoint paths, document studio cycles, settings/policy changes taking effect. This mission builds the e2e suite that lets every future change be trusted without a manual walkthrough.

## Context From Audits
Application audit §15 gap: "no e2e of authenticated app flows (login → import → batch → run console)". Infrastructure available: fixture ATS server (`make fixture-serve`), dev-auth bypass for frictionless sessions, Playwright config (`apps/web/playwright.config.ts`), CI services already run Postgres/Redis/MinIO.

## Scope
- **Core journey spec (the centerpiece):** login (or bypass) → import fixture workbook → queue shows rows → create dry-run batch → run executes against the fixture ATS → run console streams → checkpoint appears → resolve via UI → review state → (dry-run completion) → artifacts listed. Built on fixture determinism; no external network.
- **Recovery spec:** fixture login-wall page → human checkpoint created → failure report visible in job drawer.
- **Documents spec:** generate (template mode) → edit → lock → regen → download asserts a PDF response.
- **Settings-effect spec:** change policy default in `/settings` → batch creation reflects it.
- **Auth journey spec:** real signup → (console email backend) verify → login → logout (extends Mission 11's seams).
- **CI integration:** decide e2e placement in `.github/workflows/ci.yml` (separate job with full stack; fixture server step exists in CI already per `FIXTURE_ATS_PORT`); keep runtime sane via Playwright sharding/projects.
- Stabilization discipline: data-testid additions where selectors are brittle; zero `waitForTimeout`-style sleeps — event/state-based waits only.

## Out of Scope
- Visual-regression tooling (screenshots remain a manual review loop via `capture-screenshots.mjs`).
- Testing real external ATSs or real LLM providers in CI.
- Load testing (Mission 23 done).

## Starting Checklist
1. Read `playwright.config.ts` (projects, webServer, baseURL handling, the `PLAYWRIGHT_SKIP_WEB_SERVER` escape hatch used by the screenshot script).
2. Read `golden-path-smoke.spec.ts` — how far it already goes and its auth approach; build on it, don't duplicate.
3. Read the CI workflow's existing service setup; estimate the cost of a full-stack e2e job.
4. Confirm fixture workbook + fixture ATS pages cover the journey (see `fixtures/ats` catalog and `apps/api/tests/fixtures`).
5. Inventory existing `data-testid` usage conventions.

## Tasks
1. Author the five specs above, in the listed priority order; each runs independently and cleans up (or uses a fresh tenant per run).
2. Add the e2e CI job (full stack: api + worker + fixture server + web) gated to run on PRs and main; document local invocation in `docs/polish-pack/notes/gates.md`.
3. De-brittle selectors (`data-testid` standard, documented in `apps/web/AGENTS.md`).
4. Run the suite 3× locally and once in CI; fix all flakes at root cause.
5. Wire failure artifacts (Playwright traces/screenshots) into CI uploads for debuggability.

## Self-Improvement Loop
1. Inspect the next untested critical flow.
2. Identify the highest-value missing assertion (what regression would hurt most?).
3. Write the smallest stable spec section.
4. Validate ×3 locally for determinism.
5. Document coverage in the e2e map.
6. Repeat until the five specs pass deterministically locally and in CI.

## Validation
- `cd apps/web && pnpm test:e2e` ×3 consecutive green locally (full stack up).
- CI run green including the new e2e job, with trace artifacts on failure verified once (force a failure, check the upload, revert).
- `pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build`

## Acceptance Criteria
1. All five specs exist, pass deterministically (3× local, 1× CI), and use no sleep-based waits.
2. The core journey spec exercises import → run → checkpoint resolve → completion against fixtures.
3. E2E runs in CI on every PR/main push with failure traces uploaded.
4. Selector conventions documented; no spec depends on visual text likely to change in copy polish (Mission 27 follows — use testids).
5. All gates green.

## Documentation Requirements
- `docs/polish-pack/notes/26_e2e_map.md` (flow × spec × assertions).
- `docs/architecture/testing.md` updated with the e2e tier description.
- `docs/polish-pack/notes/gates.md` gains the e2e commands.

## Git Workflow
`git status` first; commits per spec + one for CI wiring; reviewed diffs; bodies with what/why/validation/follow-ups; push after gates and confirm the new CI job on the actual push.

## Production Guidance
No deployment — test infrastructure only. From this mission forward, the deploy bar for all later missions includes the e2e suite green.
