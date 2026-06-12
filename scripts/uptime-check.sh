#!/usr/bin/env bash
# Lightweight uptime monitor — suitable for cron (every 5m).
# Exits non-zero on failure; optionally pings OPS_ALERT_WEBHOOK_URL on sustained outage.
set -euo pipefail

API_URL="${API_URL:?Set API_URL}"
WEB_URL="${WEB_URL:-}"
STATE_DIR="${STATE_DIR:-/tmp/jober-uptime}"
FAIL_THRESHOLD="${FAIL_THRESHOLD:-3}"

mkdir -p "$STATE_DIR"
FAIL_FILE="$STATE_DIR/fail_count"

fail_count=0
if [ -f "$FAIL_FILE" ]; then
  fail_count=$(cat "$FAIL_FILE")
fi

if ! bash "$(dirname "$0")/railway-smoke.sh"; then
  fail_count=$((fail_count + 1))
  echo "$fail_count" >"$FAIL_FILE"
  echo "Uptime check failed ($fail_count/$FAIL_THRESHOLD)"
  if [ "$fail_count" -ge "$FAIL_THRESHOLD" ] && [ -n "${OPS_ALERT_WEBHOOK_URL:-}" ]; then
    curl -fsS -X POST "$OPS_ALERT_WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "{\"source\":\"uptime_check\",\"environment\":\"${JOBER_ENV:-unknown}\",\"attention\":[{\"level\":\"error\",\"message\":\"Uptime smoke failed ${fail_count} times in a row for ${API_URL}. Runbook: docs/runbooks/uptime-monitoring.md\",\"runbook\":\"docs/runbooks/uptime-monitoring.md\"}]}" \
      || true
  fi
  exit 1
fi

echo 0 >"$FAIL_FILE"
echo "Uptime check OK for ${API_URL}${WEB_URL:+ and ${WEB_URL}}"
