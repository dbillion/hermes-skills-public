#!/usr/bin/env bash
# prune_by_keeplist.sh — delete Docker images NOT in KEEP, then prune build cache.
# Usage: KEEP="postgres:|kindest/node|greenbone|docker/desktop-" bash prune_by_keeplist.sh
# The KEEP env var is a grep -E regex of repo prefixes to PRESERVE.
set -u
KEEP="${KEEP:-docker/desktop-}"   # default: keep Docker Desktop internals only

echo "=== Images to delete (not matching: $KEEP) ==="
docker images --format '{{.Repository}}:{{.Tag}}' \
  | grep -vE "^($KEEP)" | grep -v '<none>' > /tmp/del_list.txt
echo "  count: $(wc -l < /tmp/del_list.txt)"

while read -r img; do
  [ -z "$img" ] && continue
  if docker rmi "$img" >/dev/null 2>&1; then
    echo "  removed $img"
  elif docker rmi -f "$img" >/dev/null 2>&1; then
    echo "  forced $img"
  else
    echo "  SKIP (in use) $img"
  fi
done < /tmp/del_list.txt

echo "=== Prune build cache ==="
docker builder prune -af 2>&1 | tail -2

echo "=== Result ==="
docker system df
