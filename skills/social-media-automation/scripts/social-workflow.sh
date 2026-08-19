#!/bin/bash
# ============================================================================
# Social Media Video Workflow
# Combines carousel slides into a video with optional music
# ============================================================================
# Usage:
#   ./social-workflow.sh <slides_dir> <output_video> [audio_file]
#
# Example:
#   ./social-workflow.sh workspace/instagram-carousel/slides/ output.mp4 music.mp3
# ============================================================================

set -euo pipefail

SLIDES_DIR="${1:?Usage: $0 <slides_dir> <output_video> [audio_file]}"
OUTPUT_VIDEO="${2:?Usage: $0 <slides_dir> <output_video> [audio_file]}"
AUDIO_FILE="${3:-}"
DURATION_PER_SLIDE=5
WORKSPACE_DIR="$(dirname "$OUTPUT_VIDEO")"
CONCAT_FILE="$WORKSPACE_DIR/concat.txt"
NORMALIZED_DIR="$WORKSPACE_DIR/normalized"

echo "🎬 Social Media Video Workflow"
echo "Slides: $SLIDES_DIR → Output: $OUTPUT_VIDEO"

# Step 1: Normalize slides to 1080x1080
echo "📐 Normalizing slides..."
mkdir -p "$NORMALIZED_DIR"
slide_num=0
for slide in "$SLIDES_DIR"/slide-*.png; do
    slide_num=$((slide_num + 1))
    output="$NORMALIZED_DIR/$(printf '%02d' $slide_num).png"
    ffmpeg -y -i "$slide" \
        -vf "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:color=black" \
        -frames:v 1 "$output" 2>/dev/null
done
echo "  ✓ $slide_num slides normalized"

# Step 2: Create concat file
echo "🎞️  Building video..."
> "$CONCAT_FILE"
for img in "$NORMALIZED_DIR"/*.png; do
    echo "file '$img'" >> "$CONCAT_FILE"
    echo "duration $DURATION_PER_SLIDE" >> "$CONCAT_FILE"
done
last_img=$(ls "$NORMALIZED_DIR"/*.png | sort | tail -1)
echo "file '$last_img'" >> "$CONCAT_FILE"

# Step 3: Build video
TOTAL_DURATION=$((slide_num * DURATION_PER_SLIDE))
if [ -n "$AUDIO_FILE" ] && [ -f "$AUDIO_FILE" ]; then
    ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" -i "$AUDIO_FILE" \
        -vf "fps=30,format=yuv420p" -af "afade=t=st=0:d=2,afade=t=st=$((TOTAL_DURATION - 2)):d=2" \
        -shortest -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 128k \
        -movflags +faststart -pix_fmt yuv420p "$OUTPUT_VIDEO" 2>/dev/null
else
    ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" \
        -vf "fps=30,format=yuv420p" -c:v libx264 -preset fast -crf 18 \
        -movflags +faststart -pix_fmt yuv420p "$OUTPUT_VIDEO" 2>/dev/null
fi
echo "  ✓ Video created: $OUTPUT_VIDEO"

# Cleanup
rm -rf "$NORMALIZED_DIR" "$CONCAT_FILE"

# Info
ffprobe -v quiet -print_format json -show_format -show_streams "$OUTPUT_VIDEO" 2>/dev/null | \
    python3 -c "
import json, sys
d = json.load(sys.stdin)
f = d.get('format', {})
print(f'Duration: {float(f.get(\"duration\", 0)):.1f}s')
print(f'Size: {int(f.get(\"size\", 0)) / 1024 / 1024:.1f} MB')
for s in d.get('streams', []):
    if s.get('codec_type') == 'video':
        print(f'Resolution: {s[\"width\"]}x{s[\"height\"]}')
        print(f'Codec: {s[\"codec_name\"]}')
"
echo "✅ Done. Post with: node social-post.js $OUTPUT_VIDEO \"Your caption\""
