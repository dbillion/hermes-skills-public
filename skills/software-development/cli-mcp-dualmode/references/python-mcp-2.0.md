# Python `mcp` SDK 2.0.0 — stdio server pattern (verified)

Install (project venv has no `pip`; use uv):
```
source .venv/bin/activate
uv pip install "mcp"
```

Server skeleton (callback-constructor style — NOT the 1.x decorators):
```python
import anyio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool

def build() -> Server:
    s = Server("name", on_list_tools=_list, on_call_tool=_call)
    return s

async def _list(_ctx, _params) -> ListToolsResult:
    return ListToolsResult(tools=[Tool(name="channels", description="...",
        inputSchema={"type":"object","properties":{}})])
async def _call(_ctx, params) -> CallToolResult:
    return CallToolResult(content=[TextContent(type="text", text="ok")])

async def serve():
    server = build()
    # 2.0: stdio_server() returns a TUPLE, not an async context manager
    read, write = await stdio_server()
    await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    anyio.run(serve)
```

Smoke test over stdio (assert tools/list echoes back):
```python
import subprocess, json, time
p = subprocess.Popen(["tgf","mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def send(o): p.stdin.write(json.dumps(o)+"\n"); p.stdin.flush()
send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"s","version":"0"}}})
send({"jsonrpc":"2.0","method":"notifications/initialized"})
send({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
time.sleep(3); p.stdin.close()
out,_ = p.communicate(timeout=8)
# out contains initialize result + tools/list result with the tool list
```

Gotcha: 1.x used `@app.list_tools()` / `@app.call_tool()` decorators and
`async with stdio_server() as (r,w)`. Both are WRONG in 2.0.
