#!/usr/bin/env bash
# Sync ~/.hermes/skills into hermes-setup/skills, then report status.
set -u
SRC=/home/deeone/.hermes/skills
DST=/home/deeone/hermes-setup/skills
mkdir -p "$DST"
added=0
for d in "$SRC"/*/; do
  name=$(basename "$d")
  # skip internal/backup dirs
  case "$name" in
    .curator_backups|.hub|.git) continue ;;
  esac
  if [ ! -e "$DST/$name" ]; then
    cp -r "$d" "$DST/$name"
    added=$((added+1))
    echo "ADDED $name"
  fi
done
echo "NEW_DIRS_ADDED=$added"
cd /home/deeone/hermes-setup
echo "=== git status ==="
git status -s | head -40
echo "=== total changed/untracked ==="
git status -s | wc -l
