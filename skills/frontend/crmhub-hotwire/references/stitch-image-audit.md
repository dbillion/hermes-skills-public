# Stitch → ERB Image Fidelity Audit

## Problem
When converting Stitch HTML designs to Rails ERB views, images are frequently omitted, hidden (`class="hidden"`), or replaced with placeholders. This is a fidelity failure — the user expects pixel-perfect reproduction of the Stitch design.

## Image URL Patterns in Stitch

| Pattern | Source | Usage |
|---------|--------|-------|
| `lh3.googleusercontent.com/aida-public/...` | AIDA-generated illustrations | Avatars, hero images, product previews, decorative illustrations |
| `picsum.photos/seed/xxx/W/H` | Lorem Picsum | Placeholder images for mockups |

## Verification Script

Run this after every batch of page conversions to catch missing images:

```bash
# Compare image counts between Stitch HTML and ERB views
for stitch_file in /home/deeone/projects/.stitch/designs/*.html /home/deeone/projects/.stitch/final/*.html; do
  stitch_count=$(grep -c '<img\|<picture' "$stitch_file" 2>/dev/null || echo 0)
  basename=$(basename "$stitch_file" .html)
  
  # Find corresponding ERB (naming may vary)
  erb_file=$(find /home/deeone/projects/crm_hub/app/views -name "*.erb" | xargs grep -l "$basename" 2>/dev/null | head -1)
  
  if [ -n "$erb_file" ]; then
    erb_count=$(grep -c '<img\|<picture' "$erb_file" 2>/dev/null || echo 0)
    status="✅"
    if [ "$erb_count" -lt "$stitch_count" ]; then status="❌ MISSING"; fi
    echo "$status Stitch=$stitch_count ERB=$erb_count $(basename $stitch_file) → $(basename $erb_file)"
  fi
done
```

## Common Failure Modes

1. **Image count = 0 in ERB but >0 in Stitch** — Subagent skipped images entirely
2. **Images added with `class="hidden"`** — Technically present but invisible (still a failure)
3. **Wrong image URLs** — Used different picsum seed or wrong AIDA URL
4. **Images in wrong positions** — Image exists but not where Stitch placed it

## Correct Approach

For every `<img>` or `<picture>` in the Stitch HTML:
1. Copy the exact `src` URL
2. Place an `<img>` tag in the same position in the ERB
3. Keep the same visibility (don't add `class="hidden"`)
4. Keep the same CSS classes for sizing/positioning

## Session Evidence

- Landing page: Stitch has 3 images (booking calendar, 2 testimonial avatars) → ERB must have 3
- Client detail: Stitch has 5 images → ERB must have 5
- Dashboard: Stitch has 1 avatar → ERB must have 1
- The assistant repeatedly added `<img class="hidden">` which the user caught and rejected
