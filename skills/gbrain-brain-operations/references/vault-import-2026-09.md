# Vault import 2026-09-03 — session record

First bulk ingestion into the fresh brain. Kept as the calibrated example for
the import/embed split (SKILL.md sections 2-3).

## Sources and destinations

- Source corpus: `/home/deeone/Documents/Obsidian Vault` (152 importable `.md`
  files; `.obsidian/` and `.smart-env/` internals excluded; 5 zero-byte files).
- Brain repo: `/home/deeone/brain` (MECE scaffold committed first — sync
  refuses an uncommitted repo).
- Trial copies: `/home/deeone/brain/sources/vault-trial/` (5 files).
- Bulk copies: `/home/deeone/brain/sources/vault/` (147 files, original
  relative paths preserved, trial originals excluded).
- Pipeline manifest: `/home/deeone/brain/projects/vault-import/manifest.json`
  (total + per-item status: `imported-trial` vs `staged-bulk`).

## Trial set (deliberately diverse)

1. `trial-01-empty-start-here.md` — 0 bytes, empty edge case. Imported cleanly.
2. `trial-02-minimal-kanban.md` — 32 bytes. Chunked to 0 chunks (too small).
3. `trial-03-java-advanced-projects.md` — 38.6K structured guide with code.
4. `trial-04-hermes-journal.md` — 2.9K daily note (typed `daily`, undeclared).
5. `trial-05-kimi-research.md` — 33.4K research doc with entities.

## Timings (voyage-4 embeddings, 2026-09-03)

- Trial import-only (`sync --no-embed`): 5 pages, 82 chunks, ~14s.
- Bulk import-only: 147 pages, 223 chunks, well under the timeout.
- Single-page embed probe (`trial-04`, 1 chunk): ~21s wall (mostly startup).
- Full `embed --stale` over ~304 chunks: 25+ min and still running at last
  check (~5MB DB writes, steady). Keyword search usable throughout.
- Full `sync` WITH embed on just the 5 trial files: stalled 7+ min, killed.
  This is what motivated the split — never run embed inline on a corpus.

## Verification

- `gbrain search "CRDT operational transformation"` returned the trial-03
  page at score 1.0000 (keyword path, no vectors needed).
- `gbrain list` showed all 5 trial pages with correct titles.
- Schema warnings seen: types `daily` (109 files), `weekly` (17), `index`,
  `meta` — all stored as-is, harmless.

## Companion artifacts from the same session

- Skill workspace: `/home/deeone/gbrain-workspace/` (85-skill offline copy +
  `INDEX.md` generated from `skills/manifest.json` via python3 stdlib, +
  `README.md`). The 73-row index is the fast route into the pack.
- Serve: `gbrain serve --http` on 127.0.0.1:3131 (pglite engine), restarted
  after CLI work; harness MCP wiring (codex/claude/opencode) depends on it.
