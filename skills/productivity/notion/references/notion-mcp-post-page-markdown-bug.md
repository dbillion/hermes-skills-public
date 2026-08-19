# Notion MCP `API-post-page` markdown field bug

## Symptom
Calling the Notion MCP server's `API-post-page` **with a `markdown` field** returns HTTP 400:
```
Provide a `parent.page_id` or `parent.database_id` parameter to create a page, or use a public integration with `insert_content` capability. Internal integrations aren't owned by a single user, so creating workspace-level private pages is not supported.
```
This error is **MISLEADING**. The `parent.page_id` is valid and points to a normal
(non-workspace) page. The failure is caused by the `markdown` field, not by the parent.

## Reproduction (proven 2026-08-17)
Parent page `3bf21259-8cc5-81c0-82dc-fbf1ae75cd96` had
`parent = {page_id: 31a21259-8cc5-810c-b37d-d52a1e4e4277}` — an Operations Report
page, NOT workspace-level.

- Payload WITH `markdown` (362-byte body, valid `parent.page_id`): **400**, error above.
- Identical payload WITHOUT `markdown`: **200**, page created.

Same parent; `markdown` is the sole differentiator. The misleading text about
"workspace-level private pages" is a red herring.

## Fix
1. Create the page **without** `markdown` (title + parent only). This succeeds.
2. Add the content afterward:
   - **MCP:** `mcp-cli call notion API-append-block-children` with
     `{"block_id": "<page_id>", "children": [...]}` (verify the exact tool name via
     `mcp-cli call notion` if the server build differs).
   - **curl (Path B):** `PATCH /v1/blocks/{page_id}/children` with a `children`
     array of block objects (paragraph, heading, etc.).
3. **Alternative:** skip MCP for page creation entirely and use curl
   `POST /v1/pages` with `markdown` (Path B documents this; it works fine).

## Why
This is a quirk of the MCP server's `API-post-page` markdown handling, NOT a Notion
API limitation. Raw `POST /v1/pages` with `markdown` works. So when pushing many
pages with body content, the robust pattern is: create-then-append (MCP) or
create-with-markdown (curl). Do not waste cycles re-diagnosing the parent — the
parent is fine; it's the `markdown` field in the create call.
