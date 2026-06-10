# Mission 02: Re-certify the Quality Gate Baseline

## Purpose
Every later mission validates against the same gate set. This mission runs every gate the repo defines — locally and in CI — records the exact passing commands and durations, and fixes anything red. It turns "CI was green at M34 closeout" into "all gates are green *now*, on this machine, post in-flight landing."

## Context From Audits
Application audit §6 and §15: gates exist (`make lint`, `make test`, `make test-fixtures`, `make test-policy`, web `typecheck`/`lint:strict`/`test`/`build`/`check:motion`/`check:bundles`, Playwright e2e) and CI was green at mission 34, but the in-flight diff touched tests (`test_tenant_isolation.py`, `test_golden_path_integration.py`, `test_analytics*.py`) and worker DB-URL handling. §21 acceptance criteria 2–4 define the target state.

## Scope
- Run every defined gate for api, worker, web, fixtures, and e2e; fix failures.
- Verify local gate behavior matches `.github/workflows/ci.yml` (same env vars, same steps) and close any drift.
- Record a canonical "full gate" command list in `docs/polish-pack/notes/` (create the folder) for reuse by all later missions.
- Verify `make doctor` reports a healthy toolchain on this host.

## Out of Scope
- Adding new tests (Missions 25–26).
- Performance tuning of slow tests (note durations only).
- Touching application behavior except where required to fix a red gate.

## Starting Checklist
1. Read `.github/workflows/ci.yml` end to end — note required services (Postgres, Redis, MinIO via docker run), env vars (`VAULT_ENCRYPTION_KEY`, `DATABASE_URL` with `?ssl=disable`, `FIXTURE_ATS_PORT=8765`), and every gate step.
2. Read the `Makefile` targets: `lint`, `test`, `test-fixtures`, `test-policy`, `web-lint`, `web-build`, `migrate-check`.
3. Confirm infra is up: `make infra`, then `curl http://localhost:8000/healthz` only if the api container is also running (`make up`).
4. Check Python env: `pip install -q "./apps/api[dev]" "./apps/worker[dev]"` plus shared packages per README (`packages/schemas`, `extraction`, `forms`, `fill`, `recovery`, `verification`).

## Tasks
1. `make infra` (Postgres/Redis/MinIO) and `make migrate`; run `make migrate-check` — drift here blocks everything.
2. Backend gates: `cd apps/api && ruff check src tests && mypy src && pytest -q`; same for `apps/worker`.
3. Fixture + policy gates: `make test-fixtures`, `make test-policy`.
4. Web gates: `cd apps/web && pnpm install && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles`.
5. E2E: `pnpm test:e2e:install` once, then `pnpm test:e2e` (Playwright; check `playwright.config.ts` for whether it needs the dev server or starts one).
6. Fix every failure at the root cause; if a failure is environmental (e.g., Windows path issues), fix the harness, not the test, and document it.
7. Write `docs/polish-pack/notes/gates.md`: the exact command sequence, prerequisites, and typical durations. Later missions reference this file as "the full gate."
8. Push and confirm GitHub CI green.

## Self-Improvement Loop
1. Inspect the current gate output.
2. Identify the highest-impact red or flaky gate.
3. Make the smallest coherent fix.
4. Re-run that gate, then the full set it belongs to.
5. Document the fix.
6. Repeat until every gate passes twice consecutively (flake check) or a blocker is documented.

## Validation
The full list compiled into `docs/polish-pack/notes/gates.md`; at minimum:
- `make migrate-check`
- api/worker: `ruff check src tests && mypy src && pytest -q`
- `make test-fixtures && make test-policy`
- web: `pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles && pnpm test:e2e`
- GitHub Actions green on the pushed commit.

## Acceptance Criteria
1. Every gate above passes locally, twice in a row, with zero skips that aren't already marked and justified in-repo.
2. CI is green on `main`.
3. `docs/polish-pack/notes/gates.md` exists and is accurate (a fresh shell following it succeeds).
4. Any intentionally-deferred failure is recorded as a blocker with file/test name and reason.

## Documentation Requirements
- `docs/polish-pack/notes/gates.md` (new).
- README corrections if any documented command no longer works as written.

## Git Workflow
`git status` first; keep fixes in small commits per failing gate (`fix(test): … [pack-02]`, `chore(ci): … [pack-02]`). Review diffs before staging; commit bodies state which gate was red, the root cause, the fix, and the validation rerun. Push when all gates pass; never bypass hooks.

## Production Guidance
Do not deploy after this mission unless a gate fix corrected a defect that is live in production (e.g., a worker DB-URL bug) — in that case follow `docs/runbooks/deploy.md` and run `bash scripts/railway-smoke.sh` afterward.
