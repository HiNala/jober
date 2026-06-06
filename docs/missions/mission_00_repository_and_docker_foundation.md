# Mission 00 — Repository & Docker Foundation

> **Agent contract.** Keep a live task list (below). Work each task to its acceptance criteria, committing per task. Do not mark the mission complete until every quality gate is green. If you finish early, run the iteration clause at the bottom.

## Objective
Stand up the `jober` monorepo, local infrastructure (Postgres, Redis, MinIO), service skeletons (api, worker, web), git hygiene, and a CI skeleton — so every later mission has a green baseline to build on.

## Dependencies
None. This is the first mission.

## Target layout
```
jober/
  apps/
    api/      (FastAPI)
    worker/   (Celery + Playwright)
    web/      (Next.js — scaffolded in Mission 02; placeholder dir for now)
  packages/
    schemas/  (shared types; populated in Mission 01)
  infra/
    docker/   (Dockerfile.api, Dockerfile.worker)
    compose.yaml
    nginx/
    backups/
  docs/       (MASTER_PLAN.md, MISSION_INDEX.md, missions/, architecture/)
  storage/local-dev/
  .gitignore
  .env.example
  README.md
  Makefile
```

## Task list
- [x] `git init` (default branch `main`). Add remote `origin` → `https://github.com/HiNala/jober.git`.
- [x] Write a comprehensive `.gitignore` covering: Python (`__pycache__`, `.venv`, `*.pyc`), Node (`node_modules`, `.next`, `dist`), env files (`.env`, `.env.*`, **but not** `.env.example`), MinIO/Postgres volumes, Playwright artifacts (`traces/`, `videos/`, `*.zip`), `storage/local-dev/`, secrets, OS cruft.
- [x] `.env.example` with every variable named but **no real values**: `DATABASE_URL`, `REDIS_URL`, `MINIO_*`, `LLM_API_KEY`/`OPENAI_API_KEY`/`ANTHROPIC_API_KEY`, `VAULT_ENCRYPTION_KEY`, `SECRET_KEY`, `LLM_DEFAULT_MODEL`, `LLM_MONTHLY_BUDGET_USD`.
- [x] `apps/api`: FastAPI app with `/healthz` (liveness) and `/readyz` (checks DB + Redis + MinIO reachable). `pyproject.toml` with `ruff`, `mypy`, `pytest` configured.
- [x] `apps/worker`: Celery app booting against Redis, with one `ping` task. Playwright + Chromium installed in the worker image (`playwright install --with-deps chromium`).
- [x] `apps/web`: placeholder directory only (scaffolded for real in Mission 02). Add a `.gitkeep`.
- [x] `infra/docker/Dockerfile.api` and `Dockerfile.worker` (multi-stage, non-root user).
- [x] `infra/compose.yaml`: services `postgres` (16), `redis` (7), `minio` (+ `createbuckets` init job for `jober-artifacts`), `api`, `worker`. Healthchecks on every service. Named volumes for pg/minio data.
- [x] `Makefile` with interactive-friendly targets: `make up`, `make down`, `make logs`, `make api-shell`, `make worker-shell`, `make fmt`, `make lint`, `make test`, `make migrate`. **No required flags** — sensible defaults.
- [x] `README.md`: one-command local start, prerequisites, and a "where things live" map.
- [x] `.github/workflows/ci.yml`: matrix that runs backend `ruff`/`mypy`/`pytest` and (stubbed for now) web checks. Spins up service containers for the API tests.
- [x] Pre-commit config (`ruff`, `ruff-format`, end-of-file-fixer, trailing-whitespace, detect-secrets).

## Acceptance criteria
- `make up` brings up postgres, redis, minio, api, worker; all healthchecks pass.
- `curl localhost:8000/healthz` → 200; `/readyz` → 200 only when DB/Redis/MinIO are reachable, 503 otherwise (verify by stopping redis).
- Worker logs show the `ping` task succeeding.
- MinIO console reachable; `jober-artifacts` bucket exists.
- `make lint` and `make test` pass (tests can be trivial here, but the harness must run).
- `git status` is clean except intended files; no `.env`, no secrets, no `node_modules`, no large binaries committed.
- CI is green on the first push.

## Notes & gotchas
- Pin Playwright + the matching Chromium revision; mismatches are a top source of worker flake.
- Use a **non-root** user in worker/api images; Playwright needs the right `--with-deps` system libs — install them in the image, not at runtime.
- MinIO: create the bucket via an init container so the stack is reproducible from scratch.
- Keep `compose.yaml` the single source of local truth; don't let services drift into ad-hoc `docker run`.

## Iteration clause
If all tasks pass, harden: add a `make doctor` target that checks tool versions and port conflicts and prints a friendly remediation list; add a `docker compose` profile for "infra-only" (no api/worker) so the web app can run against bare infra during Mission 02. Then run **Mission 99**.
