# GitHub README Inline Video → GIF Fix

**Problem**: GitHub README markdown does NOT render `<video src="...">` inline. The HTML `<video>` tag is stripped for security. Only images (PNG/JPG/GIF) render inline.

**Solution**: Convert demo MP4 to optimized GIF and reference the GIF in README.

## Conversion (ffmpeg with palette optimization)

```bash
# 1. Download the MP4
wget "https://raw.githubusercontent.com/dbillion/manim-storytelling-skills/master/samples/test_v2.mp4" -O test_v2.mp4

# 2. Convert to GIF with palette (smaller, better colors)
ffmpeg -y -i test_v2.mp4 \
  -vf "fps=10,scale=854:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 test_v2.gif

# 3. Add to repo
mkdir -p samples
cp test_v2.gif samples/

# 4. Update README.md
# Before: <video src="./samples/test_v2.mp4" controls width="100%"></video>
# After:  ![Manim DSA Storytelling Demo](samples/test_v2.gif)
```

## Key ffmpeg flags

- `fps=10` — 10 FPS is enough for demo, keeps file small
- `scale=854:-1` — width 854px (HD), height auto
- `palettegen/paletteuse` — optimal color palette per frame (avoids 256-color banding)
- `-loop 0` — infinite loop

## File sizes (from this session)

| Format | Size | Duration |
|--------|------|----------|
| MP4 (original) | 1.5 MB | 34s |
| GIF (optimized) | 4.3 MB | 34s |

## GitHub Behavior

- MP4 in `<video>` tag: Shows as file link, NOT inline
- GIF in `![](samples/test_v2.gif)`: Renders INLINE, autoplays, loops
- WebP/AVIF: Not yet supported in all GitHub contexts

## Commit & Push

```bash
cd manim-storytelling-skills
git add README.md samples/test_v2.gif
git commit -m "Fix README: replace inline MP4 with GIF for GitHub inline playback"
git push origin master
```

## Result

The demo now plays inline at https://github.com/dbillion/manim-storytelling-skills — no click required.