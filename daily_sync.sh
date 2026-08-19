#!/usr/bin/env bash
# Daily Hermes skills sync + security check + push to dbillion/hermes-setup.
# Runs from cron; reports concise status. Never commits live secrets.
set -u
SRC=/home/deeone/.hermes/skills
DST=/home/deeone/hermes-setup
SK=$DST/skills
NOW=$(date '+%Y-%m-%d %H:%M')
echo "=== Hermes Skills Daily Sync [$NOW] ==="

# 1. Sync new skill dirs
added=0
for d in "$SRC"/*/; do
  name=$(basename "$d")
  case "$name" in .curator_backups|.hub|.git) continue ;; esac
  [ ! -e "$SK/$name" ] && { cp -r "$d" "$SK/$name"; added=$((added+1)); echo "ADDED $name"; }
done
echo "NEW_DIRS_ADDED=$added"

cd "$DST" || { echo "FATAL: hermes-setup missing"; exit 1; }

# 2. SECURITY GATE — block push if any LIVE secret detected.
# Only flag genuine high-entropy tokens; ignore docs/test fixtures (have '...'/'xxx'/MPLE
# or live in test/example paths). Real GitHub tokens are exactly 36 alphanumerics.
hits=$(grep -rInE '(gh[o p]_[0-9a-zA-Z]{36}|ghu_[0-9a-zA-Z]{36}|ghs_[0-9a-zA-Z]{36})' skills/ 2>/dev/null | grep -vE '\.\.\.|xxx|MPLE|/test/|/tests/|example')
if [ -n "$hits" ]; then
  echo "SECURITY_BLOCK: possible live GitHub token:"
  echo "$hits" | head
  exit 2
fi
echo "SECURITY: no live secrets detected."

# 3. Commit + push if anything changed
if [ -z "$(git status --porcelain)" ]; then
  echo "STATUS: already up to date — nothing to push."
  exit 0
fi
git add -A
git commit -q -m "daily sync: skills update $NOW" && \
git push -q origin master && \
echo "PUSHED_OK" || { echo "PUSH_FAILED"; exit 3; }
git status -s | head
