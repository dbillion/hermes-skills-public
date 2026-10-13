# PGLite single-writer ops (gbrain, observed 2026-09-03, v0.48.2.0)

- Lock: `<datadir>/.gbrain-lock` held by exactly one process. `gbrain serve
  --http` (port 3131, `/health`) holds it while running; ALL CLI writes
  (sync, remember, embed) then refuse with "database is already open".
- While serve runs: reads work, `sync` becomes serve-delegated automatically.
  For CLI writes: stop serve, do the write, restart serve.
- Token mint (`auth create`) must happen while serve is STOPPED (session
  lock); then restart serve and pass `--token` to consumers (bootstrap
  harness flow).
- `embed --stale` is the incremental pass; `--batch-size 5` survived Voyage
  429s where full batches failed. Confirm with a follow-up run showing
  "Embedded 0 chunks (0 stale found)".
- `recall` is MCP-side only (no CLI entry): `gbrain call recall
  '{"query":"..."}'`. `search` covers page chunks only, not the fact
  store — a populated search result is NOT proof a remembered fact is
  retrievable; the recall round-trip is.
- Cosmetic warnings seen, both non-blocking: NUL-signature chunks left in a
  previous embedding space after provider switch (re-run with
  `--include-null-signature` or `migrate embeddings` to unify, at API cost),
  and pinned `expansion_model` without a provider key (falls back to
  key-aware default; unpin or set the key in ~/.gbrain/config.json).
