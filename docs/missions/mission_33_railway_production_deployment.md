# Mission 33 — Railway Production Deployment

## Task list
- [x] Railway project layout + service configs (`infra/railway/*.railway.toml`)
- [x] Production Dockerfiles: API entrypoint (migrate + `$PORT`), web standalone, worker headless + health
- [x] Cross-service env template (`infra/railway/variables.example.env`); secrets only in Railway
- [x] Migrations on API deploy (`alembic upgrade head` before uvicorn)
- [x] Healthchecks: API `/healthz` + `/readyz`, web `/api/health`, worker `/readyz` (Celery)
- [x] Production boot guards: no `DEV_AUTH_BYPASS`, no `AUTH_MODE=dev`, no placeholder secrets
- [x] Managed Postgres SSL via `asyncpg_connect_args`
- [x] Deploy runbook + `scripts/railway-smoke.sh`
- [x] Storage decision documented: MinIO-on-volume (default) vs Railway buckets
- [x] Staging/production promotion + backup/restore documented in runbook

## Storage decision

**Staging uses Railway native storage buckets** (`jober-artifacts`, region `sjc`) with S3-compatible `MINIO_*` variables and `MINIO_REGION=auto`.

**Production default (documented):** MinIO on a Railway volume for parity with local compose. Railway buckets remain a supported alternative — see `docs/runbooks/deploy.md`.

## Railway project

- Project: [jober](https://railway.com/project/b06c0938-d4f7-4f77-bcb7-e2eb42c0b4be)
- Staging API: `https://api-staging-a8ca.up.railway.app` (`/readyz` green after bucket creds fix)
- Staging web: `https://web-staging-763f.up.railway.app`

## Acceptance criteria
- [x] Staging API + web deploy healthy; Postgres/Redis/bucket `/readyz` green
- [x] Worker deploy healthy on staging (`SUCCESS` after psycopg URL fix)
- [x] Migrations run automatically in API entrypoint before uvicorn
- [x] Golden path on staging: `scripts/railway-smoke.sh` (readiness + marketing funnel); fixture pipeline in CI `test_golden_path_integration.py`
- [x] Production startup fails on placeholder secrets / dev bypass (unit tests)
- [x] Backups + restore documented in `docs/runbooks/deploy.md`

## CI / local gates
- `pytest apps/api/tests/test_startup_secrets.py apps/api/tests/test_db_connect.py`
- Docker builds: `infra/docker/Dockerfile.api`, `Dockerfile.web.prod`, `Dockerfile.worker`

## Mission 99 (post–M33)

- [x] Ruff: `monpatch` typo in `test_db_connect.py`
- [x] Mypy: production secrets validation without untyped lambdas
- [x] Worker SSL: skip `sslmode=require` when `ssl=disable` in local/CI URLs
- [x] Tests: async `check_minio` + production secrets fixture fields
- [x] `test_config_database_url.py` — Railway `postgresql://` rewrite
- [x] `railway-smoke.sh` — landing + signup funnel on staging web
- [x] README + Design Council (19/20) + deploy runbook creds pitfall

**M99 CI:** [run 27271410323](https://github.com/HiNala/jober/actions/runs/27271410323) (green on `6bc3562`); M99 follow-up commits pending CI.
