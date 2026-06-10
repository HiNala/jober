#!/bin/sh
set -e

PORT="${PORT:-8000}"
cd /app

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting API on port ${PORT}..."
exec uvicorn jober_api.main:app --host 0.0.0.0 --port "${PORT}"
