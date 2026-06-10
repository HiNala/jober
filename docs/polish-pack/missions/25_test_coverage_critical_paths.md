# Mission 25: Test Coverage for Critical Paths (Unit/Integration Depth)

## Purpose
The API suite is broad, but this pack changed real behavior (consent gate, forms mapper, layout modes, email sender, error envelope, auth lifecycle). This mission measures coverage of the *critical paths*, fills verified gaps in unit/integration tests (web component tests especially — vitest depth is the known unknown), and de-flakes anything that wobbled during the pack.

## Context From Audits
Application audit §15: API strong; web vitest "component test depth unknown (discovery task)"; worker adequate. Critical paths = the MISSION_INDEX definition-of-done journey + the safety policies + everything this pack changed.

## Scope
- **Discovery first:** run coverage (`pytest --cov` for api/worker if pytest-cov is available — add as dev dep if not; `vitest --coverage` for web) and map results against a hand-written critical-path list (not a blanket % target).
- **Web unit/component gaps (expected focus):** consent sheet states, forms mapper + a representative form, page-states variants, reconnect state machine (Mission 15), command palette actions, analytics SDK gating, document studio lock behavior.
- **API gaps:** anything on the critical-path list under ~80% branch coverage gets targeted tests — especially services touched by this pack (email sender, error handlers, auth lifecycle) and the orchestration seams (batch → enqueue → run state transitions with mocked Celery).
- **Flake hunt:** run the full api+web suites 3× consecutively; quarantine-and-fix anything non-deterministic (timing-dependent SSE tests are prime suspects).
- Mutation-style spot check on the two most safety-critical modules (fill policy, redaction): deliberately break the code locally, confirm a test fails, revert. If a break survives, write the missing test.

## Out of Scope
- Coverage % vanity targets across the whole codebase.
- E2E expansion (Mission 26).
- Testing-library migrations or framework swaps.

## Starting Checklist
1. Check for coverage tooling: `grep -rn "pytest-cov\|coverage" apps/api/pyproject.toml apps/worker/pyproject.toml` and `grep -n "coverage" apps/web/vitest.config.ts`.
2. `ls apps/web/src/**/*.test.* -R` (or glob) — inventory existing web tests.
3. Write the critical-path list from MISSION_INDEX definition-of-done + `pytest -m policy --collect-only` output + this pack's change log (git log `[pack-` commits).
4. Read `apps/api/tests/conftest.py` and web test setup for available fixtures/harnesses.
5. Note CI duration budget (current pipeline length) — added tests must not blow it up; mark slow tests appropriately.

## Tasks
1. Produce the coverage map (`docs/polish-pack/notes/25_coverage_map.md`): critical path × current coverage × verdict.
2. Write web component tests for the listed gaps (priority order above).
3. Write API targeted tests for under-covered critical branches.
4. Run the 3× flake hunt; fix root causes (fake timers, deterministic fixtures, explicit waits).
5. Mutation spot-check on fill policy + redaction; add tests for any surviving break.
6. Wire coverage reporting into CI as informational (not gating) if cheap; otherwise document the local command.

## Self-Improvement Loop
1. Inspect the next uncovered critical branch.
2. Identify the highest-impact missing test (what failure would hurt users most?).
3. Write the smallest meaningful test (assert behavior, not implementation).
4. Validate it fails on broken code (mutate or stub) and passes on real code.
5. Update the coverage map.
6. Repeat until every critical-path row is covered or consciously waived.

## Validation
- `cd apps/api && pytest -q` ×3 consecutive green; same for worker.
- `cd apps/web && pnpm test` ×3 consecutive green; `pnpm typecheck && pnpm lint:strict && pnpm build`.
- `make test-policy && make test-fixtures`
- Coverage reports archived in the notes file (summary tables, not raw HTML).

## Acceptance Criteria
1. Coverage map complete; every critical path covered or waived with rationale.
2. Web tests exist for all pack-introduced behavior listed in Scope.
3. Zero flakes across 3× consecutive full runs.
4. Mutation spot-checks pass (no silent survivors) on fill policy and redaction.
5. CI duration within +25% of pre-mission baseline; all gates green.

## Documentation Requirements
- `docs/polish-pack/notes/25_coverage_map.md`.
- Testing conventions delta in `docs/architecture/testing.md` if patterns were established.

## Git Workflow
`git status` first; commits per test cluster (`test(web): consent sheet state coverage [pack-25]`); flake fixes separate from new tests; push after gates.

## Production Guidance
No deployment — test-only changes. If a test exposes a live product bug, fix it under Mission 31 rules with its own commit and deployment decision.
