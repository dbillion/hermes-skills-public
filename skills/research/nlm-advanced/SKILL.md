---
name: nlm-advanced
description: "Advanced NLM features: Discover Sources (auto web search), YouTube transcript extraction, slide deck design with --focus, profile rotation. Use alongside nlm-productivity for advanced workflows."
---

# NLM Advanced Features

Reference for advanced NotebookLM capabilities discovered through active use.

## Discover Sources (Auto Web Search)

NotebookLM can search the web and auto-add sources to a notebook. This is the fastest way to build a research library.

### Via NotebookLM Web UI
1. Open notebook → click "Discover sources"
2. Type research question or topic
3. NotebookLM finds and suggests relevant sources
4. Select — they're auto-added to your notebook

### Tips
- Be specific: "Pauline theology of grace in Romans" not just "grace"
- Preferred: journal articles, books, seminary publications
- Avoid: Wikipedia, personal blogs, non-academic websites
- Aim for 6-8 sources per paper (min 5, 3 must be printed)

---

## YouTube Transcript Extraction

**ALWAYS prefer NLM --youtube source.** Do NOT install youtube-transcript-api as first resort.

```bash
# Add YouTube video as source
nlm source add <notebook-id> --youtube "https://youtu.be/VIDEO_ID" --wait

# Extract transcript
nlm notebook query <notebook-id> "Extract the full transcript. Include timestamps. Format as clean transcript with speaker labels if identifiable."

# Structured analysis
nlm notebook query <notebook-id> "Provide: 1) Main thesis, 2) Key points with timestamps, 3) Biblical references, 4) Notable quotes, 5) Call to action. Format as structured analysis."
```

### Why NLM first?
- No extra packages needed
- Handles auth and processing automatically
- Supports multilingual videos
- Can analyze content directly after ingestion

### Zapier YouTube MCP limitation
The Zapier YouTube MCP (zapier-youtube-mcp) provides 8 tools: search, analytics, upload, thumbnails, playlists, raw API calls. It does **NOT** extract transcripts. Use it for finding videos, not reading them.

---

## Slide Decks with Visual Design

**⚠️ Always sleep 5 minutes before running `nlm slides create`** to avoid rate limits (RESOURCE_EXHAUSTED code 8). Slide deck generation is the most rate-limited NLM operation.

Use `--focus` for high-quality presentation decks. The `--length` option accepts `default` or `short` (not `dynamic`).

```bash
# Basic
nlm slides create <notebook-id> --confirm

# Detailed with design focus
nlm slides create <notebook-id> --format detailed_deck --length default --confirm \\
  --focus "Act as senior presentation designer. One message per slide. Max 4 bullets, 12 words each. 18 pages."
```

After starting slide deck generation, check progress with:
```bash
nlm studio status <notebook-id>
```
Wait until the status changes from `in_progress` to `completed` before retrieving the artifact.

### Design Focus Template (Dark Luxury / Sacred Aesthetic)
```
--focus "Act as a McKinsey Senior Designer. CREATE A VISUAL WONDER.
Rules:
1. Style: Dark luxury, cinematic sacred artifact aesthetic.
2. Palette: Obsidian foundation with Burnished Gold and Volumetric Light.
3. Typography: 3D-beveled Gold Serif headers; Montserrat body.
4. Composition: Symmetrical triptychs and theatrical staging.
5. Atmosphere: Cinematic god rays, radiant bloom, deckled edge overlays.
6. Materiality: Textures of molten obsidian, igneous basalt, forged metal.
7. Content: One core message per slide.
8. Limits: Max 4 bullets per slide, 12 words each.
9. GENERATE A COMPREHENSIVE 18-PAGE DECK."
```

### Accent Colors by Bible Topic
- Wisdom (Proverbs): Deep Emerald or Gold
- Law (Deuteronomy): Stone Grey or Bronze
- Grace (Luke): Crimson or Royal Blue

---

## Profile Rotation

When rate limits hit (INVALID_ARGUMENT error code 8):

```bash
nlm login profile list
nlm login switch <profile-name>
```

### Zapier MCP Configuration Pattern
When user provides a Zapier MCP URL (format: `https://mcp.zapier.com/api/v1/connect?token=***`):
- Configure in Hermes native-mcp as HTTP StreamableHTTP transport
- The token is embedded in the URL query parameter
- Do NOT try to extract the token — use the full URL as-is

---

## Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| NLM --youtube takes >60s | Video processing can be slow | Use --wait flag, takes 30-90s for long videos |
| Zapier MCP auth fails | Token is in URL query param | Configure as HTTP transport with full URL |
| "Transcript disabled" | Video has no captions | Try NLM anyway -- it can still analyze content |
| Rate limit on slide creation (code 8) | Slide deck generation is more rate-limited than other operations | **Always sleep 5 minutes before `nlm slides create`** to avoid RESOURCE_EXHAUSTED; check `nlm studio status` after wait to confirm readiness |
| Rate limit on other NLM ops (code 8) | Too many requests | Switch profile with `nlm login -p <profile>` or wait 5 min |
| Missing citation data | NLM can't find publisher | Search Google Scholar directly |
| "Unknown option: --notebook-id" when adding a source | The CLI expects notebook ID as first argument, not a flag | Use `nlm source add <notebook-id> --url <URL> [--wait]` |
| "Download failed for slide_deck" | Wrong artifact ID or profile mismatch | Verify correct studio ID from `nlm studio status`; ensure logged into the correct profile |
| studio status returns empty / "Could not retrieve" | Notebook ID not found under current profile, or API temporary glitch | Re-list notebooks with `nlm notebook list` under the correct profile; retry with short delay |
