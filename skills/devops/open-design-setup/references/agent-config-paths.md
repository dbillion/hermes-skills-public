# Open Design `od mcp install` — per-agent strategies & config paths

From `apps/daemon/src/mcp-agent-install.ts`. `AGENT_SLUGS` (the only valid
`<agent>` values):

```
claude codex reasonix raven cursor copilot openclaw antigravity pi vibe
hermes cline kimi kiro trae opencode claude-desktop
```

## Strategy → how `od` writes the config

| Strategy | Agents | What `od` does |
|----------|--------|----------------|
| `cli`    | claude, codex, kimi, reasonix | shells out to the agent's own `<bin> mcp add/remove`; needs that CLI installed or it errors |
| `json`   | cursor, copilot, cline, openclaw, antigravity, kiro, raven, trae, opencode, claude-desktop | **deep-merges** one `open-design` server entry into the agent's JSON config; does NOT clobber other servers |
| `manual` | pi, hermes, vibe | prints a ready-to-paste block; **refuses to guess** the path (safe — avoids corrupting user configs) |

## Known config paths (for the `manual` strategy)

- **Hermes**: `~/.hermes/config.yaml` under `mcp_servers.open-design` (YAML).
  Direct file edits are **blocked by a security guard** — use `hermes config set`
  (see SKILL.md). Restart Hermes to load.
- **pi**: `~/.pi/agent/mcp.json` (JSON, `mcpServers` key). File may not exist yet;
  create it. Validate with `node -e "require('/home/deeone/.pi/agent/mcp.json')"`.
- **vibe**: path not authoritatively documented; OD prints a snippet — paste into
  vibe's MCP config after confirming its location.

## `cli` agents — prerequisites
`claude`/`codex`/`kimi`/`reasonix` need their executables on PATH for `od` to
shell out. If `od mcp install claude` fails with "command not found" / no such
binary, either install the agent CLI first or use the agent's own `mcp add`
command with the block from `references/mcp-server-block.md`.

## Verification per agent
- Hermes: after restart, the MCP server list shows `open-design`.
- pi: `pi mcp list` (or equivalent) shows `open-design`.
- json agents: re-read the config file — an `open-design` entry is present and
  other servers are untouched.
