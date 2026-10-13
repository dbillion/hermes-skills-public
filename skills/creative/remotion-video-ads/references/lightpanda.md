# Lightpanda Browser Integration

## Overview

Lightpanda is a headless browser written in Zig for AI agent automation. 1.3-5.8x faster than Chrome for navigation. It has no GUI — all interaction is via CDP or MCP.

## Installation

Binary: `/home/deeone/bin/lightpanda` (version ddd34dc5, ~106MB)

```bash
# Check version
lightpanda version

# Commands: fetch, serve, mcp, version, help
```

## Configuration

### Browser Engine (Hermes config.yaml)

```yaml
browser:
  engine: lightpanda
  lightpanda_path: /home/deeone/bin/lightpanda
  cdp_url: ''  # Leave empty for direct engine mode
```

Set via CLI: `hermes config set browser.engine lightpanda`

### MCP Server (Hermes config.yaml)

```yaml
mcp_servers:
  lightpanda:
    command: "/home/deeone/bin/lightpanda"
    args: ["mcp"]
    timeout: 60
    connect_timeout: 30
```

MCP tools exposed: `goto`, `markdown`, `links`, `evaluate`, `semantic_tree`, `interactiveElements`, `structuredData`

## CDP Server Mode

Lightpanda can run as a CDP server for external browser attachment:

```bash
# Start CDP server (background)
lightpanda serve --host 127.0.0.1 --port 9222 --timeout 300 &

# Verify
curl http://127.0.0.1:9222/json/version
# Returns: {"webSocketDebuggerUrl": "ws://127.0.0.1:9222/"}
```

### Connecting agent-browser to Lightpanda CDP

```bash
export AGENT_BROWSER_CDP_URL="http://127.0.0.1:9222"
agent-browser --cdp 9222 open https://example.com
agent-browser --cdp 9222 screenshot --annotate --output /tmp/screenshot.png
agent-browser --cdp 9222 snapshot
```

### Taking Screenshots (since Lightpanda has no GUI)

Lightpanda is headless — there is no visual window. To "see" what it renders:

1. **Annotated screenshot** (labels interactive elements):
   ```bash
   agent-browser --cdp 9222 screenshot --annotate --output /tmp/page.png
   ```

2. **Full page screenshot**:
   ```bash
   agent-browser --cdp 9222 screenshot --full --output /tmp/page-full.png
   ```

3. **Open screenshot on desktop**:
   ```bash
   DISPLAY=:1 xdg-open /tmp/page.png
   ```

4. **Via Hermes browser tools**: `browser_vision` captures screenshots to `~/.hermes/cache/screenshots/` (but vision analysis requires a model that supports image input; if current model doesn't, use `xdg-open` to view directly)

## Chrome Fallback

Automatic for unsupported actions:
- Screenshots (use agent-browser directly for CDP screenshots)
- PDF generation
- File uploads
- Clipboard operations

## Session Persistence & Authentication

Lightpanda CDP sessions maintain cookies/state. For authenticated sites:
- Navigate to login page via `browser_navigate`
- Fill credentials via `browser_type` / `browser_click`
- Session persists across navigations within the same CDP connection
- **Security note**: Never enter credentials without explicit user permission

## agent-browser Path

The agent-browser CLI is at:
```
/home/deeone/.hermes/hermes-agent/node_modules/.bin/agent-browser
```

Not on system PATH — always use full path.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `agent-browser: command not found` | Use full path above |
| Screenshot shows wrong page | agent-browser has its own session; navigate it separately or use `--cdp` flag |
| Lightpanda CDP not responding | Check `curl http://127.0.0.1:9222/json/version`; restart with `lightpanda serve` |
| Vision analysis fails (404) | Current model may not support image input; use `DISPLAY=:1 xdg-open <path>` to view screenshots |
