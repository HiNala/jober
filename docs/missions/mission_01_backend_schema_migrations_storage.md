# Mission 01 — Backend Schema, Migrations & Storage

> **Agent contract.** Keep a live task list (below). Work each task to its acceptance criteria, committing per task. Do not mark the mission complete until every quality gate is green.

## Objective
Define the full typed data model in SQLAlchemy 2.0 (async), wire Alembic migrations, stand up MinIO object storage with presigned URLs, and expose a shared schema package so the web app and API never drift.

## Dependencies
Mission 00 (infra running).

## Task list
- [x] SQLAlchemy 2.0 async models for every entity, split across files (<2000 lines each).
- [x] Enums for run status (full state machine), policy, field status, checkpoint type, document type.
- [x] Alembic configured for async; initial migration; `make migrate` applies cleanly.
- [x] Encrypted column type for sensitive vault fields (`VAULT_ENCRYPTION_KEY`, Fernet).
- [x] MinIO client wrapper: `put_object`, `presigned_get`, `presigned_put`, key conventions.
- [x] Repository/service layer with typed CRUD.
- [x] `packages/schemas`: Pydantic v2 + TypeScript export script.
- [x] Seed script: demo `UserProfile` + sample `JobTarget`s.
- [x] Unit tests: model round-trips, encryption transparency, MinIO presign round-trip.
- [x] Iteration: `infra/backups/`, `make backup`/`restore`, migration drift check in CI.

## Acceptance criteria
- [x] `make migrate` builds full schema from empty; `alembic downgrade base` → `upgrade head` round-trips.
- [x] Sensitive field: ciphertext at rest, plaintext via ORM.
- [x] Presigned upload + download round-trip through MinIO in tests.
- [x] `ruff`, `mypy`, `pytest` green; shared types export without errors.

## Notes
- Enum columns stored as `VARCHAR(32)` in migrations (avoids PG native enum downgrade bugs).
- `RunPolicy.REVIEW_BEFORE_SUBMIT` is the default — never `auto_submit`.
- `proposed_value_redacted` / `redacted_*` columns are for masked previews only.

## Iteration clause (Mission 99)
- [x] Backup/restore scripts and Makefile targets.
- [x] Migration drift CI check with VARCHAR/Enum equivalence handling.
- [x] Policy baseline tests for schema-layer invariants.
