# Raw stdio MCP probe (proves a server actually works, not just "config parses")

Use this when `hermes mcp test` isn't available, hangs, or you need to prove a
tool is callable end-to-end (e.g. before telling the user "it's installed").

## Key gotcha
Most community MCP servers (substack-mcp, etc.) speak **newline-delimited JSON**
on stdio — one JSON object per line, terminated by `\n`. They do NOT use LSP
`Content-Length: N\r\n\r\n` framing. Sending framed bytes makes them hang with
no reply (false negative). Send plain `{...}\n`.

## Ready-to-run probe
Replace `BIN` and the `env` block with your server's binary and credentials.

```python
#!/usr/bin/env python3
import subprocess, os, time, json, select

BIN = "/home/deeone/.npm/_npx/354e31246c6ee875/node_modules/substack-mcp/src/index.js"  # or your server
env = dict(os.environ)
env.update({
    "SUBSTACK_PUBLICATION_URL": "https://dbillion.substack.com/",
    "SUBSTACK_USER_ID": "36196425",
    "SUBSTACK_SESSION_TOKEN": "<PASTE_FULL_COOKIE_STRING>",
})

p = subprocess.Popen(["node", BIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, env=env, text=True, bufsize=1)

def rpc(id, method, params=None):
    msg = {"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}}
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()

def readline(timeout=30):
    r, _, _ = select.select([p.stdout], [], [], timeout)
    return p.stdout.readline() if r else None

time.sleep(2)  # let the server boot (esp. first npx fetch)

# 1. initialize
rpc(1, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                      "clientInfo": {"name": "v", "version": "1"}})
init = readline()
print("INIT:", (init[:200] if init else "NONE (server hung / wrong transport)"))

if init:
    # 2. ack + list tools
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized",
                              "params": {}}) + "\n")
    p.stdin.flush()
    rpc(2, "tools/list")
    tl = readline()
    print("TOOLS_LIST:", (tl[:600] if tl else "NONE"))

    # 3. optional: call a tool to prove end-to-end
    rpc(3, "tools/call", {"name": "create_draft_post", "arguments": {
        "title": "MCP Draft Test", "subtitle": "verify", "body": "<p>test</p>"}})
    resp = readline(60)
    print("TOOL_CALL:", (resp[:400] if resp else "NONE"))

p.terminate()
```

## Reading the result
- `INIT` shows `serverInfo` (name/version) → handshake OK.
- `TOOLS_LIST` shows the `tools:[]` array → server exposes what you expect.
- `TOOL_CALL` returning a result (not `error.code: -32603`) → end-to-end works.
- A `403` in TOOL_CALL means the **credential is expired**, not a config bug
  (see the 403 diagnosis section in SKILL.md). Confirm with a direct `curl`
  using the same cookie.

## First-run note
If `BIN` is an `npx -y pkg@latest` server, the first invocation downloads the
package. Point `BIN` at the cached path under `~/.npm/_npx/<hash>/node_modules/<pkg>/`
to skip the npx resolution delay and avoid re-fetch hangs.
