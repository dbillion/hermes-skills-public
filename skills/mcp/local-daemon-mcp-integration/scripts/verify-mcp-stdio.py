#!/usr/bin/env python3
"""Verify a stdio MCP server with a real JSON-RPC handshake.

Usage:
  python3 verify-mcp-stdio.py --cmd /path/to/node --args '/repo/dist/cli.js' 'mcp' '--daemon-url' 'http://127.0.0.1:7456' --env OD_DATA_DIR=/repo/.od

Sends `initialize` then `tools/list` over NEWLINE-DELIMITED JSON (NOT LSP
framing) and prints serverInfo + tool names. Exit 0 if both succeed.
"""
import argparse
import json
import os
import select
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", required=True, help="executable (e.g. node binary)")
    ap.add_argument("--args", nargs="+", required=True, help="args for the MCP server")
    ap.add_argument("--env", action="append", default=[], help="KEY=VALUE env overrides")
    ap.add_argument("--call", help="optional tool name to call after tools/list")
    ap.add_argument("--init-timeout", type=int, default=30)
    ap.add_argument("--call-timeout", type=int, default=30)
    a = ap.parse_args()

    env = dict(os.environ)
    for kv in a.env:
        k, _, v = kv.partition("=")
        env[k] = v

    p = subprocess.Popen(
        [a.cmd, *a.args], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env=env, text=True,
    )

    def send(obj):
        p.stdin.write(json.dumps(obj) + "\n")
        p.stdin.flush()

    def readline(t):
        r, _, _ = select.select([p.stdout], [], [], t)
        return p.stdout.readline() if r else None

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                         "clientInfo": {"name": "verify", "version": "1"}}})
        init = readline(a.init_timeout)
        if not init or not init.strip():
            print("INIT FAILED/TIMEOUT"); return 1
        msg = json.loads(init)
        print("INIT serverInfo:", json.dumps(msg.get("result", {}).get("serverInfo")))
        send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        t = readline(a.call_timeout)
        if not t or not t.strip():
            print("tools/list FAILED/TIMEOUT"); return 1
        tools = json.loads(t).get("result", {}).get("tools", [])
        print("TOOL COUNT:", len(tools))
        print("TOOLS:", [x["name"] for x in tools])
        if a.call:
            send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                  "params": {"name": a.call, "arguments": {}}})
            c = readline(a.call_timeout)
            print("CALL RESULT:", (c or "NONE").strip()[:600])
        return 0
    finally:
        p.terminate()
        try:
            p.wait(timeout=5)
        except Exception:
            p.kill()


if __name__ == "__main__":
    sys.exit(main())
