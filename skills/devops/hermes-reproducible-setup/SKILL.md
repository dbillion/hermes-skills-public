---
name: hermes-reproducible-setup
description: Secret-safe Hermes Agent backup to reinstall elsewhere.
---

# Hermes Reproducible Setup

Capture a full Hermes Agent install so it can be reinstalled on a fresh machine
**with identical access to external tools/MCP servers**, without ever committing
credentials.

## When to use
- "make my setup reinstallable on another PC", "back up my Hermes config",
  "clone my agent setup", "commit my skills + tools so I can restore them".
- Any task where the deliverable is a git repo that restores the agent environment.

## Core contract (NON-NEGOTIABLE)
**No secret values ever enter the repo.** Live config (`~/.hermes/config.yaml`,
`~/.mcp_servers.json`, `~/.env`, `auth.json`, `nous_auth.json`, `*.db`) stays
local and gitignored. The repo carries *structure only*: every secret value is
replaced by a `${ENV:VAR}` placeholder, and real values live in a local
`secrets.env` the user carries over separately (password manager / encrypted channel).

## Process
1. **Create a dedicated repo** (e.g. `~/hermes-setup`), separate from a messy
   home-dir git repo. Don't dump into `$HOME` if `$HOME` is already a repo.
2. **Generate redacted templates** with `scripts/mask_secrets.py .` — it reads
   the live config and writes `config.yaml.template`, `mcp_servers.json.template`,
   and `secrets.example` (var names only). See `references/secret-redaction-pitfalls.md`.
3. **Capture ALL skill sources** (see Pitfalls #1). Copy user-authored
   `~/.hermes/skills/*` → `skills/` and the symlinked `~/.agents/skills/*` →
   `skills-external/`. Exclude nested `.git` (move to trash, not rm) and binary
   assets via `.gitignore` (`skills/**/*.png`, `*.bin`, `*.pdf`, …).
4. **Write `bootstrap.sh`** that: loads `secrets.env`, substitutes `${ENV:VAR}`
   in the templates → writes `~/.hermes/config.yaml` + `~/.mcp_servers.json`,
   reinstalls external CLIs (hermes, nlm, codegraph, mcp-cli, lightpanda binary,
   tgforwarder), copies `skills/` → `~/.hermes/skills` and `skills-external/` →
   `~/.agents/skills`, and re-symlinks skills for unified discovery.
5. **`.gitignore`** must block: `.env`, `secrets.env`, `config.yaml`,
   `mcp_servers.json`, `auth.json`, `nous_auth.json`, `*.db`, logs, caches,
   `lightpanda`, `tgforwarder/`, and skill binary assets.
6. **Verify before commit**: `grep -c` for real credential patterns
   (`cf_clearance=`, `AWSALBTG=`, `substack.sid=s%`, `sk-…`, `ghp_…`, `xoxb-…`,
   `ya29.`) across staged files → must be 0. Validate templates parse
   (`python3 -c "import yaml,json; …"`). Confirm no live secret files are staged.

## External tool CLIs to reinstall (capture provenance)
| Tool | Install | Notes |
|---|---|---|
| hermes | install.sh | agent CLI + venv |
| nlm | `uv tool install notebooklm-mcp-cli` | NotebookLM MCP CLI |
| codegraph | `uv tool install codegraph` | code-graph MCP server |
| mcp-cli | `uv tool install mcp-cli` | generic MCP CLI |
| lightpanda | binary download → `~/bin` | headless browser (gitignored) |
| tgforwarder | `pip install -e <repo>` | Telegram MTProto forwarder (own git repo) |
| uv, gh, go, node, jq, rg | system/nvm | assumed present |

## Pitfalls
1. **Counting only ONE skill source.** Hermes skills come from BOTH
   `~/.hermes/skills/` (user-authored, real dirs) AND `~/.agents/skills/` /
   `~/.claude/skills/` (symlinked, often 400+). The "prior backup" the user
   remembers (e.g. a `hermes-skills` repo) is usually the *symlinked* set. If you
   capture only `~/.hermes/skills/` you'll deliver ~143 skills when the user
   expects ~500. Capture both. Also diff the live source against any prior backup
   repo — the live tree may have skills the backup lacks.
2. **Multi-line secret leak in `env:` blocks.** `config.yaml` MCP `env:` blocks
   (e.g. Substack session cookies) are multi-line scalars spanning lines at
   deeper indentation. A per-line regex requiring `:` will NOT match those
   continuation lines, so they fall through and get written verbatim. Handle
   env-block lines BEFORE the main parse guard; blank any env-block line that is
   not a nested `key:` mapping. (Detail: `references/secret-redaction-pitfalls.md`.)
3. **Nested `.git` in copied skills.** Some skill dirs are themselves git repos.
   Copying them creates nested `.git` → broken submodules / unclonable repo.
   Move each nested `.git` to `~/.local/share/Trash/` (recoverable, never `rm`),
   then `git rm --cached` the stale gitlink and re-add as plain files.
4. **Commit may be blocked by the user's safety guard.** `git commit` (especially
   with inline `-c user.name=…` flags, or after `cmd | xargs` pipes) can be
   blocked by the scanner/guard. Stage everything, then either use a plain
   `git commit` after `git config user.name`, or leave staging for the user to
   commit. Never retry the same blocked form repeatedly.
5. **Binary bloat.** Skill dirs bundle textures/`.bin`/PDFs (esp. threejs-*).
   Gitignore `*.png *.jpg *.bin *.mp4 *.pdf` etc. across `skills/` AND
   `skills-external/`. Keep the repo text-only and lean.

## Support files
- `scripts/mask_secrets.py` — regenerates the three templates from live config;
  safe to re-run after you change providers/MCP servers.
- `references/secret-redaction-pitfalls.md` — the multi-line-secret-leak lesson,
  with the exact failure mode and fix.
