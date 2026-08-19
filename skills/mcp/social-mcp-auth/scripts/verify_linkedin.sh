#!/usr/bin/env bash
# verify_linkedin.sh — confirm the linkedin-scraper-mcp server is up and authenticated.
# Usage: verify_linkedin.sh [port] [host]
# Requires: server running; `mcporter` on PATH; run from ~ (or pass real config dir).
set -euo pipefail
PORT="${1:-3000}"
HOST="${2:-127.0.0.1}"
MCPORTER="${MCPORTER:-mcporter}"

echo "== port check =="
code=$(curl -s -o /dev/null -w "%{http_code}" "http://${HOST}:${PORT}/mcp" || echo "000")
if [ "$code" = "406" ] || [ "$code" = "200" ]; then
  echo "  server responding (HTTP $code) — likely up"
else
  echo "  server NOT reachable on ${HOST}:${PORT} (HTTP $code)"; exit 1
fi

echo "== auth check (get_my_profile) =="
out=$(timeout 60 "$MCPORTER" call 'linkedin.get_my_profile()' 2>&1) || true
if echo "$out" | grep -q '"url"'; then
  url=$(echo "$out" | grep -oE 'https://www.linkedin.com/in/[^/"]+' | head -1)
  echo "  AUTH OK — profile: ${url}"
else
  echo "  AUTH FAIL — server asked for re-login. Output:"
  echo "$out" | head -5
  exit 2
fi
