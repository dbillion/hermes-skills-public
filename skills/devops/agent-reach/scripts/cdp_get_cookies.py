#!/usr/bin/env python3
"""CDP client: extract a site's cookies (INCLUDING HttpOnly li_at) from a live
debug-enabled Chrome, bypassing on-disk app-bound encryption.

Prereqs:
  - A Chrome launched with --remote-debugging-port=9222 against a profile COPY
    (see references/cookie-cdp-extraction.md). Endpoint: http://127.0.0.1:9222
  - python `websockets` (pip install websockets). Tested on websockets 15.x.

Usage:
  python3 cdp_get_cookies.py [--port 9222] [--domain linkedin.com] [--out /tmp/li_cookies.json]

Writes a Playwright storage_state.json-shaped file:
  {"cookies": [{name, value, domain, path, expires, httpOnly, secure, sameSite}, ...]}
and prints each cookie name + httpOnly flag, plus HAS_LI_AT.
"""
import argparse
import asyncio
import json
import sys
import urllib.request

try:
    import websockets
except ImportError:
    sys.exit("Missing dep: pip install websockets")


def get_page_ws(port):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as r:
        targets = json.load(r)
    page = next((t for t in targets if t.get("type") == "page"), None)
    if not page:
        raise SystemExit("NO_PAGE_TARGET on CDP endpoint")
    return page["webSocketDebuggerUrl"]


async def main(port, domain, out):
    ws_url = get_page_ws(port)
    async with websockets.connect(ws_url, max_size=None) as ws:
        counter = {"n": 1}

        async def send(method, params=None):
            rid = counter["n"]
            counter["n"] += 1
            payload = {"id": rid, "method": method}
            if params is not None:
                payload["params"] = params
            await ws.send(json.dumps(payload))
            return rid

        await send("Network.enable")
        await send("Page.enable")
        # Bring the site's cookie context into this tab.
        await send("Page.navigate", {"url": f"https://www.{domain}/"})
        await asyncio.sleep(4)

        rid = await send("Network.getCookies",
                         {"urls": [f"https://www.{domain}", f"https://{domain}"]})
        cookies = None
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=15)
            msg = json.loads(raw)
            if msg.get("id") == rid:
                cookies = msg.get("result", {}).get("cookies", [])
                break

        matched = [c for c in cookies if domain in c.get("domain", "")]
        out_obj = {"cookies": [
            {"name": c["name"], "value": c["value"], "domain": c["domain"],
             "path": c.get("path", "/"), "expires": c.get("expires", -1),
             "httpOnly": c.get("httpOnly", False), "secure": c.get("secure", True),
             "sameSite": c.get("sameSite", "None")}
            for c in matched
        ]}
        for c in out_obj["cookies"]:
            print(f"{c['name']:<22} httpOnly={str(c['httpOnly']):<5} len={len(c['value'])}")
        has = any(c["name"] == "li_at" for c in out_obj["cookies"])
        print("HAS_LI_AT:", has)
        with open(out, "w") as f:
            json.dump(out_obj, f, indent=2)
        print(f"WROTE {out} cookies={len(out_obj['cookies'])}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--domain", default="linkedin.com")
    ap.add_argument("--out", default="/tmp/li_cookies.json")
    a = ap.parse_args()
    asyncio.run(main(a.port, a.domain, a.out))
