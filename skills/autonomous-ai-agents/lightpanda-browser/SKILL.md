---
name: lightpanda-browser
description: Lightpanda headless browser integration for Hermes Agent — CDP server mode, MCP server, browser engine configuration, and visual feedback via annotated screenshots.
---

# Lightpanda Browser Integration

Lightpanda is a headless browser engine that can be used as a faster alternative to Chrome for browser automation. It supports CDP (Chrome DevTools Protocol) and MCP (Model Context Protocol).

## Binary Location
- `/home/deeone/bin/lightpanda` (106MB, version ddd34dc5)

## Configuration

To enable Lightpanda as the browser engine:

```bash
hermes config set browser.engine lightpanda
hermes config set browser.lightpanda_path /home/deeone/bin/lightpanda
```

## CDP Server Mode

Lightpanda can run as a CDP server, allowing agent-browser to connect to it:

```bash
# Start Lightpanda CDP server (background)
/home/deeone/bin/lightpanda serve --host 127.0.0.1 --port 9222 --timeout 300

# Verify it's running
curl -s http://127.0.0.1:9222/json/version

# Connect agent-browser to it
agent-browser --cdp 9222 open https://example.com
agent-browser --cdp 9222 snapshot -i
agent-browser --cdp 9222 screenshot --annotate --output /tmp/screenshot.png
```

## MCP Server

Lightpanda provides an MCP server with 7 tools: `goto`, `markdown`, `links`, `evaluate`, `semantic_tree`, `interactiveElements`, `structuredData`.

Register in `~/.hermes/config.yaml` under `mcp_servers`:
```yaml
mcp_servers:
  lightpanda:
    command: "/home/deeone/bin/lightpanda"
    args: ["mcp"]
    timeout: 60
    connect_timeout: 30
```

## User Visibility

When the user wants to "see" what the browser is doing:
1. Take an annotated screenshot: `agent-browser --cdp 9222 screenshot --annotate --output /tmp/screenshot.png`
2. Open it on the desktop: `DISPLAY=:1 xdg-open /tmp/screenshot.png`
3. Lightpanda is headless — screenshots are the primary way to show the user what's happening

## Connecting to Existing Browser Sessions

To connect to an already-logged-in browser via CDP:
1. Find the browser's CDP port: `ss -tlnp | grep -E "922[0-9]"`
2. Note: `localhost` may work when `127.0.0.1` doesn't for CDP connections
3. WARNING: Headless Chrome instances with `--user-data-dir=/tmp/...` are temporary profiles without user sessions
4. Your actual logged-in desktop browser sessions are NOT accessible via CDP from the agent

## Cookie Injection for Authenticated Sites

Lightpanda is a separate browser instance with its own profile. Injecting cookies via `document.cookie` in CDP does NOT work for sites like LinkedIn that require full authentication flows. The proper approach is:

1. **For LinkedIn/authenticated sites:** Use email/password login flow via the bot, not cookie injection
2. **Cookie injection via CDP eval** only works for simple session tokens, not secure auth cookies
3. Fresh cookies from DevTools may still fail if the site requires additional tokens (e.g., `li_at` + `JSESSIONID` + `bcookie` + `li_rm` etc.)

## Subagent Browser Control

When the user wants interactive browser control with visual feedback, spawn a Gemini CLI subagent:
```
delegate_task(
    goal="Control Lightpanda browser via CDP. Navigate to URL, take annotated screenshots, and report back.",
    context="Lightpanda CDP server running on 127.0.0.1:9222. Use agent-browser --cdp 9222 commands. Open screenshots with DISPLAY=:1 xdg-open.",
    toolsets=["terminal"]
)
```
This gives the user a visible browser experience while the subagent handles CDP interaction.

## Chrome Fallback

Lightpanda automatically falls back to Chrome for unsupported actions (screenshots, PDF generation, file uploads, clipboard operations).
