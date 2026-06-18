# Canonical quality gates — Jober polish pack

**Created:** 2026-06-11 (Mission 02) · **CI reference:** `.github/workflows/ci.yml`

Run the full gate set before every mission boundary and in every Mission 31 continuation loop. Gates must pass **twice consecutively** on the host doing the work (flake check).

## Prerequisites

1. **Toolchain:** Python 3.12+, Node 22+, pnpm 9+, Docker Compose v2, `ruff`/`mypy`/`pytest` (install via `pip install "./apps/api[dev]" "./apps/worker[dev]"` plus shared packages — see CI install step).
2. **Infra running** (Postgres, Redis, MinIO + bucket):
   ```bash
   docker compose --env-file .env --profile infra up -d postgres redis minio createbuckets
   ```
   On this Windows host, `.env` maps non-default host ports (`POSTGRES_HOST_PORT=5434`, `REDIS_HOST_PORT=6381`, `MINIO_API_HOST_PORT=9010`). **Keep infra up for the entire gate run** — stopping containers mid-run causes `ConnectionRefused` in API tests.
3. **Environment variables** (match CI; adjust host ports from `.env`):

   | Variable | CI value | This host (`.env`) |
   |----------|----------|-------------------|
   | `DATABASE_URL` | `postgresql+asyncpg://jober:jober@localhost:5432/jober?ssl=disable` | `...@localhost:5434/...` |
   | `REDIS_URL` | `redis://localhost:6379/0` | `redis://localhost:6381/0` |
   | `MINIO_ENDPOINT` | `localhost:9000` | `localhost:9010` |
   | `MINIO_ACCESS_KEY` | `minioadmin` | same |
   | `MINIO_SECRET_KEY` | `minioadmin` | same |
   | `MINIO_BUCKET` | `jober-artifacts` | same |
   | `MINIO_SECURE` | `false` | same |
   | `VAULT_ENCRYPTION_KEY` | `w-CndrrLpumBk62xq-1SBueyOre-DhzV_gGc86LmvnQ=` | same |
   | `FIXTURE_ATS_PORT` | `8765` | same |
   | `SECRET_KEY` | (dev) any non-placeholder | `local-dev-secret` |
   | `JOBER_ENV` | `development` (local) | same |

4. **Web typecheck:** If `docker compose --profile full up web` was used, delete `apps/web/.next` before `pnpm typecheck` — Windows bind-mount + polling can corrupt generated `.next/dev/types/validator.ts`.

## Full gate sequence

Run from **repo root** unless noted. Recorded durations are from Mission 02 on Windows (2026-06-11); Linux CI is faster.

### 0. Doctor (optional sanity)

```bash
make doctor          # Linux/macOS/Git Bash
```

Windows without Make: verify `docker`, `docker compose`, `python` 3.12, `ruff`, and that infra containers are healthy (`docker compose ps`).

### 1. Migration drift (~25s)

```bash
make migrate-check
```

Equivalent:
```bash
cd apps/api && alembic upgrade head && python scripts/check_migration_drift.py
```

### 2. Backend lint (~2 min)

```bash
make lint    # includes web-lint; or split below
```

API + worker only:
```bash
cd apps/api && ruff check src tests && mypy src
cd apps/worker && ruff check src tests && mypy src
```

### 3. Backend tests (~3–4 min each run × 2)

```bash
make test
```

Equivalent (with env vars set):
```bash
cd apps/api && pytest -q
cd apps/worker && pytest -q
```

**Current results (Mission 28):** api 83 passed / 313 skipped; worker 22 passed.

### 4. Fixture pipeline (~90s)

```bash
make test-fixtures
```

### 5. Policy suite (~50s)

```bash
make test-policy
```

**Current results (Mission 28):** 19 passed.

### 6. Web gates (~7 min)

```bash
cd apps/web
pnpm install --frozen-lockfile   # CI only; skip if deps current
pnpm typecheck
pnpm lint:strict
pnpm check:motion
pnpm test
pnpm build
pnpm check:bundles
```

Or `make web-lint` + `make web-build` + motion/bundles on Linux.

**Current results (Mission 28):** `pnpm test` **128 passed**; `check:bundles` 2564 KB / 2650 KB budget.

### 7. E2E — marketing tier (~1 min after browser install)

```bash
cd apps/web
pnpm test:e2e:install    # once per machine/CI image
CI=true pnpm test:e2e:marketing
```

Playwright starts `pnpm start` via `playwright.config.ts` unless `PLAYWRIGHT_SKIP_WEB_SERVER=1`. The `marketing` project excludes `*.fullstack.spec.ts`.

**Windows:** With `CI=true`, Playwright refuses to reuse an existing server on port 3000. Stop any stale `next start` / dev server on `:3000` before e2e, or e2e fails with *"port already used"*. Without `CI`, `reuseExistingServer: true` applies but the running server must be a fresh production build with `NEXT_PUBLIC_DEV_AUTH_BYPASS=true` (see `playwright.config.ts` webServer env).

**Current results (Mission 28):** marketing e2e **71 passed** (CI); fullstack e2e **5 passed** (Mission 26).

### 8. E2E — full-stack tier (Mission 26)

Requires Postgres, Redis, MinIO, API (`:8000`), Celery worker + beat, fixture ATS (`:8765`), and e2e seed:

```bash
# Infra (default ports — match CI)
docker compose --profile infra up -d postgres redis minio createbuckets

export DATABASE_URL=postgresql+asyncpg://jober:jober@localhost:5432/jober?ssl=disable
export REDIS_URL=redis://localhost:6379/0
export MINIO_ENDPOINT=localhost:9000
export VAULT_ENCRYPTION_KEY=w-CndrrLpumBk62xq-1SBueyOre-DhzV_gGc86LmvnQ=
export SECRET_KEY=local-dev-secret
export DEV_AUTH_BYPASS=true
export LLM_PROVIDER=template

cd apps/api && alembic upgrade head && python scripts/seed_e2e.py
python apps/web/e2e/scripts/build-e2e-workbook.py

# Three terminals (or compose --profile full):
make fixture-serve
cd apps/api && uvicorn jober_api.main:app --port 8000
cd apps/worker && celery -A jober_worker.celery_app worker --loglevel=info

cd apps/web && pnpm build
E2E_FULL_STACK=1 CI=true pnpm test:e2e:fullstack
```

Optional auth lifecycle spec: `E2E_AUTH_NATIVE=1` with `AUTH_MODE=native`, API `DEV_AUTH_BYPASS=false`, and web built without `NEXT_PUBLIC_DEV_AUTH_BYPASS`.

CI job: `e2e-fullstack` in `.github/workflows/ci.yml` (runs on every PR/main push).

## One-liner summary (Mission 31 / pre-push)

```text
make migrate-check
make lint && make test && make test-fixtures && make test-policy
cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles && pnpm test:e2e:marketing
```

On Windows without Make, run each step above with env vars exported and `docker compose --profile infra up -d` first.

## CI parity notes

| CI job | Local gate |
|--------|------------|
| `backend` → Alembic + drift | `make migrate-check` |
| `backend` → ruff/mypy/pytest | `make lint` + `make test` |
| `backend` → package pytest | covered by `make test-fixtures` + api install |
| `policy` → `pytest -m policy` | `make test-policy` |
| `web` → typecheck/lint/test/build/bundles/e2e marketing | web §6–7 |
| `e2e-fullstack` → fixture journeys | web §8 |
| `detect-secrets` | pre-commit / `detect-secrets scan --baseline .secrets.baseline` |

CI uses default ports (5432/6379/9000); local `.env` overrides require the adjusted `DATABASE_URL` / `REDIS_URL` / `MINIO_ENDPOINT` in the table above.

## Known blockers / waivers

| Item | Status | Mission | Notes |
|---|---|---|---|
| Legal counsel review of `/acceptable-use` | Open (external) | 30 | Waivable for soft launch |
| Lighthouse CWV production verification | Open | 30 | Automated blocked by bot interstitial; manual PSI post-deploy |
| Per-route OG image assets | Deferred | Post-launch | Mission 27 deferral |
| `auth-journey` fullstack in CI | Waiver | 26 | Requires `E2E_AUTH_NATIVE=1` + native auth stack |
| App-route axe coverage | Deferred | Post-launch | Marketing axe green; app routes incremental |
