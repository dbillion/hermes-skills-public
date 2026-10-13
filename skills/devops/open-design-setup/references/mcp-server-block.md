# Open Design MCP server block (the exact payload `od` emits)

Every `od mcp install <agent>` (manual strategy) prints the same launch spec.
Paths below are the values used on this box — adjust to your install location.

## For Hermes (`~/.hermes/config.yaml` — YAML via `hermes config set`)
```yaml
mcp_servers:
  open-design:
    command: "/home/deeone/.nvm/versions/node/v24.19.0/bin/node"
    args: ["/home/deeone/open-design/open-design/apps/daemon/dist/cli.js", "mcp"]
    env:
      OD_DATA_DIR: "/home/deeone/open-design/open-design/.od"
      OD_SIDECAR_IPC_PATH: "/tmp/open-design/ipc/default/daemon.sock"
```
Apply with:
```sh
hermes config set mcp_servers.open-design.command "/home/deeone/.nvm/versions/node/v24.19.0/bin/node"
hermes config set mcp_servers.open-design.args '["/home/deeone/open-design/open-design/apps/daemon/dist/cli.js", "mcp"]'
hermes config set mcp_servers.open-design.env.OD_DATA_DIR "/home/deeone/open-design/open-design/.od"
hermes config set mcp_servers.open-design.env.OD_SIDECAR_IPC_PATH "/tmp/open-design/ipc/default/daemon.sock"
```

## For pi (`~/.pi/agent/mcp.json` — JSON `mcpServers`)
```json
{
  "mcpServers": {
    "open-design": {
      "command": "/home/deeone/.nvm/versions/node/v24.19.0/bin/node",
      "args": ["/home/deeone/open-design/open-design/apps/daemon/dist/cli.js", "mcp"],
      "env": {
        "OD_DATA_DIR": "/home/deeone/open-design/open-design/.od",
        "OD_SIDECAR_IPC_PATH": "/tmp/open-design/ipc/default/daemon.sock"
      }
    }
  }
}
```

## Key fields
- `command`: the **Node 24** binary — never the system `node` if it's v25/v22
  (better-sqlite3 is ABI 137 / Node 24; wrong node → ERR_DLOPEN_FAILED).
- `args`: always `[<path>/apps/daemon/dist/cli.js, "mcp"]`.
- `OD_DATA_DIR`: the daemon's data root (`.od` next to the repo, or wherever the
  daemon was started with).
- `OD_SIDECAR_IPC_PATH`: the unix socket the daemon created
  (`/tmp/open-design/ipc/default/daemon.sock`). The `mcp` subcommand discovers the
  live daemon even if the port is ephemeral, so this is the stable anchor.

## Troubleshooting
- Server won't connect → confirm socket exists: `ls /tmp/open-design/ipc/default/daemon.sock`.
- `ERR_DLOPEN_FAILED` → the `command` node is not v24. Repoint to the v24 binary.
- Empty/old config → restart the agent (Hermes / pi) to re-read MCP config.
