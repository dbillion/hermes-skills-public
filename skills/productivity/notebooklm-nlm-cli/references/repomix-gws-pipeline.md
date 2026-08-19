# repomix + gws Drive pipeline (NotebookLM `nlm` CLI)

Condensed recipe from the 2010–2026 ColorNote backup ingest (Aug 2026). Goal: get a
large markdown corpus into NotebookLM as clean, retrievable sources.

## Decision: use `--text` chunking, NOT `--drive` attach
The remote MCP behind `nlm` cannot read local disk (`--file` → `INVALID_ARGUMENT` code 3),
and `--text` caps one source at ~50 KB. So a big doc must be split into ≤~38 KB chunks.
Two ways to split; repomix gives the better boundaries:

1. repomix merge the era/section `.md` files → `repomix <dir> --style markdown --output merged.md --quiet`
   (installed at `~/.local/bin/repomix`, v1.13.1; `-q` invalid, no `--no-git-sort`).
2. Split `merged.md` at `### ` heading boundaries, flush when `curlen > 38000 and next line
   starts with '### '`. Keeps notes intact. Target ≤~48 KB/chunk (verified safe margin).
3. Upload each chunk: `nlm source add "<nbid>" --text "$BODY" --title "$T" --wait --json`
   from a self-resuming Python loop (log `nbid|title` per success; pace ~1s; on 429 sleep 20s).

Result for the ColorNote corpus: 5 era files → 2 notebooks (A=2016–2019, B=2010–2015+2020–2026)
→ ~45 + ~24 `--text` sources, each notebook under the free 50-source cap.

## Why `gws` and not `rclone`
- `gws` 0.8.1 (node, `~/.local/bin/gws`) is oauth2-authenticated already — Drive ops need
  NO interactive step. Commands: `gws drive +upload <file> --name "X"`; `gws drive files list
  --params '{"pageSize":3}'`; `gws drive permissions create --json '{"role":"reader",...}'
  --params '{"fileId":"<id>"}'`.
- `rclone gdrive:` had an EMPTY token → `rclone config reconnect gdrive:` (manual browser
  OAuth) required. Skip it.

## Hard pitfall: cross-account Drive ownership breaks RAG
`gws` uploads to the `gws` default account's Drive (here `dayozoe`). If the notebook is owned
by a different `nlm` profile (here `abiodun`), then `nlm source add --drive <id>`:
- shows `status: 3` ("processed") in `nlm source list` — looks fine,
- but `nlm query` reports "no sources uploaded", and `nlm content source <id>` →
  `PERMISSION_DENIED` (code 7).
Sharing the Drive file with the owner (`gws drive permissions create --json
'{"role":"reader","type":"user","emailAddress":"<owner>"}' --params '{"fileId":"<id>"}'`)
did NOT make NotebookLM ingest it.
Also `gws drive +upload` forces `mimeType: application/octet-stream` regardless of extension,
so NotebookLM's `google_docs` import does not parse it as text.
**Fix:** create the notebook under the same profile that owns the Drive files, OR just use
`--text` chunking (the proven, reliable path). Drive attach is unreliable for RAG here.

## Note on notebook create rate limits
`nlm notebook create` under a heavily-used profile (`dayozoe`, 112 notebooks) returns
`RESOURCE_EXHAUSTED` (code 8) repeatedly. Create under a low-use valid profile (`abiodun`),
then `nlm share invite <nbid> <email> --role editor` (per-email; `share batch` →
INVALID_ARGUMENT) so the other account can read/generate too.
