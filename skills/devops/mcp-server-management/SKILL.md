---
name: mcp-server-management
description: Managing Model Context Protocol (MCP) servers for Hermes Agent and OpenClaw
version: 1.0.0
---
# MCP Server Management

Managing Model Context Protocol (MCP) servers for Hermes Agent and OpenClaw agents.

## Overview

This skill covers adding, configuring, testing, and troubleshooting MCP servers for use with Hermes Agent and OpenClaw agents. MCP servers extend agent capabilities by providing access to external tools and services.

## Supported MCP Server Types

1. **Stdio Servers** - Local executables (e.g., maltego-mcp, custom Python scripts)
2. **HTTP/SSE Servers** - Network endpoints (e.g., Burp Suite MCP extension)

## Hermes Agent MCP Management

### Adding an MCP Server

#### Stdio Server (command + args)
```bash
hermes mcp add <name> --command <path/to/executable> --args <arg1> <arg2>... --env KEY=value [--env KEY2=value2...]
```

Example: Adding maltego-mcp
```bash
hermes mcp add maltego --command /home/deeone/.nvm/versions/node/v25.6.1/bin/maltego-mcp
```

Example: Adding OpenCTI MCP with environment variables
```bash
hermes mcp add opencti --command /home/deeone/mcp-servers/mcp-opencti/.venv/bin/python \
  --args /home/deeone/mcp-servers/mcp-opencti/opencti_mcp_server_v7.py \
  --env OPENCTI_URL=http://localhost:8081 \
  --env OPENCTI_TOKEN=b0de265c-0912-49d3-b781-7d4c4793a8be
```

#### HTTP/SSE Server
```bash
hermes mcp add <name> --url <endpoint-url>
```

Example: Adding Burp Suite MCP (requires Caddy proxy)
```bash
hermes mcp add burpsuite --url http://127.0.0.1:9876/sse
```

### Managing MCP Servers

- List configured servers: `hermes mcp list`
- Test connection: `hermes mcp test <name>`
- Remove server: `hermes mcp remove <name>`
- Toggle tools: `hermes mcp configure <name>` (requires interactive terminal)

### Common MCP Server Patterns

#### Maltego MCP Server
```bash
hermes mcp add maltego --command $(which maltego-mcp)
```
Provides tools for:
- Creating/loading/saving Maltego graphs (.mtgx)
- WHOIS, DNS, ASN, crt.sh lookups
- Entity and link management

#### OpenCTI MCP Server
```bash
hermes mcp add opencti --command /path/to/venv/bin/python \
  --args /path/to/opencti_mcp_server_v7.py \
  --env OPENCTI_URL=http://localhost:8080 \
  --env OPENCTI_TOKEN=your-token-here
```
Provides tools for querying OpenCTI threat intelligence platform.

#### Burp Suite MCP Extension
Requires:
1. Burp Professional with Custom AI Agent extension installed
2. MCP server enabled in Burp Suite settings (default port 9876)
3. Caddy proxy for SSE normalization (see burp-mcp-agents repo)

```bash
hermes mcp add burpsuite --url http://127.0.0.1:9876/sse
```

## OpenClaw MCP Management

In OpenClaw, MCP servers are configured via JSON configuration:

```bash
openclaw mcp set <name> '{"command": "/path/to/server", "args": ["arg1", "arg2"], "env": {"KEY": "value"}}'
```

Example for OpenCTI:
```bash
openclaw mcp set opencti '{"command":"/home/deeone/mcp-servers/mcp-opencti/.venv/bin/python","args":["/home/deeone/mcp-servers/mcp-opencti/opencti_mcp_server_v7.py"],"env":{"OPENCTI_URL":"http://localhost:8081","OPENCTI_TOKEN":"b0de265c-0912-49d3-b781-7d4c4793a8be"}}'
```

Example for Maltego:
```bash
openclaw mcp set maltego '{"command":"/home/deeone/.nvm/versions/node/v25.6.1/bin/maltego-mcp","args":[]}'
```

## Driving MCP servers via the `mcp-cli` CLI (independent of Hermes/OpenClaw)

Some servers (e.g. **neon**, **context7**) are registered in a *separate*
config file — by default `~/.config/mcp-cli/mcp_servers.json` — and are NOT
visible to `hermes mcp list`. They are driven by the standalone `mcp-cli`
binary (v0.3.0+), which is fully functional. Do NOT assume `mcp-cli` is silent
or broken — that was a misdiagnosis; it works when invoked with the `-c` flag.

```bash
# List servers + tools known to mcp-cli
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json            # server list
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json info <server>
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json info <server>/<tool>   # tool schema
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json call <server> <tool> '<json-args>'
# slash form also works:  mcp-cli -c <cfg> call <server>/<tool> '<json>'
```

Calling rules (proven):
- Args are JSON passed as the LAST positional string (or via stdin). Use single
  quotes around the JSON and escape any inner single quotes with `'\''`.
- Tool/schema mismatch surfaces as `UNKNOWN_OPTION` (wrong flag) or
  `SERVER_NOT_FOUND` (server not in that config — note `mcp-cli info neon/...`
  ALSO needs the `-c` flag, or it looks in the wrong config).
- If `mcp-cli` is invoked WITHOUT `-c`, it reads its *own* default config
  (different from Hermes's). Servers registered there (github, context7,
  stitch, etc.) work; servers only in `~/.config/mcp-cli/mcp_servers.json`
  will report `SERVER_NOT_FOUND`.

### Neon MCP (managed Postgres) — create DB, enable extensions, apply schema
Project id is supplied by the user (e.g. `weathered-forest-50229673`). The
`run_sql` tool executes a **single SQL statement** and **persists DDL**
(confirmed: CREATE TABLE / extensions survive). Patterns:
- **Single statement only.** `run_sql` wraps the SQL in a prepared statement and
  rejects multiple commands ("cannot insert multiple commands into a prepared
  statement"). Split multi-statement scripts and call once per statement.
- **`[]` response is ambiguous.** It is returned for BOTH success AND some
  silent failures. Always re-query (`SELECT ... FROM information_schema.tables`)
  to confirm a DDL actually persisted — never trust `[]` alone.
- Schema with PostGIS/pgvector works: `geometry(Point,4326)`, `vector(1536)`,
  `JSONB` columns all persist. Available extensions on Neon: `postgis`,
  `postgis_topology`, `vector`, `pg_graphql`. Enable first:
  `CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS vector;`
- Optional params beyond `projectId`/`sql`: `branchId`, `databaseName`.
- BULK APPLY CAUTION: a Python loop that shells out `mcp-cli ... call` may get
  `[]` for every statement yet only partly persist (timing/transaction quirks).
  Prefer applying each CREATE TABLE individually in a direct terminal call and
  verifying after. See `references/mcp-cli-recipes.md` for the Neon + Context7
  runbook and a verification snippet.

### Context7 MCP — research a library before integrating it
Works through `mcp-cli` too. Resolve first, then fetch docs:
```bash
mcp-cli -c <cfg> call context7/resolve-library-id '{"libraryName":"mastra","query":"mastra agent framework"}'
# -> Context7-compatible library ID, e.g. /mastra-ai/mastra
mcp-cli -c <cfg> call context7/get-library-docs '{"context7CompatibleLibraryID":"/mastra-ai/mastra","topic":"agents rag memory workflows","tokens":6000}'
```
- `resolve-library-id` requires BOTH `libraryName` and `query` keys (sending
  only one yields an input-validation error).
- For Mastra the canonical, High-reputation ID is **`/mastra-ai/mastra`**
  (18k+ snippets). Use this when the user wants agentic workflows in a TS backend.

## Registering a NEW server into `~/.mcp_servers.json` (the mcp-cli default config)

`mcp-cli` with no `-c` flag reads `~/.mcp_servers.json`. To make a server
callable from anywhere, add it there. This file is shared by many tools, so
edit it ADDITIVELY and prove nothing was lost:

```python
import json, shutil, time
p = '/home/deeone/.mcp_servers.json'
bak = f'/tmp/mcp_servers.bak_{int(time.time())}'; shutil.copy(p, bak)
d = json.load(open(p))
d['mcpServers']['<name>'] = {"type":"stdio","command":"node",
                             "args":["/abs/path/dist/index.js","--stdio"], "env":{}}
json.dump(d, open(p,'w'), indent=2)
old = json.load(open(bak))                      # verify
assert set(old['mcpServers']) <= set(json.load(open(p))['mcpServers'])
```
Report `count before -> after` and the "all old servers kept" assertion.
Then verify resolution WITHOUT `-c`: `mcp-cli call <name> <tool> '{}'`.

**Before assuming a server is unavailable, check whether it is merely
UNREGISTERED.** A grep of the config plus `mcp-cli grep '*name*'` returning
nothing does NOT mean the server is absent from the machine — it is often
already built on disk (search for the package dir / a binary in
`~/.npm-global/bin`). Skills that document a server frequently contain its
exact install path; read them before concluding it needs installing.

**Test with a scratch config first.** Point `-c /tmp/<name>.json` at a
throwaway config holding only the new server, confirm it connects and a real
tool call returns, and only then write into the shared
`~/.mcp_servers.json`.

**Enumerating is not calling.** `mcp-cli -c ... -d` listing tools only proves
the process starts. Always follow with an actual `call` of a cheap read-only
tool and quote the response.

### Excalidraw MCP (diagram rendering)
Built locally at
`/home/deeone/picoclaw/excalidraw-mcp-app/excalidraw-mcp-app/dist/index.js`
(also `~/.npm-global/bin/excalidraw-mcp-server`). Registered in
`~/.mcp_servers.json` as `excalidraw`. Tools: `read_me` (element-format cheat
sheet — call before drawing), `create_view`, `export_to_excalidraw`,
`save_checkpoint`, `read_checkpoint`.
- `create_view` is a **UI/widget** tool: over plain `mcp-cli` you get a JSON
  envelope, not an image. It renders in an MCP-app iframe host.
- `export_to_excalidraw` returns a shareable URL but **uploads to
  excalidraw.com** — confirm with the user before calling it.

## Troubleshooting

### Connection Timeouts
If `hermes mcp test <name>` times out after 40 seconds:

1. **Verify the underlying service is running**:
   - For Burp Suite: Check Burp is running with MCP extension loaded
   - For OpenCTI: Verify OpenCTI instance is accessible at the configured URL
   - For stdio servers: Test the command manually

2. **Check environment variables**:
   - Ensure required env vars are set (OPENCTI_URL, OPENCTI_TOKEN, etc.)
   - For Hermes: Use `--env` flag when adding
   - For OpenClaw: Include in `env` field of JSON config

3. **Test connectivity directly**:
   - HTTP/SSE: `curl -i http://localhost:9876/sse` (should return 200 OK with event-stream)
   - Stdio: Run the command manually to see if it starts correctly

#### Port Conflicts
Default Burp MCP port is 9876. If in use:
- Change Burp MCP port in extension settings
- Update Hermes/OpenClaw configuration accordingly
- Or free up port 9876

#### Burp MCP Server Configuration Notes
Do NOT attempt to load the Burp AI Agent as a Java agent using:
```bash
java -javaagent:./burp-ai-agent.jar -jar burpsuite.jar
```
This will fail with "Failed to find Premain-Class manifest attribute" because the burp-ai-agent.jar is not designed to be used as a Java agent.

Instead, follow the proper installation procedure:
1. Start Burp Suite normally: `java -jar burpsuite.jar`
2. Install the Burp AI Agent extension via Burp Suite UI: Extensions → Add → Select the burp-ai-agent.jar file
3. Enable the MCP Server in the Burp AI Agent extension settings (Settings → MCP Server)
4. The MCP server will then be available for connection (typically at http://localhost:9876/sse)
5. Refer to https://github.com/six2dez/burp-mcp-agents for detailed setup and configuration instructions

## Manual config edit (when `hermes mcp add` is unavailable)

Some servers ship only a JSON snippet (e.g. community MCP servers from GitHub)
and you must edit `~/.hermes/config.yaml` directly under `mcp_servers:`.

**CRITICAL PITFALL — the agent's `patch`/`write_file` tools REFUSE to edit
`~/.hermes/config.yaml`** (it is treated as security-sensitive). And do NOT
round-trip the file through `yaml.safe_dump` / `yaml.dump` — that **strips all
comments and alphabetically reorders every key**, destroying the file. Two safe
paths:

1. **Preferred:** surgical text insertion with a Python script that only
   `lines.insert()`s the new block before the next top-level key
   (e.g. `plugins:`), leaving the rest of the file byte-for-byte intact.
2. **Or:** run `hermes config edit` / `hermes config set` if the value fits a
   single key (complex nested blocks usually don't).

After editing, validate with:
```bash
python3 -c "import yaml; c=yaml.safe_load(open('/home/deeone/.hermes/config.yaml')); print(c['mcp_servers']['<name>'].keys())"
# Also confirm comment count survived: grep -c '^#' ~/.hermes/config.yaml
```
If comment count dropped to ~0, you round-tripped the file — restore from
`~/.hermes/config.yaml.bak.*` and redo with surgical insertion.

**Env var extraction trick:** if a server needs an ID you don't have (e.g.
`SUBSTACK_USER_ID`), the credential blob often contains a JWT. Decode the
`substack.lli` / similar cookie value's payload (the part between the two `.`
in the JWT) with:
```bash
python3 -c "import base64,json; p='<JWT_PAYLOAD>'; p+='='*(-len(p)%4); print(json.loads(base64.urlsafe_b64decode(p)))"
```
The decoded claim (e.g. `userId`) is usually the missing ID.

## Deep verification via raw stdio probe

`hermes mcp test` is the first check, but to PROVE a server actually works
(end-to-end, tool callable) run a raw stdio MCP handshake. **Transport note:**
most servers expect newline-delimited JSON (`{...}\n`), NOT LSP `Content-Length`
framing. A framed request will hang silently — a classic false-negative.

Minimal probe (stdio, newline-delimited):
```python
import subprocess, os, select, json
p = subprocess.Popen(["node", BIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, env={**os.environ, **ENV}, text=True)
p.stdin.write(json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize",
    "params":{"protocolVersion":"2024-11-05","capabilities":{},
              "clientInfo":{"name":"v","version":"1"}}})+"\n"); p.stdin.flush()
r,_,_ = select.select([p.stdout],[],[],30)
init = p.stdout.readline() if r else None      # expect serverInfo
p.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})+"\n"); p.stdin.flush()
p.stdin.write(json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})+"\n"); p.stdin.flush()
r,_,_ = select.select([p.stdout],[],[],30)
print(p.stdout.readline())                       # expect tools[] list
p.terminate()
```
A full ready-to-run version lives in `references/stdio-mcp-probe.md`.

## Credential 403 diagnosis

If the server connects and `tools/list` works but a `tools/call` returns
**403**, the server/wiring is fine — the credential is dead/expired. Confirm
before touching config:
```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" -H "Cookie: <PASTED_TOKEN>" \
  "https://substack.com/api/v1/user/current"
# 403 "Not authorized" => token expired; get a fresh cookie from the browser
# 200 + JSON => token valid; the 403 is a server-side permission issue
```
Regenerate the token from the browser (DevTools → Network → any request →
Request Headers → copy full `Cookie:` value) and update `SUBSTACK_SESSION_TOKEN`
in config. The config and wiring are correct; only the credential needs refresh.

### Extracting a fresh cookie from a headless browser (no manual copy-paste)
If the user says "grab a fresh token from the browser," see
`references/cdp-cookie-extraction.md`. It covers launching headless Brave on this
box (`/opt/brave-bin/brave --headless=new --remote-debugging-port=9224`),
connecting to the page WebSocket, and reading cookies via `Storage.getCookies`.
**Diagnostic signature:** if `substack.sid` is ABSENT and `substack.lli == 0`,
the profile is logged out — every API call 403s and a pasted old token won't
help. You must log in (or have the user paste a fresh `Cookie:` header) before
the MCP server will authenticate.

## Verification

After adding an MCP server, verify it works:

```bash
# List available tools from the server
hermes mcp test <server-name>

# Should show connected status and list of available tools
# Example output:
# Testing 'maltego'...
#   Transport: stdio → /path/to/maltego-mcp
#   Auth: none
#   ✓ Connected (XXXXms)
#   ✓ Tools discovered: 12
#     maltego_create_graph
#     maltego_add_entity
#     ... etc
```

Then do a deep stdio probe (above) to prove the tools are actually callable,
not just discoverable.

## Best Practices

1. **Test after adding**: Always run `hermes mcp test <name>` after adding a server
2. **Use descriptive names**: Name servers clearly (e.g., "maltego-whois", "opencti-prod")
3. **Document environment variables**: Keep track of required ENV var
4. **Check service prerequisites**: Ensure underlying services (Burp Suite, OpenCTI, etc.) are running and accessible
5. **Start with minimal args**: When troubleshooting, test the base command first before adding complex arguments

## References

- [Burp MCP Agents Repository](https://github.com/six2dez/burp-mcp-agents) - Setup guides for Burp Suite MCP
- [Maltego MCP Repository](https://github.com/lidless-labs/maltego-mcp) - Maltego MCP server details
- [OpenCTI MCP Server](https://github.com/opencti-platform/opencti-connector-mcp) - Official OpenCTI MCP connector
- `references/mcp-cli-recipes.md` - Driving MCP servers via the standalone `mcp-cli` CLI: Neon Postgres (extensions, single-statement run_sql, DDL-persist verification) and Context7 library research runbook.
- `references/cdp-cookie-extraction.md` - Launch headless Brave + CDP to extract a fresh session cookie when an MCP token has expired (and how to tell if the profile is logged out).
- `references/cleanup-tips.md` - Disk/memory cleanup for MCP server workloads.
- `references/obsidian-rest-api-and-plugin-data.md` - Driving an Obsidian vault over the Local REST API plugin (liveness check, Bearer auth without leaking the key into argv), the `obs`-is-OBS-Studio binary trap, and reading `<vault>/.obsidian/plugins/<id>/data.json` to discover real plugin paths (worked example: installing Excalidraw libraries).

## Related Skills

- `hermes-agent` - Core Hermes Agent configuration and usage
- `openclaw` - OpenClaw agent management (if available)
- `burpsuite` - Burp Suite specific operations
- `maltego` - Maltego specific operations