# Jober

Assisted application autopilot for high-volume, high-quality job applications.

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
| `make test-fixtures` | Fixture catalog + pipeline + browser tests |
| `make test-policy` | Blocking policy suite (`pytest -m policy`) |
| `make fixture-serve` | Local ATS fixture server on :8765 |
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
fixtures/
  ats/      Synthetic ATS pages for offline CI (see `docs/architecture/testing.md`)
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

Routes: `/` (marketing landing), `/pricing`, `/privacy`, `/terms`, `/signup`, `/login`, `/dashboard`, `/queue`, `/discover`, `/library`, `/search`, `/settings`, `/kitchen-sink` (component catalog). `/documents` and `/vault` redirect into Library and Settings.

**Marketing (Missions 29–30):** Public site at `/` (landing), `/features`, `/how-it-works`, `/faq`, `/pricing`, `/blog`, plus `/privacy`, `/terms`, and `/acceptable-use` (draft legal — requires counsel before launch). Pricing mirrors API plan limits (Free: 20 runs/mo, 5 batch, $5 LLM; Pro: 500/100/$50). CTA clicks emit `feature.use` (consent-gated); UTM params persist in-session for signup attribution. Set `NEXT_PUBLIC_SITE_URL` for sitemap/OG. See `docs/missions/mission_29_marketing_landing.md` and `mission_30_marketing_site.md`.

**Design system (Mission 16):** tokens in `apps/web/src/lib/design/tokens.ts`; shared page states in `components/states/page-states.tsx`. Settings shows plan usage and tenant policy from the API (Mission 15).

**Motion (Mission 19):** central vocabulary in `apps/web/src/lib/design/motion.ts` — see `docs/architecture/motion.md`. Feature components must use motion tokens (`pnpm check:motion`); `prefers-reduced-motion` is honored globally.

**Auth (Mission 20):** native email/password with Argon2id, Redis cookie sessions, and CSRF. Set `AUTH_MODE=native` for real auth; `DEV_AUTH_BYPASS=true` (API) + `NEXT_PUBLIC_DEV_AUTH_BYPASS=true` (web) for frictionless local dev. Production refuses `DEV_AUTH_BYPASS`. See `docs/missions/mission_20_native_auth.md`.

**Google OAuth (Mission 21):** optional “Continue with Google” alongside native auth. Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` (API callback), then `NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED=true` on the web app to show provider buttons. Linking a verified native account requires password confirmation at `/link-google`. Manage linked methods in Settings. See `docs/missions/mission_21_google_oauth.md`.

**Discover (Mission 23):** `/discover` unifies board search and XLSX import into named target lists with dedupe, fit signals, saved searches, list refresh, and batch launch (`filters.job_list_id`). See `docs/missions/mission_23_unified_job_discovery.md`.

**Workspace shell (Mission 17):** three-pane layout in `components/workspace/` — collapsible nav, center work column with command bar, resizable right canvas (browser/doc preview). Layout prefs persist in `localStorage`. Shortcuts: ⌘/Ctrl-B (nav), ⌘/Ctrl-\\ (canvas), ⌘/Ctrl-/ (command input).

**Live canvas (Mission 18):** on `/runs/[id]`, the right canvas streams screenshots via SSE, shows artifact grid/layers, document and fill-diff views, and a combined review-and-submit surface. Components live in `components/canvas/`.

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
pip install "./packages/schemas" "./packages/extraction" "./packages/forms"
pip install "./apps/api[dev]"
```

Browser extraction requires the worker (`make up` or `celery -A jober_worker.celery_app worker`). Use `fixture_html` in the extract body for CI-safe tests without Playwright.

## Form discovery (Mission 07)

Scan apply forms into typed field observations with confidence scores and redacted value previews.

| Endpoint | Purpose |
|----------|---------|
| `POST /api/job-targets/{id}/discover-form` | Scan fixture HTML → `FormFieldObservation` rows |
| `GET /api/job-targets/{id}/field-observations` | Latest discovery inventory for review |
| `PATCH /api/job-targets/field-observations/{id}` | Edit mapping/status; `remember: true` stores label→field memory |

Sensitive EEO/salary fields always surface as `needs_review`. High-confidence public fields are eligible for auto-fill (`skipped` status). Review mapped fields in the job detail drawer before Mission 08 fill.

After pulling Mission 07+, run `make migrate` once (adds `field_mapping_memory`).

## Form filling (Mission 08)

Fill discovered fields via typed Playwright actions (label/role locators first) and attach resume + cover letter from MinIO.

| Endpoint | Purpose |
|----------|---------|
| `POST /api/job-targets/{id}/fill-form` | Fill via `fixture_html` (CI) or enqueue browser worker |

Each filled field stores a masked `fill_diff` (`proposed_redacted` vs `actual_redacted`) in observation evidence for Mission 09 review. Login/CAPTCHA/sensitive fields create human checkpoints — never bypassed.

Local install also needs `packages/fill` and Playwright Chromium (`playwright install chromium`).

## Review & submit (Mission 09)

After fill, run readiness verification, review masked diffs in the job drawer, then submit manually. Default policy is `review_before_submit`; `auto_submit` requires explicit per-batch opt-in and is never the global default.

| Endpoint | Purpose |
|----------|---------|
| `POST /api/job-targets/{id}/verify-ready` | Readiness checks → `review_and_submit` on pass (continues latest fill run) |
| `GET /api/job-targets/{id}/review` | Human summary, fill diff, readiness report |
| `POST /api/application-runs/{id}/submit` | Human submit + confirmation capture |
| `POST /api/application-runs/{id}/skip-submit` | Skip without submitting |

Local install also needs `packages/verification` (`pip install -e packages/verification`).

## Retry & recovery (Mission 10)

Recovery loop enforces attempt budgets (3 normal + 1 alternate), classifies failures, writes self-assessments, and produces actionable failure reports. CAPTCHA/login/2FA never retry automatically.

| Endpoint | Purpose |
|----------|---------|
| `POST /api/job-targets/{id}/recovery-fill` | Fixture recovery loop with budgets |
| `GET /api/job-targets/{id}/failure-report` | Latest failure report for job drawer |
| `POST /api/application-runs/{id}/resume` | Resume from last checkpoint |
| `GET /api/recovery/failure-analytics` | Failure classes by ATS + circuit alerts |

Local install also needs `packages/recovery` (`pip install -e packages/recovery`). Run `make migrate` for Mission 10 schema (`failure_events`, checkpoint columns).

## Live run console (Mission 11)

Watch runs in the web console at `/runs/{run_id}` or the interactive terminal via `make tui` (no CLI flags required).

| Endpoint | Purpose |
|----------|---------|
| `GET /api/application-runs/{id}/console` | Snapshot + scrub timeline + artifact URLs |
| `GET /api/application-runs/{id}/events` | SSE stream (`after_seq` / `Last-Event-ID` for reconnect) |
| `GET /api/console/recent-events` | Dashboard feed of latest run events across jobs |
| `POST /api/application-runs/{id}/checkpoints/{id}/resolve` | Approve / deny / edit / skip (web + TUI) |

Run `make migrate` for Mission 11 (`run_events` table). Install TUI: `pip install -e apps/tui`.

## Batch ops & scheduling (Mission 13)

Queue batches of applications with Redis-backed pacing: global pause/resume, per-domain locks (never parallel applies to the same ATS host), site cooldowns, quiet hours, and monthly LLM budget hard-stop.

| Endpoint | Purpose |
|----------|---------|
| `POST /api/batches/preview` | Filter jobs; excludes already-applied and prior successful runs |
| `POST /api/batches` | Create batch (`dry_run` / `review_before_submit` / `auto_submit`) |
| `POST /api/batches/{id}/enqueue` | Start batch (respects quiet hours for non-dry-run) |
| `POST /api/queue/pause-all` / `resume-all` | Global queue control |
| `GET /api/dashboard/summary` | Live metrics + worker capacity |
| `GET /api/batches/daily-plan` | Proposed Priority-A plan + pacing note |

**Dashboard:** `/dashboard` shows live metrics, worker pool capacity, and batch controls (dry-run enqueue, pause/resume).

`auto_submit` is never the default; set `AUTO_SUBMIT_OPT_IN=true` only when you explicitly want opt-in auto-submit batches. Worker image installs `jober-api` alongside shared packages so Celery beat can run the batch orchestrator.

After pulling Mission 13+, run `make migrate` once (adds `application_batches`, `batch_items`).

## Security & privacy (Mission 14)

Write-time redaction masks secrets and PII in run events, browser events, and LLM audit rows. Set `JOBER_ENV=production` and real `VAULT_ENCRYPTION_KEY` / `SECRET_KEY` before deploying; use `REQUIRE_SECRETS=true` to enforce locally.

| Endpoint | Purpose |
|----------|---------|
| `POST /api/privacy/runs/{id}/purge` | Delete run + MinIO artifacts |
| `POST /api/privacy/cleanup` | Purge runs by date/status filters |
| `GET /api/privacy/export-all` | Export profiles, jobs, run metadata |
| `DELETE /api/privacy/delete-all` | Wipe local data (`confirm: DELETE ALL MY DATA`) |
| `PUT /api/application-runs/{id}/browser-storage-state` | Save encrypted Playwright session after human login |

Env: `LOG_MODE=redacted` (default) or `debug` (more detail, still scrubs secrets), `PRESIGNED_URL_TTL_MINUTES=15`. See [`docs/architecture/threat-model.md`](docs/architecture/threat-model.md).

## Multi-tenant & billing (Mission 15)

API routes under `/api/*` require authentication. **Native auth (Mission 20):** set `AUTH_MODE=native` for cookie sessions; use `DEV_AUTH_BYPASS=true` locally to skip sign-in. **Header dev mode:** `X-Jober-Tenant-Id` / `X-Jober-User-Id` (defaults seeded by migration). **Clerk (optional):** `AUTH_MODE=clerk` with JWT issuer/secret.

| Endpoint | Purpose |
|----------|---------|
| `GET /api/billing/usage` | Monthly runs, documents, LLM cost vs plan limits |
| `GET/PUT /api/settings/policy` | `review_before_submit` default, opt-in `auto_submit`, retention |
| `POST /api/webhooks/stripe` | Subscription-driven plan upgrades/downgrades |
| `GET /api/privacy/export-all` | Tenant-scoped data export (audit logged) |
| `DELETE /api/privacy/delete-all` | Tenant-scoped wipe (`confirm: DELETE ALL MY DATA`) |

Plans: **Free** (5 jobs/batch, 20 runs/mo) vs **Pro** (100/batch, 500 runs/mo). MinIO keys are prefixed `tenants/{id}/`. Workers: set `BROWSERLESS_URL` for headless servers; local `PLAYWRIGHT_HEADED=true` unchanged.

Positioning: [`docs/architecture/product.md`](docs/architecture/product.md). Run `make migrate` after pull (adds `tenants`, `users`, `audit_log_entries`, `tenant_id` columns).

## Cover letters (Mission 05 + 24)

Generate grounded cover letters at `/documents` (Document Studio) or edit in the run canvas Documents tab.

| Endpoint | Purpose |
|----------|---------|
| `GET /api/documents/letter-options` | Templates (classic/modern/compact) + voice presets |
| `POST /api/documents/generate-cover-letter` | Draft with template/voice, regen, `run_id` linkage |
| `PATCH /api/documents/{id}` | Inline text edit, lock paragraphs, re-render + ATS refresh |
| `POST /api/documents/{id}/duplicate` | Reuse letter as seed for another job |
| `GET /api/documents?job_target_id=` | Version history for a job |
| `GET /api/documents/{id}/download/pdf` | Download rendered PDF (ATS-safe text) |

Mission 24: Settings global generate toggle + default template/voice; batch `filters.generate_cover_letter` override; per-run `PATCH /api/application-runs/{id}/run-options` (Default / Generate / Skip in run console); skip when form lacks `cover_letter_upload`; `ab_tracking` metadata for analytics.

Without `LLM_API_KEY`, the API uses a deterministic template provider (CI-safe). Optional env vars: `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_DRAFT_MODEL`, `LLM_SCORING_MODEL`, `LLM_MONTHLY_BUDGET_USD` (default $25). Calls log to `LlmCall`; exceeding the monthly cap returns HTTP 402.

## First-party analytics (Mission 25)

No Google Analytics, Segment, or third-party trackers. Events land in Postgres via same-origin `POST /api/events`.

| Piece | Location |
|-------|----------|
| Collector | `POST /api/events` (public; requires `jober_analytics_consent=1` cookie; honors DNT) |
| Client SDK | `apps/web/src/lib/analytics/sdk.ts` — batch + `sendBeacon`, anon id rotation |
| Server events | `emit_server_event` on signup, list create, run start, submit, letter generate |
| Rollups | Celery `analytics_daily_rollup` (02:15 UTC) → funnel, page, DAU/WAU/MAU, LLM cost tables |

Privacy: no raw IP stored (coarse geo only at ingest), PII keys blocked in event props, opt-in consent banner. Config: `ANALYTICS_ENABLED`, `ANALYTICS_RETENTION_DAYS`. Weekly Celery `analytics_retention_purge` deletes events older than the retention window.

## Analytics dashboards (Mission 26)

Rollup-backed dashboards at `/analytics` — no synchronous scans of raw `AnalyticsEvent` rows.

| Route | Who | Purpose |
|-------|-----|---------|
| `GET /api/analytics/me` | Signed-in user | Applications, letters, LLM cost vs budget, activity series |
| `GET /api/analytics/admin/funnel` | Admin | Signup funnel with per-step drop-off |
| `GET /api/analytics/admin/traffic` | Admin | Page views, DAU/WAU/MAU from daily rollups |
| `GET /api/analytics/admin/cost` | Admin | LLM spend reconciled against `LlmCall` |

Each view supports `start`/`end` query params, optional `compare_previous=true`, and `export.csv` download. Charts use Recharts with shared theme tokens (`apps/web/src/components/analytics/charts/`).

## RBAC & admin bootstrap (Mission 27)

Central permissions in `apps/api/src/jober_api/auth/permissions.py`. Every protected API route declares a permission; undeclared routes fail startup validation and are enforced via `Depends(require_permission)`.

| Role | Capabilities |
|------|----------------|
| `user` | Tenant-scoped workspace data (`authenticated`) |
| `admin` | Ops dashboard, analytics rollups, user directory, config, audit log |

First admin (only while none exist):

```bash
ADMIN_BOOTSTRAP_SECRET=your-one-time-secret python apps/api/scripts/bootstrap_admin.py --email you@example.com
```

Further admins: existing admin promotes via `/admin/users` or `PATCH /api/admin/users/{id}/role`. See `docs/architecture/rbac.md` for admin data boundaries.

## Admin dashboard (Mission 28)

Ops-first UI at `/admin` (admin role only): overview attention items, acquisition funnel, user directory with audited support view, runs/reliability, cost reconciliation, system health, and feature flags.

Key API routes: `GET /api/admin/overview`, `/api/admin/runs`, `/api/admin/acquisition`, `/api/admin/cost`, `/api/admin/system`, `GET/PATCH /api/admin/config/{key}`.

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
