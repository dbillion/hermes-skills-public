# SpiderFoot 4.0.0 — Headless REST Driver (proven working path)

This is the corrected, verified way to run SpiderFoot for company OSINT in this environment.
The older skill text said `docker compose up -d` + `sfcli.py` — that is WRONG for v4.0.0.

## Why the old path fails on v4.0.0
- **No docker.** SpiderFoot is a source checkout at `/home/deeone/spiderfoot` (uv venv, Python 3.14).
- **`sfcli.py -e file` is buggy** — passes a path string where a file object is expected (`'str' has no attribute 'readline'`). Don't use the CLI.
- **Direct engine (`sfscan.startSpiderFootScanner`) does NOT persist events** to the SQLite DB in this
  version. Scans run (DNS resolves, ARIN queries, 37 correlation rules execute) but `tbl_scan_results`
  stays at 0 rows. Only the **web-server path** stores results.

## The working path: run the server, drive it via REST

### 1. Start the server (background / daemon)
```bash
cd /home/deeone/spiderfoot && ./.venv/bin/python sf.py -l 127.0.0.1:5001
```
- Binds to `127.0.0.1:5001`. No auth by default — local-only, but stop it when idle.
- Requires `secure` + `cherrypy` installed in the venv (pin `netaddr==0.8.0`; v1.3.0 removed `is_private`).

### 2. Submit a passive scan (capture the 303 Location, do NOT follow it)
```python
import urllib.request, urllib.parse, re

def submit(target, modules="sfp_dnsresolve,sfp_certspotter,sfp_arin"):
    q = urllib.parse.urlencode({
        "scanname": f"JobHunt-{target}", "scantarget": target,
        "modulelist": modules, "typelist": "", "usecase": "passive",
    })
    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = urllib.request.build_opener(_NoRedirect())
    with opener.open(f"http://127.0.0.1:5001/startscan?{q}", timeout=20) as r:
        loc = r.headers.get("Location", "")
    m = re.search(r"id=([A-F0-9]+)", loc)
    return m.group(1) if m else None
```
- The scan id is in the `Location` header (`?id=XXXXXXXX`). Reading the body after `urlopen` follows the
  303 redirect and loses the id — hence the `_NoRedirect` handler.

### 3. Poll until FINISHED
```python
import json, time
def wait(scan_id, timeout=180):
    for _ in range(timeout):
        time.sleep(1)
        rows = json.loads(urllib.request.urlopen("http://127.0.0.1:5001/scanlist", timeout=10).read())
        m = next((s for s in rows if s[0] == scan_id), None)
        if m and m[6] in ("FINISHED", "ERROR"):
            return m[6]
    return "TIMEOUT"
```

### 4. Export events
```python
def export(scan_id):
    raw = urllib.request.urlopen(f"http://127.0.0.1:5001/scanexportjsonmulti?ids={scan_id}", timeout=20).read()
    return json.loads(raw)   # list of {event_type, data, module, source_data, ...}
```
- Event key is `event_type` (NOT `type`). `data` holds the value.

## Wiring into jobhunt-board.py
`enrich_domain(domain)` in `/home/deeone/.hermes/scripts/jobhunt-board.py` calls
`/home/deeone/spiderfoot/run_scan.py <domain> <out.json>` (the REST client above) and reads:
```json
{"scanId": "...", "target": "...", "status": "FINISHED", "events": N, "sample": [{"type": "...", "data": "..."}]}
```
It writes the real `ScanStatus` column (no longer the hardcoded `"not scanned"`). Each scan is 1–3 min;
the board calls it per company domain.

## Known-good results
- `github.com` passive scan → 246 events stored.
- `infios.com` (original user scan) → 28 events stored.
- If `events: 0` from the direct engine: that's the persistence bug — use the server path.
