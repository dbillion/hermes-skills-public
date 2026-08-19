#!/usr/bin/env bash
# Safe Manim batch renderer.
#  - derives the scene CLASS NAME from the file (regex), never the filename
#  - accumulates mp4s per-scene folder; NEVER rm -rf media
#  - logs >>> DONE / >>> FAIL per scene; continues on failure
#  - run backgrounded:  bash safe_batch_render.sh &
set -u
cd "$(dirname "$0")"
LOG=batch_progress.log
: > "$LOG"

for f in trick_*.py; do
  # Robust: read the class name FROM the file.
  cls=$(/home/deeone/.local/share/uv/tools/manim/bin/python -c "
import re, sys
src = open(sys.argv[1]).read()
m = re.search(r'class\s+(Trick\w+)\s*\(', src)
print(m.group(1) if m else 'TrickUNKNOWN')
" "$f")
  if [ "$cls" = "TrickUNKNOWN" ]; then
    echo ">>> SKIP $f (no Trick class found)" | tee -a "$LOG"
    continue
  fi
  t0=$(date +%s)
  manim --renderer=cairo -ql "$f" "$cls" >> "$LOG" 2>&1
  rc=$?
  t1=$(date +%s)
  if [ $rc -eq 0 ] && [ -f "media/videos/${f%.py}/480p15/${cls}.mp4" ]; then
    sz=$(stat -c%s "media/videos/${f%.py}/480p15/${cls}.mp4")
    echo ">>> DONE $f ($cls) rc=$rc size=${sz}B elapsed=$((t1-t0))s $(date +%H:%M:%S)" | tee -a "$LOG"
  else
    echo ">>> FAIL $f ($cls) rc=$rc elapsed=$((t1-t0))s $(date +%H:%M:%S)" | tee -a "$LOG"
  fi
done
echo ">>> ALL DONE $(date +%H:%M:%S)" | tee -a "$LOG"
