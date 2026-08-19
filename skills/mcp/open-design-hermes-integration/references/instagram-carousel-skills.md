# OpenDesign skills for Instagram / social carousels (verified 2026-08)

Verified live via `od list_skills` (162 skills total) on the running OpenDesign
daemon. These are the relevant skills for building a **Java DSA Instagram carousel**
(swipeable multi-card / 1080×1350 vertical).

## Best-fit skills
- **`card-xiaohongshu`** — "Xiaohongshu-style knowledge cards, arranged as a
  swipeable multi-card carousel." Closest match to an IG carousel (swipeable
  cards). `mode=prototype`, `surface=web`.
- **`frontend-slides`** — animation-rich HTML presentations, visual style previews.
  `mode=deck`, `surface=web`, `category=slides`. Good for deck export.
- **`ppt-keynote`** — Apple Keynote-quality slides, one card per screen, keyboard
  left/right nav. `mode=deck`.
- **`slides`** — create/edit .pptx decks (PptxGenJS). `mode=deck`, `category=slides`.
- **`poster-hero`** — vertical poster / Moments-style share image, strong visual
  impact. `mode=prototype`. Good for a single-card cover.
- **`imagegen`** — generate/edit images via OpenAI Image API (social cards,
  illustrations, diagrams). `mode=image`.
- **`fal-generate`** / **`fal-lip-sync`** — Fal.ai image/video gen for asset
  illustration or talking-head explainer cuts.

## `start_run` invocation recipe (verified schema)
`od start_run` spawns OD's own agent and returns a `runId`; poll `get_run`
until terminal. Requires an existing project first (`create_project`).
```json
{
  "project": "<project id or name substring>",
  "skill": "card-xiaohongshu",
  "skills": ["imagegen", "frontend-slides"],
  "prompt": "Java DSA Instagram carousel — e.g. 'Big-O in 5 cards': one code snippet + one-line intuition per card, 1080x1350, brand palette",
  "model": "<optional model override>"
}
```
Note: `project` is optional but expires after ~5 min of no OD activity — pass it
explicitly for cron/disconnected runs. `skill` is a single id; `skills[]` composes
additional ids (deduped server-side).

## Odds & ends
- Daemon must be up: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7456/api/health` → 200.
- `od` MCP server is a stdio proxy (see SKILL.md Phase B) — scope it with the
  Node-24 binary + `cli.js mcp --daemon-url http://127.0.0.1:7456`.
- `list_skills` output is a JSON **string nested inside `content[0].text`** (JSON-RPC
  envelope), not top-level JSON — parse `json.loads(content[0].text)["skills"]`.
