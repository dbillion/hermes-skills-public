#!/usr/bin/env bash
# Safe Manim batch render — NEVER deletes media/. Accumulates per-scene mp4s.
# Usage: bash safe_batch_render.sh [quality]   (quality default: -ql --renderer=cairo)
# Drop into the dir containing trick_*.py scene files (each defines a
# `class TrickNN...` with the SceneName). Logs START/DONE/FAIL to render_progress.log.
set -u
cd "$(dirname "$0")"
QUAL="${1:--ql --renderer=cairo}"
LOG=render_progress.log
: > "$LOG"

for f in trick_*.py; do
  # Scene class name = first "^class Trick<digits><Word>" (no bound-method risk)
  cls=$(grep -m1 -oE "^class Trick[0-9][A-Za-z0-9_]*" "$f" | sed -E 's/^class //')
  echo ">>> START $f ($cls) $(date +%H:%M:%S)" | tee -a "$LOG"
  manim $QUAL "$f" "$cls" >> "$LOG" 2>&1
  rc=$?
  if [ $rc -eq 0 ] && [ -f "media/videos/${f%.py}/480p15/${cls}.mp4" ]; then
    sz=$(stat -c%s "media/videos/${f%.py}/480p15/${cls}.mp4")
    echo ">>> DONE  $f ($cls) rc=$rc size=${sz}B $(date +%H:%M:%S)" | tee -a "$LOG"
  else
    echo ">>> FAIL  $f ($cls) rc=$rc $(date +%H:%M:%S)" | tee -a "$LOG"
  fi
done
echo ">>> ALL DONE $(date +%H:%M:%S)" | tee -a "$LOG"
# Post-run verify (disk truth, not memory):
echo "=== final mp4s on disk (excluding partial) ==="
find media -name "*.mp4" -type f ! -path "*partial_movie_files*" | sort
