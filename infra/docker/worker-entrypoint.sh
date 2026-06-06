#!/bin/sh
set -e

celery -A jober_worker.celery_app worker --loglevel=info &
WORKER_PID=$!

echo "Waiting for Celery worker..."
READY=0
for _ in $(seq 1 60); do
  if celery -A jober_worker.celery_app inspect ping 2>/dev/null | grep -q pong; then
    echo "Celery worker is ready"
    READY=1
    break
  fi
  sleep 1
done

if [ "$READY" -eq 1 ]; then
  echo "Running startup ping task..."
  celery -A jober_worker.celery_app call jober_worker.tasks.ping || true
else
  echo "Worker did not become ready in time; continuing without startup ping"
fi

wait $WORKER_PID