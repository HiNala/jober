#!/usr/bin/env bash
# Post-deploy smoke check — readiness probes + optional golden-path hint.
set -euo pipefail

API_URL="${API_URL:?Set API_URL to the public API base (e.g. https://api.example.com)}"
WEB_URL="${WEB_URL:-}"

echo "==> API /healthz"
curl -fsS "${API_URL}/healthz" | grep -q '"status":"ok"'

echo "==> API /readyz"
ready_json="$(curl -fsS "${API_URL}/readyz")"
echo "${ready_json}"
echo "${ready_json}" | grep -q '"status":"ready"'

if [ -n "${WEB_URL}" ]; then
  echo "==> Web /api/health"
  curl -fsS "${WEB_URL}/api/health" | grep -q '"status":"ok"'
fi

echo "Smoke checks passed. Run golden-path e2e against staging before promoting to production."
