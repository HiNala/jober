#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
COMPOSE_FILE="${ROOT}/infra/compose.yaml"
COMPOSE_ENV=()
if [[ -f "${ROOT}/.env" ]]; then
  COMPOSE_ENV=(--env-file "${ROOT}/.env")
fi
COMPOSE=(docker compose "${COMPOSE_ENV[@]}" -f "${COMPOSE_FILE}" --profile infra)

SOURCE="${1:-${ROOT}/infra/backups/latest}"
if [[ ! -d "${SOURCE}" ]]; then
  echo "Backup directory not found: ${SOURCE}" >&2
  exit 1
fi

if [[ ! -f "${SOURCE}/postgres.dump" ]]; then
  echo "Missing postgres.dump in ${SOURCE}" >&2
  exit 1
fi

echo "Restoring Postgres from ${SOURCE}/postgres.dump"
"${COMPOSE[@]}" exec -T postgres dropdb -U jober --if-exists jober
"${COMPOSE[@]}" exec -T postgres createdb -U jober jober
cat "${SOURCE}/postgres.dump" | "${COMPOSE[@]}" exec -T postgres pg_restore -U jober -d jober --no-owner --no-privileges

if [[ -d "${SOURCE}/minio" ]]; then
  echo "Restoring MinIO bucket from ${SOURCE}/minio"
  "${COMPOSE[@]}" run --rm --no-deps -v "${SOURCE}:/backup:ro" --entrypoint /bin/sh createbuckets -c "
    mc alias set local http://minio:9000 minioadmin minioadmin &&
    mc mirror --overwrite /backup/minio local/jober-artifacts
  "
fi

echo "Restore complete from ${SOURCE}"
