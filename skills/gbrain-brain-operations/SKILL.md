---
name: gbrain-brain-operations
version: 1.0.0
description: "Operate a gbrain brain: sync, import, embed, serve."
triggers:
  - "gbrain sync"
  - "gbrain embed"
  - "brain import"
  - "vault import"
  - "gbrain serve"
  - "brain locked"
  - "PGLite lock"
---

# gbrain-brain-operations — running a gbrain knowledge brain

## 1. Serve lifecycle (the single-writer lock)

`gbrain serve --http` holds the PGLite database open. While it runs, every CLI
write command (`put`, `sync`, `embed`, `import`) fails with the
"already open through gbrain serve" message. Reads (`search`, `list`, `get`)
keep working.

Discipline:

- Before CLI writes: stop serve (kill the background session), do the work,
  restart serve immediately after. The agent harness (Claude Code / Codex /
  opencode MCP wiring) goes dark while serve is down — never leave it stopped.
- `gbrain serve --http` needs `VOYAGE_API_KEY` in its environment for
  serve-side embedding. Pass it via inline `export`, never commit it.
- Verify serve health after restart: `curl -s http://127.0.0.1:3131/health`.

## 2. Import/embed split (never one big sync on a fresh corpus)

A full `gbrain sync` with embedding on a large corpus stalls (embedding API
calls dominate; a 5-file trial took 7+ minutes stuck on embed while
import-only took 14 seconds). Always split:

1. `gbrain sync --repo <repo> --no-embed` — fast text import, verifies filing.
2. Probe embed rate on ONE real page first:
   `gbrain embed <slug>` (~20s incl. startup; ~6s/chunk steady-state on voyage-4).
3. `gbrain embed --stale` in background with notify; monitor the real `bun`
   worker (child of the shell wrapper — check `pgrep -P`), not the wrapper.
   Blind `tail` pipes hide progress: watch `/proc/<pid>/io` (`wchar` growth
   means embeddings are landing) over 60-90s windows.
4. Keyword search (`gbrain search`) works without embeddings — the corpus is
   usable before embed finishes. Hybrid `query` needs vectors.

## 3. Trial before bulk (vault/corpus ingestion)

Follow the ladder from the gbrain `bulk-ingestion` skill (see the offline copy
at `~/gbrain-workspace/skills/bulk-ingestion/SKILL.md`):

- Pick 5-10 DIVERSE trial files first: an empty file, a minimal file, a large
  structured file, a journal/daily file, a research file with entities.
- Stage trial copies under `<repo>/sources/<corpus>-trial/`, commit, sync
  `--no-embed`, verify with `gbrain search` + `gbrain list`.
- Only then copy the bulk set (minus trial originals to avoid duplicates),
  commit, sync `--no-embed`.
- First-ever sync on a fresh repo fails with "Make at least one commit before
  syncing" — commit the scaffold first.
- Track state in `<repo>/projects/<pipeline>/manifest.json` (total from source
  enumeration, per-item status) so reruns are idempotent and resumable.
- Expect schema-pack type warnings (`daily`, `weekly`, `index`, `meta` stored
  as-is) on Obsidian-style vaults; silence or declare types afterwards.

## 4. Secrets

- Embedding key (`VOYAGE_API_KEY`) and any tokens travel via inline env export
  per command, never written into repos or committed files.
- Auth tokens for MCP wiring (`gbrain auth create`) are shown once — deliver
  inline to the wiring command in the same session, then `unset`.

## References

- `references/vault-import-2026-09.md` — the first full vault import: paths,
  counts, timings, and what stalled.
