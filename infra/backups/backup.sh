#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
COMPOSE_FILE="${ROOT}/infra/compose.yaml"
COMPOSE_ENV=()
if [[ -f "${ROOT}/.env" ]]; then
  COMPOSE_ENV=(--env-file "${ROOT}/.env")
fi
COMPOSE=(docker compose "${COMPOSE_ENV[@]}" -f "${COMPOSE_FILE}" --profile infra)

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="${ROOT}/infra/backups/snapshots/${STAMP}"
mkdir -p "${DEST}"

echo "Backing up Postgres to ${DEST}/postgres.dump"
"${COMPOSE[@]}" exec -T postgres pg_dump -U jober -Fc jober > "${DEST}/postgres.dump"

echo "Backing up MinIO bucket to ${DEST}/minio"
mkdir -p "${DEST}/minio"
"${COMPOSE[@]}" run --rm --no-deps -v "${DEST}:/backup" --entrypoint /bin/sh createbuckets -c "
  mc alias set local http://minio:9000 minioadmin minioadmin &&
  mc mirror --overwrite local/jober-artifacts /backup/minio
"

cat > "${DEST}/manifest.json" <<EOF
{
  "created_at": "${STAMP}",
  "postgres": "postgres.dump",
  "minio": "minio/"
}
EOF

ln -sfn "${DEST}" "${ROOT}/infra/backups/latest"
echo "Backup complete: ${DEST}"
