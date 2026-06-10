# Mission 01: Land In-Flight Changes and Restore a Clean Main

## Purpose
`main` carries 18 modified files and 5 untracked paths of unvalidated work (formatting normalization, a local-dev web Docker service, a screenshot pipeline, the first product-polish component). Nothing else in this pack can be validated or cleanly diffed until this is triaged, validated, and committed (or deliberately discarded). This mission establishes the clean baseline every later mission depends on.

## Context From Audits
Application audit §7.1 and §19 risk #1: uncommitted work is the top risk. The diff splits into four logical groups: (a) ruff-style reformatting across API services/tests plus a new worker test (`apps/worker/tests/test_db_url.py` gains a `?ssl=disable` case); (b) local web dev infrastructure (`infra/docker/Dockerfile.web`, compose `web` service, root `compose.yaml` include); (c) screenshot/review pipeline (`apps/web/scripts/capture-screenshots.mjs`, `docs/screenshots/` with 23 PNGs + `UI-REVIEW.md`); (d) the start of UI polish (`apps/web/src/components/product/announcement-banner.tsx`) and an `infra/railway/minio.railway.toml` change.

## Scope
- Triage, validate, and commit the current working tree as separate logical commits.
- Verify `.gitignore` covers build artifacts present in the tree (`apps/web/test-results/`, `tsconfig.tsbuildinfo`, `.mypy_cache/`, `docs/screenshots/prod/*.png` — decide whether screenshots belong in git or only locally; they are referenced by `UI-REVIEW.md`, so committing them is the default).
- Confirm the new compose `web` service and `Dockerfile.web` actually work (`docker compose up web` from repo root).
- Decide the fate of `announcement-banner.tsx`: if unused, leave uncommitted work out by either wiring it minimally where intended or parking it in a clearly-named branch — do not commit dead code to `main`.

## Out of Scope
- Any UI polish beyond what the banner component strictly needs to be non-dead.
- Refactoring the formatting-touched services.
- Deploying the `minio.railway.toml` change (validated later in Mission 30).

## Starting Checklist
1. `git status --short` and `git diff` — read the full diff, group by intent.
2. `git log --oneline -15` — understand what the recent hotfix commits already landed.
3. Read `infra/docker/Dockerfile.web`, root `compose.yaml`, the compose `web` service block in `infra/compose.yaml`.
4. Read `apps/web/scripts/capture-screenshots.mjs` to learn how it is invoked (it is used by many later missions).
5. `grep -n "announcement-banner" -r apps/web/src` — find whether the banner is imported anywhere.
6. Check `.gitignore` against stray artifacts.

## Tasks
1. Run the API/worker gates against the formatting diff: `cd apps/api && ruff check src tests && mypy src && pytest -q`, then the same in `apps/worker` (start infra first with `make infra` if tests need Postgres/Redis/MinIO).
2. Commit group (a) as `chore(format): normalize ruff style across api services and tests` including the new worker SSL test (mention it in the body).
3. Validate group (b): from repo root run `docker compose up -d web` (or `make up`), confirm `http://localhost:3000` serves with hot reload, then commit as `feat(dev): dockerized web dev service with root compose entrypoint`.
4. Commit group (c): screenshot script + `docs/screenshots/` as `docs(design): production screenshot pipeline and UI review`.
5. Resolve group (d): wire or park `announcement-banner.tsx`; validate `infra/railway/minio.railway.toml` against `docs/runbooks/deploy.md` expectations; commit each with accurate messages.
6. Add any missing `.gitignore` entries; `git rm --cached` anything that should never have been tracked.
7. Confirm `git status` is clean and CI passes on the pushed result.

## Self-Improvement Loop
1. Inspect the current implementation (the working tree and each candidate commit).
2. Identify the highest-impact gap within this mission scope (e.g., a diff group that fails a gate).
3. Make the smallest coherent improvement (fix or split the offending hunk).
4. Validate the change with the commands below.
5. Document the result in the commit body.
6. Repeat until the acceptance criteria are satisfied or no further safe improvement remains.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q`
- `cd apps/worker && ruff check src tests && mypy src && pytest -q`
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build`
- `docker compose up -d web` from repo root; load `http://localhost:3000`; edit a component and confirm hot reload.
- `git status --short` returns nothing after the final commit.
- CI on GitHub (`.github/workflows/ci.yml`) green for the pushed commits.

## Acceptance Criteria
1. Working tree is clean; every former in-flight change is committed in a logical group or parked on a named branch with a one-line rationale in the commit/branch description.
2. All lint/type/test gates pass locally for api, worker, and web.
3. The dockerized web dev flow works on this Windows host (documented in README if the root `compose.yaml` changes the quick-start).
4. No dead code committed to `main`.

## Documentation Requirements
- If the root `compose.yaml` or `make up` behavior changed, update the README Quick start section.
- Add a dated note at the top of `docs/screenshots/UI-REVIEW.md` stating it is the driving document for missions 04–10 and 27–28 of this pack.

## Git Workflow
Check `git status` before starting. Keep each commit to one logical group above; review `git diff --staged` before each commit. Commit messages include the mission tag, e.g. `chore(format): … [pack-01]`, with a body covering what changed, why, validation performed, and known follow-ups. Push to `origin main` after gates pass — this repo's convention (MASTER_PLAN §10) is push at mission boundaries. Never use `--no-verify`.

## Production Guidance
Do not deploy after this mission. The `minio.railway.toml` change must wait for the release-oriented missions; everything else is dev-local or docs.
