# Open Design → Hermes MCP install (verified recipe)

Captured from a live session (tgforwarder / OD v0.19.2). This is the byte-exact
flow that worked; the parent SKILL.md explains the theory.

## 1. Start the daemon (ephemeral port)
```bash
cd /home/deeone/open-design/open-design
pnpm tools-dev          # foreground dev server; or run as background=true
```
Note the printed ports, e.g.:
```
Web:    http://127.0.0.1:46559/
Daemon: http://127.0.0.1:43471/
```
The **daemon** port (43471) is what `mcp install` needs — NOT 7456.

## 2. Confirm daemon health
```bash
curl -s http://127.0.0.1:43471/api/health
# -> {"ok":true,"version":"0.19.2"}
```

## 3. Install OD's MCP into Hermes
```bash
cd /home/deeone/open-design/open-design
export OD_DAEMON_URL="http://127.0.0.1:43471"
opendesign mcp install hermes            # registers into Hermes config
opendesign mcp install hermes --dry-run --json   # safe preview
```

## 4. Gotchas
- `od` on PATH = GNU coreutils octal dump. Use `opendesign` (pnpm symlink).
- `hermes` is a valid agent for `mcp install`.
- If foreground terminal calls start returning exit 130, the dev server is
  holding the PTY — re-run steps as `background=true`.
- `mcp install` reads the daemon's `/api/mcp/install-info` for the exact launch
  command, so it matches the Settings → MCP panel.
