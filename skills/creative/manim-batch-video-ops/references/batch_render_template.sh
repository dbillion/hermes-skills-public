#!/usr/bin/env bash
# Safe batch render — NO rm -rf. Accumulates per-scene .mp4 files.
# Derives the scene class name from the file (not the filename).
# Logs >>> DONE / >>> FAIL per scene so the run is auditable.
set -u
cd /home/deeone/manim-dsa/videos/tricks/redo   # <-- adjust to your scenes dir
LOG=batch_progress.log
: > "$LOG"

for f in trick_*.py; do
  # Robust: read the class name from the file itself.
  cls=$(python3 -c "
import re, sys
src = open(sys.argv[1]).read()
m = re.search(r'class\s+(Trick\w+|[A-Z]\w+Walkthrough\w*)\s*\(', src)
print(m.group(1) if m else 'TrickUNKNOWN')
" "$f")
  if [ "$cls" = "TrickUNKNOWN" ]; then
    echo ">>> SKIP $f (no scene class found)" | tee -a "$LOG"
    continue
  fi
  t0=$(date +%s)
  manim --renderer=cairo -ql "$f" "$cls" >> "$LOG" 2>&1
  rc=$?
  t1=$(date +%s)
  mp4="media/videos/${f%.py}/480p15/${cls}.mp4"
  if [ $rc -eq 0 ] && [ -f "$mp4" ]; then
    sz=$(stat -c%s "$mp4")
    echo ">>> DONE $f ($cls) rc=$rc size=${sz}B elapsed=$((t1-t0))s $(date +%H:%M:%S)" | tee -a "$LOG"
  else
    echo ">>> FAIL $f ($cls) rc=$rc elapsed=$((t1-t0))s $(date +%H:%M:%S)" | tee -a "$LOG"
  fi
done
echo ">>> ALL DONE $(date +%H:%M:%S)" | tee -a "$LOG"
