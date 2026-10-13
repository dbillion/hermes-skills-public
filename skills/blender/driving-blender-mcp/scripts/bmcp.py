#!/usr/bin/env python3
"""Minimal Blender MCP addon client (TCP JSON-RPC on localhost:9876).

Usage: python3 bmcp.py '<json-command>'
Connects to the running Blender MCP addon, sends one JSON command object
{"type": ..., "params": {...}}, prints the parsed JSON response.
Exit code 0 on status=success, 1 on error, 2 on usage error.
"""
import json
import socket
import sys

HOST = "127.0.0.1"
PORT = 9876
TIMEOUT = 90.0


def send_command(cmd: dict) -> dict:
    payload = json.dumps(cmd).encode("utf-8")
    with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as sock:
        sock.sendall(payload)
        sock.settimeout(TIMEOUT)
        buf = b""
        while True:
            try:
                chunk = sock.recv(65536)
            except socket.timeout:
                break
            if not chunk:
                break
            buf += chunk
            try:
                return json.loads(buf.decode("utf-8"))
            except json.JSONDecodeError:
                continue
    if not buf:
        raise RuntimeError("no response received from Blender addon")
    return json.loads(buf.decode("utf-8"))


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: bmcp.py '<json-command>'", file=sys.stderr)
        return 2
    cmd = json.loads(sys.argv[1])
    resp = send_command(cmd)
    print(json.dumps(resp, indent=2))
    return 0 if resp.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
