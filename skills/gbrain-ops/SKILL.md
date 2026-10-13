---
name: gbrain-ops
description: "Use when running gbrain on PGLite. Serve lock, sync, embed."
---

# gbrain PGLite Operations

A PGLite-backed brain has ONE writer. `gbrain serve` (HTTP/MCP) holds the database
open; every CLI write (`put`, `sync` with embed, `embed`, `import`) then fails with the
single-writer lock message. Reads (`search`, `list`, `get`, `query`) keep working.

## The lock discipline

- Harness wiring (Codex/Claude/opencode MCP) depends on serve staying UP. Treat serve
  downtime as an outage window: stop it, do CLI writes, restart it, verify health.
- `gbrain sync --repo <path>` is serve-delegated and works while serve runs — but only
  for text import. Embedding still needs the CLI path (serve stopped).
- Track the serve background session id; the MCP wiring goes dark the moment it dies.
- After ANY CLI write session: restart serve, then `curl -s http://127.0.0.1:3131/health`.

## The import/sync/embed split

`gbrain sync --repo` with embedding is slow and opaque (one stuck API call stalls the
whole run with no per-file progress). Split it:

1. `git add -A && git commit` in the brain repo FIRST — sync refuses repos with no commits
   (`unknown revision HEAD`).
2. `gbrain sync --repo <path> --no-embed` — fast text import with per-file progress
   (`[import.files] 5/5`, chunk counts). Verify with `gbrain search "<known phrase>"`.
3. `gbrain embed --stale` separately, in background with notify — see
   `references/voyage-embed-throttle.md` for the rate-limit playbook.

## Trial before bulk (vault imports)

- Never bulk-import a vault/Obsidian export sight-unseen. Copy 5 DIVERSE files
  (empty edge case, minimal note, large structured doc, journal entry, entity-rich
  research) into `sources/<name>-trial/`, sync, search-verify, then bulk the rest into
  `sources/<name>/` preserving relative paths (provenance).
- Exclude vault internals (`.obsidian/`, `.smart-env/`, plugin scripts) at copy time.
- Track state in `projects/<pipeline>/manifest.json` (total from source enumeration,
  per-item status) so reruns are idempotent and resumable across sessions.
- Expect schema type warnings (`daily`, `weekly` undeclared) — pages store as-is; silence
  with `gbrain config set schema.type_warnings false` or declare types later.

## Monitoring background gbrain work

- `gbrain` CLI output piped through `tail` shows NOTHING until exit — poll liveness via
  `/proc/<pid>/io` (wchar growth = embeddings landing) not via session output preview.
- `pgrep -f "gbrain embed"` matches the zsh WRAPPER first. Find the real worker with
  `pgrep -P <wrapper-pid> -a` (the `bun ... gbrain` child) and watch ITS io counters.
- Single-slug probe before full runs: `time gbrain embed <one-slug>` measures startup
  overhead (~15s PGLite open) vs per-chunk cost. A 0-chunk page still costs startup.

## Pitfalls

- Never run tool installers (code-review-graph, skills) from inside the brain repo or any
  third-party checkout — they inject dotfiles/hooks into the cwd. `cd ~` (or the target
  project) first, and `git status --short` after.
- `gbrain embed` `--stale` retries ONLY failed/stale chunks — reruns are safe and cheap.
- Voyage 429s are per-burst, not fatal: smaller `--batch-size`, cooldowns, rerun. Details in
  `references/voyage-embed-throttle.md`.
- Keep API keys in session env (`export VOYAGE_API_KEY=...`), never in files or repos.
