COMPOSE_FILE := infra/compose.yaml
COMPOSE_ENV := $(if $(wildcard .env),--env-file .env,)
COMPOSE := docker compose $(COMPOSE_ENV) -f $(COMPOSE_FILE)
COMPOSE_FULL := COMPOSE_PROFILES=full $(COMPOSE)
COMPOSE_INFRA := COMPOSE_PROFILES=infra $(COMPOSE)

.PHONY: up down logs infra api-shell worker-shell fmt lint test web-lint web-build migrate migrate-check seed schemas-export backup restore doctor ping-worker tui

up:
	$(COMPOSE_FULL) up -d --build

down:
	$(COMPOSE_FULL) down

logs:
	$(COMPOSE_FULL) logs -f --tail=200

infra:
	$(COMPOSE_INFRA) up -d postgres redis minio createbuckets

api-shell:
	$(COMPOSE_FULL) exec api sh

worker-shell:
	$(COMPOSE_FULL) exec worker sh

ping-worker:
	$(COMPOSE_FULL) exec worker celery -A jober_worker.celery_app call jober_worker.tasks.ping

tui:
	cd apps/tui && pip install -e . -q && python -m jober_tui

fmt:
	cd apps/api && ruff format src tests && ruff check --fix src tests
	cd apps/worker && ruff format src tests && ruff check --fix src tests

lint:
	cd apps/api && ruff check src tests && mypy src
	cd apps/worker && ruff check src tests && mypy src
	$(MAKE) web-lint

test:
	cd apps/api && pytest -q
	cd apps/worker && pytest -q

web-lint:
	cd apps/web && pnpm lint:strict && pnpm typecheck && pnpm test

web-build:
	cd apps/web && pnpm build

migrate:
	cd apps/api && alembic upgrade head

migrate-check:
	cd apps/api && alembic upgrade head && python scripts/check_migration_drift.py

seed:
	cd apps/api && python scripts/seed.py

schemas-export:
	cd packages/schemas && python scripts/export_typescript.py

backup:
	bash infra/backups/backup.sh

restore:
	bash infra/backups/restore.sh $(SOURCE)

doctor:
	@echo "=== Jober doctor ==="
	@command -v docker >/dev/null 2>&1 && echo "[ok] docker" || echo "[!!] docker not found"
	@command -v docker compose >/dev/null 2>&1 && echo "[ok] docker compose" || echo "[!!] docker compose not found"
	@command -v python3 >/dev/null 2>&1 && echo "[ok] python3: $$(python3 --version 2>&1)" || echo "[!!] python3 not found"
	@command -v ruff >/dev/null 2>&1 && echo "[ok] ruff" || echo "[!!] ruff not found (pip install apps/api[dev])"
	@for port in 5432 6379 8000 9000 9001; do \
		if command -v ss >/dev/null 2>&1; then \
			ss -ltn 2>/dev/null | grep -q ":$$port " && echo "[!!] port $$port appears in use" || echo "[ok] port $$port free"; \
		elif command -v netstat >/dev/null 2>&1; then \
			netstat -an 2>/dev/null | grep -q ":$$port " && echo "[!!] port $$port appears in use" || echo "[ok] port $$port free"; \
		else \
			echo "[??] cannot check port $$port (no ss/netstat)"; \
		fi; \
	done
	@echo "Copy .env.example to .env before first run if you need local overrides."
