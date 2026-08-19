# nlm CLI Recipes

## Notebook + sources
```bash
nlm notebook create "<title>" --json                 # -> notebook_id
nlm source add <nb> --file <path> --title "<label>" --wait

# Code files (.java/.py/.ts) are REJECTED -> copy to .txt first:
cp Algorithms.java Algorithms.txt
nlm source add <nb> --file Algorithms.txt --title "Algorithms.java" --wait

# Images upload fine and act as visual references:
nlm source add <nb> --file owl.png --title "Brand Owl (reference)" --wait

# Consolidate many small files to avoid rate limits:
cat linkedin/*.md > all_algos.md      # one source instead of 83
```

## 18-page visual slide deck (dark-luxury McKinsey aesthetic)
```bash
nlm slides create <nb> --format detailed_deck --length default --confirm \
  --focus "Act as a McKinsey Senior Designer. CREATE A VISUAL WONDER. Rules: 1. Dark luxury, obsidian + burnished gold + volumetric light. 2. 3D-beveled gold serif headers, Montserrat body. 3. Symmetrical triptychs, theatrical staging. 4. One message per slide, max 4 bullets / 12 words. 5. GENERATE A COMPREHENSIVE 18-PAGE DECK."
```
> `--length dynamic` is NOT supported by this CLI — use `default` and bake the page count into `--focus`.

## Single infographic PNG (hand-drawn / kawaii / doodle)
```bash
nlm infographic create <nb> --orientation portrait --detail detailed \
  --style kawaii \
  --focus "Hand-drawn doodle style, warm cozy colors. Feature the brand-character OWL from the uploaded reference image in multiple spots: pointing at tips, holding items, reacting. Match the owl's exact visual design. Top 10 home-organization tips for small spaces, social-media ready." \
  --confirm
```

## Status + download
```bash
nlm studio status <nb>                # needs notebook_id (NOT artifact_id); "unknown"=in progress
nlm download infographic <nb> --id <artifact_id> --output out.png
nlm download slide-deck  <nb> --output out.pdf
```

## Share
```bash
nlm share public <nb>                  # public link == notebook URL; artifacts live inside under Studio
```

## Quota fallback
If Gemini *image* REST models 429, generate the visual via NotebookLM `infographic create` / `slides create`
instead — different backend, separate quota. (For *seeing* an image when native vision is throttled,
see the `gemini-vision-router` skill.)
