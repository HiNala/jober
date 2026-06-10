#!/usr/bin/env bash
# Staging/production golden-path gate — unauthenticated smoke only (no live mass submit).
# Authenticated fixture pipeline is covered by CI: test_golden_path_integration.py
set -euo pipefail

# Override for production: API_URL=https://api-production-4b5b.up.railway.app WEB_URL=https://web-production-29902.up.railway.app
API_URL="${API_URL:-https://api-staging-a8ca.up.railway.app}"
WEB_URL="${WEB_URL:-https://web-staging-763f.up.railway.app}"

export API_URL WEB_URL
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Golden path (public smoke) for ${API_URL}"
bash "${SCRIPT_DIR}/railway-smoke.sh"

echo ""
echo "Golden path public checks passed."
echo "Authenticated fixture submit/review flow: CI test_golden_path_integration.py (blocking)."
echo "Do not run mass live submissions against production ATS from this script."
