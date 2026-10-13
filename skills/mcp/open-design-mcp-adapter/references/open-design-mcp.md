# Open Design MCP — exact config + verification snippets

## Config block to insert into `~/.hermes/config.yaml`

Insert AFTER the last `mcp_servers:` entry (do NOT edit the file with
`patch`/`write_file`/`yaml.safe_dump` — they strip comments / reorder keys).

```yaml
  open-design:
    command: "/home/deeone/.nvm/versions/node/v24.19.0/bin/node"
    args:
      - "/home/deeone/open-design/open-design/apps/daemon/dist/cli.js"
      - "mcp"
      - "--daemon-url"
      - "http://127.0.0.1:7456"
    env:
      OD_DATA_DIR: "/home/deeone/open-design/open-design/.od"
```

## Surgical insertion (Python, preserves comments/order)

```python
path = "/home/deeone/.hermes/config.yaml"
lines = open(path).readlines()
# find the mcp_servers block and the last entry (mcp-cli) end line
mcp_start = next(i for i,l in enumerate(lines) if l.strip()=="mcp_servers:")
# last 2-space-indented key before next top-level key is the last entry
last = max(i for i,l in enumerate(lines) if i>mcp_start and l.startswith("  ") and not l.startswith("   ") and l.strip().endswith(":"))
block = '''  open-design:
    command: "/home/deeone/.nvm/versions/node/v24.19.0/bin/node"
    args:
      - "/home/deeone/open-design/open-design/apps/daemon/dist/cli.js"
      - "mcp"
      - "--daemon-url"
      - "http://127.0.0.1:7456"
    env:
      OD_DATA_DIR: "/home/deeone/open-design/open-design/.od"
'''
lines.insert(last+1, "\n"+block)
open(path,"w").writelines(lines)
```

## Live verification (stdio JSON-RPC handshake, NDJSON framing)

```python
import subprocess, json
cmd = ["/home/deeone/.nvm/versions/node/v24.19.0/bin/node",
       "/home/deeone/open-design/open-design/apps/daemon/dist/cli.js",
       "mcp","--daemon-url","http://127.0.0.1:7456"]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True)
def send(obj): p.stdin.write(json.dumps(obj)+"\n"); p.stdin.flush()
def read():
    line=p.stdout.readline()
    return json.loads(line) if line.strip() else None
send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{
    "protocolVersion":"2024-11-05",
    "capabilities":{},"clientInfo":{"name":"probe","version":"1"}}})
print("init:", read())
send({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
tl = read()
tools = tl.get("result",{}).get("tools",[]) if tl else []
print("serverInfo ok, tools:", len(tools), [t["name"] for t in tools[:5]])
```

Expect: `serverInfo: open-design v0.2.0`, ~22 tools.

## systemd --user service (auto-start, survives reboot)

`~/.config/systemd/user/open-design-daemon.service`:
```ini
[Unit]
Description=Open Design local daemon (MCP + agent adapter for Hermes)
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/deeone/open-design/open-design
Environment=PATH=/home/deeone/.nvm/versions/node/v24.19.0/bin:/usr/bin:/bin
Environment=OD_DATA_DIR=/home/deeone/open-design/open-design/.od
ExecStart=/home/deeone/.nvm/versions/node/v24.19.0/bin/node /home/deeone/open-design/open-design/apps/daemon/bin/od.mjs --no-open
Restart=on-failure

[Install]
WantedBy=default.target
```
Enable: `systemctl --user enable --now open-design-daemon.service`.
Verify: `systemctl --user is-enabled open-design-daemon` → `enabled`;
`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7456/api/health` → `200`.
