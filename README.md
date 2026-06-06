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
| `make seed` | Insert demo profile + job targets |
| `make schemas-export` | Regenerate TypeScript types from `packages/schemas` |

Without Make:

```bash
docker compose --env-file .env -f infra/compose.yaml --profile full up -d --build
```

If default ports are busy, copy `.env.example` to `.env` and set `POSTGRES_HOST_PORT`, `REDIS_HOST_PORT`, `API_HOST_PORT`, `MINIO_API_HOST_PORT`, and `MINIO_CONSOLE_HOST_PORT`.

## Where things live

```
apps/
  api/      FastAPI — /healthz, /readyz
  worker/   Celery + Playwright (Chromium)
  web/      Next.js placeholder (Mission 02)
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

## Development gates

- Backend: `ruff`, `mypy`, `pytest`
- Pre-commit: `pre-commit install` then hooks run on commit
- CI: `.github/workflows/ci.yml`
- Architecture notes: [`docs/architecture/`](docs/architecture/) (design reviews, policy baseline)

Full product spec and mission sequence: [`docs/MASTER_PLAN.md`](docs/MASTER_PLAN.md) and [`docs/MISSION_INDEX.md`](docs/MISSION_INDEX.md).
