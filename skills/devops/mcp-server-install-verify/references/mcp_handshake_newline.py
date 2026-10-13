#!/usr/bin/env python3
"""
Reusable MCP stdio handshake harness for newline-delimited-JSON servers
(e.g. substack-mcp). Proves a server works: initialize -> tools/list.

Usage:
  python3 mcp_handshake_newline.py --cmd npx --args "-y" --args "substack-mcp@latest" \
      --env SUBSTACK_PUBLICATION_URL=... --env SUBSTACK_SESSION_TOKEN=... --env SUBSTACK_USER_ID=...

Or edit ENV below and run directly.
"""
import subprocess, os, sys, time, json, select, argparse

ENV = {
    "SUBSTACK_PUBLICATION_URL": "https://dbillion.substack.com/",
    "SUBSTACK_USER_ID": "36196425",
    # SUBSTACK_SESSION_TOKEN left blank on purpose — fill before use
    "SUBSTACK_SESSION_TOKEN": "",
}

def rpc(p, id, method, params=None):
    p.stdin.write(json.dumps({"jsonrpc":"2.0","id":id,"method":method,
                              "params":params or {}}) + "\n")
    p.stdin.flush()

def readline(p, timeout=30):
    r,_,_ = select.select([p.stdout],[],[],timeout)
    return p.stdout.readline() if r else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", default="node")
    ap.add_argument("--args", action="append", default=[])
    ap.add_argument("--env", action="append", default=[], help="KEY=VALUE")
    ap.add_argument("--bin", default=None, help="direct path to server entry (skips npx)")
    a = ap.parse_args()

    env = dict(os.environ)
    env.update(ENV)
    for e in a.env:
        k,v = e.split("=",1); env[k]=v

    cmd = [a.bin] if a.bin else [a.cmd] + a.args
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env, text=True, bufsize=1)
    time.sleep(2)
    rpc(p, 1, "initialize", {"protocolVersion":"2024-11-05","capabilities":{},
                             "clientInfo":{"name":"verify","version":"1"}})
    init = readline(p)
    print("INIT:", (init[:200] if init else "NONE (server may use LSP framing, not newline)"))
    if not init:
        p.terminate(); sys.exit(2)
    p.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized",
                              "params":{}}) + "\n"); p.stdin.flush()
    rpc(p, 2, "tools/list")
    tl = readline(p)
    print("TOOLS:", (tl[:600] if tl else "NONE"))
    p.terminate()

if __name__ == "__main__":
    main()
