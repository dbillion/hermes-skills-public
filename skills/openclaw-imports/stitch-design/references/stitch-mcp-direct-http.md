# Stitch MCP direct HTTP workflow (session notes)

## When mcp-cli fails with schema errors
- `mcp-cli info stitch` can fail on schema refs (e.g., `can't resolve reference #/$defs/ScreenInstance`), even though the Stitch MCP endpoint is healthy.
- In that case, use direct JSON-RPC over HTTP to `https://stitch.googleapis.com/mcp` with the Stitch API key header `X-Goog-Api-Key`.

## JSON-RPC call pattern
- All tool calls are via `method: "tools/call"` and `params: { name, arguments }`.
- List tools:
  - `method: "tools/list"`
- Initialize (optional):
  - `method: "initialize"`

## Important tool names confirmed
- `create_project`
- `generate_screen_from_text`
- `get_screen`
- `list_projects`
- `list_screens`

## Critical gotchas (observed)
1) **`create_project` must be called via `tools/call`.**
   Calling `create_project` directly returns `Method not supported`.

2) **`generate_screen_from_text` requires `projectId` WITHOUT the `projects/` prefix.**

3) **`list_screens` may return empty immediately after generation.**
   - The screen ID can be extracted from the `generate_screen_from_text` response text (search `screens/<id>`).

4) **`get_screen` requires all three fields** (despite deprecated fields):
   - `name` = `projects/{projectId}/screens/{screenId}`
   - `projectId` = `{projectId}`
   - `screenId` = `{screenId}`

5) **Download image/HTML via `get_screen` URLs.**
   - Use `structuredContent.screenshot.downloadUrl`
   - Use `structuredContent.htmlCode.downloadUrl`
   - The MCP server does not expose `download_screen_image` / `download_screen_html` in this environment.

## Screen deduplication (important)

`list_screens` returns **all** versions of screens ever generated in a project. Multiple generations of the same title will all appear. To get the **latest** version of each unique screen:

- Iterate the screens array in order (index 0 = oldest, last = newest)
- Build a map keyed by `title`, overwriting on each occurrence
- The final value is always the newest generation

```python
# Pseudocode
latest = {}
for s in screens_response:
    title = s['title']
    latest[title] = s  # last one wins
```

This matters when you re-generate screens — the old screen IDs still exist and will appear in `list_screens` unless you filter by title.

## Batch download workflow

When you need to download all screens from a project (e.g., after multiple `generate_screen_from_text` calls):

1. `tools/call: list_screens` → get all screens
2. Deduplicate by title (keep last occurrence per title)
3. For each unique screen, `tools/call: get_screen` to get fresh `downloadUrl` values
   - `list_screens` download URLs can expire; `get_screen` always returns fresh ones
4. Download HTML from `structuredContent.htmlCode.downloadUrl`
5) Download PNG from `structuredContent.screenshot.downloadUrl`

Rate-limit: add 0.5s between `get_screen` calls to avoid 429s.

## Minimal sequence
1) tools/call: `create_project` → get `projects/<id>`
2) tools/call: `generate_screen_from_text` (projectId = numeric id)
3) parse `screens/<id>` from response text
4) tools/call: `get_screen` with required fields
5) download assets from `downloadUrl`
