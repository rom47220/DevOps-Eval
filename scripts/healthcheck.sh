#!/usr/bin/env bash
set -euo pipefail

URL="${1:-http://localhost:8080/health}"
RETRIES="${2:-3}"
SLEEP_SECS="${3:-3}"

for i in $(seq 1 "$RETRIES"); do
  echo "[healthcheck] try ${i}/${RETRIES} -> ${URL}"
  if curl -sf "$URL" | grep -q '"status":"ok"'; then
    echo "[healthcheck] OK"
    exit 0
  fi
  sleep "$SLEEP_SECS"
done

echo "[healthcheck] FAILED after ${RETRIES} tries" >&2
exit 1
