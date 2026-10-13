#!/usr/bin/env bash
# Merge per-scene .srt sidecars (with cumulative time offsets) and burn into video.
# Usage: hardsub.sh <scene_dir> <out_base>
#   scene_dir : dir containing <Scene>.mp4 + <Scene>.srt pairs (concat order = glob)
#   out_base  : output path prefix (writes <out_base>_subbed.mp4)
set -e
DIR="$1"; OUT="$2"
# ordered scene names (edit to match your concat order)
SCENES=(S1_Title S2_Naive S3_Counter S4_Flow S5_Why S6_Recap)
offset=0.0
: > merged.srt
idx=1
durs=()
for s in "${SCENES[@]}"; do
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$DIR/$s.mp4")
  durs+=("$d")
done
for i in "${!SCENES[@]}"; do
  s="${SCENES[$i]}"; d="${durs[$i]}"
  # shift each timestamp in the srt by $offset
  awk -v off="$offset" -v base="$idx" '
    /^[0-9]+$/ {print base++; next}
    /--> / {
      split($1,a,":"); split(a[3],x,"."); s1=a[1]*3600+a[2]*60+x[1]+ (("x" in x)?x[2]/1000:0) + off
      split($3,b,":"); split(b[3],y,"."); s2=b[1]*3600+b[2]*60+y[1]+ (("y" in y)?y[2]/1000:0) + off
      printf "%02d:%02d:%06.3f --> %02d:%02d:%06.3f\n", int(s1/3600),int(s1/60)%60,s1%60, int(s2/3600),int(s2/60)%60,s2%60
      next
    }
    {print}
  ' "$DIR/$s.srt" >> merged.srt
  idx=$((idx+$(grep -c '^--> ' "$DIR/$s.srt")))
  offset=$(echo "$offset + $d" | bc)
done
ffmpeg -y -i "$DIR/${SCENES[0]}.mp4" -i merged.srt -map 0:v -map 1 -c:a copy "${OUT}_subbed.mp4"
echo "Wrote ${OUT}_subbed.mp4 with merged.srt ($(wc -l < merged.srt) lines)"
