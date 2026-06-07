# Jober

Assisted application autopilot for high-volume, high-quality startup engineering job applications.

**Owner:** Brian Permut · **Repo:** [github.com/HiNala/jober](https://github.com/HiNala/jober)

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2)
- Python 3.12+ (for local lint/test without containers)
- Make (optional on Windows — use the `docker compose` commands below directly)

## Quick start

```bash
cp .env.example .env   # optional local overrides
make up                # builds and starts postgres, redis, minio, api, worker
```

Verify:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

- API: http://localhost:8000
- MinIO console: http://localhost:9001 (user/pass `minioadmin` / `minioadmin`)
- Postgres: `localhost:5432` (db/user/pass `jober` / `jober` / `jober`)

Infra only (for Mission 02 local web dev):

```bash
make infra
```

## Common commands

| Command | Description |
|---------|-------------|
| `make up` | Start full stack |
| `make down` | Stop stack |
| `make logs` | Tail service logs |
| `make lint` | Ruff + mypy (api + worker) |
| `make test` | Pytest (api + worker) |
| `make fmt` | Format + auto-fix |
| `make doctor` | Check tools and port conflicts |
| `make ping-worker` | Dispatch Celery ping task |
| `make migrate` | Apply Alembic migrations (`upgrade head`) |
| `make migrate-check` | Migrate + verify models match DB (drift check) |
| `make seed` | Insert demo profile + job targets |
| `make schemas-export` | Regenerate TypeScript types from `packages/schemas` |
| `make backup` | Snapshot Postgres + MinIO to `infra/backups/snapshots/` |
| `make restore` | Restore from `infra/backups/latest` or `SOURCE=...` |

Without Make:

```bash
docker compose --env-file .env -f infra/compose.yaml --profile full up -d --build
```

If default ports are busy, copy `.env.example` to `.env` and set `POSTGRES_HOST_PORT`, `REDIS_HOST_PORT`, `API_HOST_PORT`, `MINIO_API_HOST_PORT`, and `MINIO_CONSOLE_HOST_PORT`.

### Database & vault

```bash
make migrate          # apply schema
make seed             # demo UserProfile + JobTargets (idempotent)
make migrate-check    # migrate + fail if models drift from DB
```

Set `VAULT_ENCRYPTION_KEY` in `.env` before seeding profiles with sensitive EEO data (generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`). CI uses a fixed test key.

Backup/restore requires the infra profile (`make infra` or `make up`). On Windows, use Git Bash or WSL for `make backup`/`restore` (bash scripts).

## Where things live

```
apps/
  api/      FastAPI — health, import/export, job targets
  worker/   Celery + Playwright (Chromium)
  web/      Next.js app shell + design system (Mission 02)
packages/
  schemas/  Shared Pydantic types + `generated/types.ts` for the web app
infra/
  compose.yaml
  docker/   Dockerfiles
docs/
  MASTER_PLAN.md
  MISSION_INDEX.md
  missions/
```

## Web app (Mission 02+)

```bash
cd apps/web
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL if API is not on :8000
pnpm install
pnpm dev                     # http://localhost:3000
```

Routes: `/` (landing), `/dashboard`, `/queue`, `/documents`, `/vault`, `/settings`, `/kitchen-sink` (component catalog).

## Profile vault (Mission 04)

Upload a canonical resume (PDF/DOCX) and manage tiered profile fields at `/vault`.

| Endpoint | Purpose |
|----------|---------|
| `GET /api/profile` | Vault + completeness checklist |
| `PATCH /api/profile` | Public / preference fields |
| `PATCH /api/profile/vault` | Encrypted EEO values + consent flags |
| `POST /api/resumes` | Upload resume → MinIO + text/skills parse |

Set `VAULT_ENCRYPTION_KEY` before storing sensitive EEO answers. Sensitive fields default to **never auto-fill**; the fill policy returns `NEEDS_HUMAN` unless explicit consent + stored value exist.

After pulling Mission 04+, run `make migrate` once (adds `profile_common_answers`, `current_title`, `notice_period`).

## Job extraction (Mission 06)

Extract a normalized job profile from an apply URL (Playwright worker) or fixture HTML (CI-safe).

| Endpoint | Purpose |
|----------|---------|
| `POST /api/job-targets/{id}/extract` | Extract profile (`fixture_html` for tests) or enqueue browser run |
| `GET /api/job-targets/{id}/job-profile` | Cached profile for today |

Platform detection uses URL + DOM signatures (Ashby, Lever, Greenhouse, Workday, Jobvite, Personio, Teamtailor, generic). Login/CAPTCHA/2FA pages create a human checkpoint — never auto-bypassed.

After pulling Mission 06+, run `make migrate` once (adds `extracted_job_profile` columns on `job_targets`).

Local API dev (install shared packages before the API wheel):

```bash
pip install "./packages/schemas" "./packages/extraction"
pip install "./apps/api[dev]"
```

Browser extraction requires the worker (`make up` or `celery -A jober_worker.celery_app worker`). Use `fixture_html` in the extract body for CI-safe tests without Playwright.

## Cover letters (Mission 05)

Generate grounded cover letters at `/documents` (Document Studio).

| Endpoint | Purpose |
|----------|---------|
| `POST /api/documents/generate-cover-letter` | Draft letter + ATS score + PDF/DOCX keys |
| `GET /api/documents?job_target_id=` | List generated documents for a job |
| `GET /api/documents/{id}/download/pdf` | Download rendered PDF |
| `GET /api/documents/{id}/download/docx` | Download DOCX (optional) |

Without `LLM_API_KEY`, the API uses a deterministic template provider (CI-safe). Optional env vars: `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_DRAFT_MODEL`, `LLM_SCORING_MODEL`, `LLM_MONTHLY_BUDGET_USD` (default $25). Calls log to `LlmCall`; exceeding the monthly cap returns HTTP 402.

## Job spreadsheet import (Mission 03)

Import Brian's tracker workbook into Postgres and round-trip status back to XLSX.

**API** (prefix `/api`):

| Endpoint | Purpose |
|----------|---------|
| `POST /imports/jobs-xlsx?dry_run=true` | Preview column mapping + row counts |
| `POST /imports/jobs-xlsx` | Upsert JobTargets, CompanyBoards, CoverLetterAngles |
| `GET /exports/jobs-xlsx` | Download workbook (app-owned status/dates/notes) |
| `GET /job-targets` | List/filter queue rows |
| `PATCH /job-targets/{id}` | Update status, dates, notes |

**UI:** open `/queue` → **Import spreadsheet** (drag-drop) → confirm mapping → review warnings. Export from the queue header.

Sheets mapped: **Direct Job Leads** → `JobTarget`, **Company Boards** → `CompanyBoard`, **Cover Letter Angles** → `CoverLetterAngle`. Summary / Refresh Sources are stored as metadata only.

Local verification with the real workbook:

```bash
curl -X POST "http://localhost:8000/api/imports/jobs-xlsx?dry_run=true" \
  -F "file=@/path/to/tracker.xlsx"
```

Expect **155** job targets, **130** company boards, and **10** cover-letter angles on commit; re-import should update in place without duplicates.

## Development gates

- Backend: `ruff`, `mypy`, `pytest`
- Web: `pnpm typecheck`, `pnpm lint:strict`, `pnpm test`, `pnpm build` (in `apps/web`, or `make web-lint`)
- Pre-commit: `pre-commit install` then hooks run on commit
- CI: `.github/workflows/ci.yml`
- Architecture notes: [`docs/architecture/`](docs/architecture/) (design reviews, policy baseline)

Full product spec and mission sequence: [`docs/MASTER_PLAN.md`](docs/MASTER_PLAN.md) and [`docs/MISSION_INDEX.md`](docs/MISSION_INDEX.md).
