# Hermes Agent — Full Reinstall / Setup Repo

This repository captures a **complete, reproducible** Hermes Agent setup so it can be
reinstalled on another machine — including config structure, all MCP server
definitions, user-authored skills, and the external tool CLIs Hermes depends on.

## What is and isn't in here (security)

| Included (committed) | Excluded (NEVER committed) |
|---|---|
| `config.yaml.template` — full config with secrets as `${ENV:VAR}` | `config.yaml` (live, with real secrets) |
| `mcp_servers.json.template` — all 50 MCP servers, tokens as `${ENV:VAR}` | `.mcp_servers.json` (live) |
| `secrets.example` — list of every required env var (names only) | `secrets.env` (your real values) |
| `skills/` — 143 user-authored skill dirs (text content) | `.env`, `auth.json`, `nous_auth.json`, `*.db`, logs, caches |
| `bootstrap.sh` — reinstall engine | `lightpanda` binary, `tgforwarder/` repo, venvs |

**No secret values are stored in this repo.** The templates contain only
`${ENV:VAR}` placeholders. Real values live in a local, gitignored `secrets.env`
that you carry over separately (e.g. via a password manager or encrypted channel).

## Reinstall on a new machine

```bash
git clone <this-repo> hermes-setup
cd hermes-setup

# 1. Provide your secrets (copy the template, fill in real values)
cp secrets.example secrets.env
$EDITOR secrets.env          # paste real API keys / tokens

# 2. Run the bootstrap (installs CLIs, restores config + skills)
./bootstrap.sh
```

`bootstrap.sh` will:
1. Load `secrets.env` into the environment.
2. Substitute `${ENV:VAR}` in the templates → write `~/.hermes/config.yaml`
   and `~/.mcp_servers.json`.
3. Install external CLIs: `uv`, `hermes`, `nlm`, `codegraph`, `mcp-cli`,
   `lightpanda` (binary), `tgforwarder` (editable from its repo).
4. Copy user-authored skills and re-link external skill sources
   (`~/.agents/skills`, `~/.claude/skills`, `~/.codegraph`) if present.

Flags: `./bootstrap.sh --skip-tools` (keep existing CLIs),
`./bootstrap.sh --skip-skills`.

## Regenerating the templates (after you change your live config)

If you add a new MCP server or provider key, re-run the masking script — it reads
your **live** config and rewrites the templates with fresh `${ENV:VAR}` placeholders
(again: it never writes secret values into the templates):

```bash
python3 scripts/mask_secrets.py .
git add config.yaml.template mcp_servers.json.template secrets.example
git commit -m "refresh templates from live config"
```

## External tool CLIs captured

| Tool | Install method | Notes |
|---|---|---|
| `hermes` | install.sh | Agent CLI + venv at `~/.hermes/hermes-agent/venv` |
| `nlm` | `uv tool install notebooklm-mcp-cli` | NotebookLM MCP CLI (symlink in `~/.local/bin`) |
| `codegraph` | `uv tool install codegraph` | Code graph MCP server |
| `mcp-cli` | `uv tool install mcp-cli` | Generic MCP CLI |
| `lightpanda` | binary download to `~/bin` | Headless browser (106 MB; excluded from repo) |
| `tgforwarder` | `pip install -e <repo>` | Telegram MTProto forwarder (its own git repo) |
| `gh`, `go`, `node`, `jq`, `rg` | system / nvm | Assumed present on target |

## Skill inventory

See `references/skill-inventory.md` for the full list of captured skills and the
external (symlinked) skill sources that `bootstrap.sh` re-links.
