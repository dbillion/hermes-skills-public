# SpiderFoot v4.0.0 — Headless / Automated Integration (passive recon)

SpiderFoot is in `/home/deeone/spiderfoot` (v4.0.0). It does passive OSINT:
DNS/ARIN/certificate/subdomain enumeration for a target domain.

## CRITICAL: the working path is the web server + REST API, NOT the direct engine

- ❌ **Do NOT** call `sfscan.startSpiderFootScanner(...)` directly. It launches the
  scan, modules run (DNS resolves, ARIN fetches, 37 correlation rules execute), but
  **events are NOT persisted** to `tbl_scan_results` — you get 0 stored events even
  though the scan "completes". This is a framework quirk when the scanner runs
  detached from the web server. Do not burn time debugging it.
- ✅ **Do** run the web server (`sf.py`) and drive it via REST. This is the path that
  reliably persists events (verified: an `infios.com` scan stored 28 events; an
  `example.com` scan stored 246).

## Setup (uv venv — preferred for easy teardown)

```bash
cd /home/deeone/spiderfoot
uv venv .venv
uv pip install --python .venv/bin/python \
  adblockparser dnspython ExifRead "CherryPy>=18.8.0,<19" cherrypy-cors Mako \
  beautifulsoup4 netaddr==0.8.0 pysocks requests ipwhois ipaddr phonenumbers \
  "pygexf>=0.2.2,<0.3" PyPDF2 "python-whois>=0.7.3,<0.8" secure pyOpenSSL \
  python-docx python-pptx "networkx>=2.6.3,<2.7" cryptography publicsuffixlist \
  openpyxl pyyaml
# lxml needs a C compiler; skip it — passive modules don't require it.
```

Dependency pitfalls (all hit and resolved):
- **`netaddr`**: newest 1.3.0 removed `IPAddress.is_private` → **pin `netaddr==0.8.0`**.
- **`secure`**: required for the web server to start (`secure_headers.framework.cherrypy()`)
  but may be silently skipped by a bulk install. If `sf.py` dies at startup with
  `'Secure' object has no attribute 'framework'`, install it explicitly:
  `uv pip install --python .venv/bin/python "secure>=0.3.0,<0.4.0"`.
- Bind the server to `127.0.0.1` only — it ships with auth DISABLED (SpiderFoot warns).

## Start the server

```bash
cd /home/deeone/spiderfoot
.venv/bin/python sf.py -l 127.0.0.1:5001
```
Long-lived daemon. Stop it when not in use.

## REST client pattern (verified working)

Use `urllib` (stdlib) — no extra deps:

1. **Submit scan** — GET `/startscan?scanname=JobHunt-<domain>&scantarget=<domain>
   &modulelist=<csv>&typelist=&usecase=passive`. Returns **HTTP 303**; the scan id is in
   the `Location` header (`/scaninfo?id=XXXX`). Capture the header with a redirect
   handler that returns `None` (do NOT follow the redirect, or urllib returns the
   scaninfo page and the id parse becomes fragile).
   Passive module list:
   `sfp_dnsresolve,sfp_dnsneighbor,sfp_certspotter,sfp_arin,sfp_bingsearch,sfp_threatcrowd,sfp_sublist3r`
2. **Poll** `/scanlist` (JSON array of `[id, name, target, start, end, _, status, eventCount, {...}]`)
   until `status` is `FINISHED` or `ERROR`. A scan takes **1–3 minutes**; poll up to ~180s.
3. **Export** — GET `/scanexportjsonmulti?ids=<id>` → JSON list of event dicts with keys
   `event_type`, `data`, `module`, `source_data`. (Note: the key is `event_type`, NOT `type`.)

Minimal client skeleton:

```python
import json, re, urllib.request, urllib.parse

SF = "http://127.0.0.1:5001"
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a): return None
op = urllib.request.build_opener(_NoRedirect())

def start_scan(domain, modules):
    q = urllib.parse.urlencode({"scanname": f"JobHunt-{domain}", "scantarget": domain,
        "modulelist": modules, "typelist": "", "usecase": "passive"})
    with op.open(f"{SF}/startscan?{q}", timeout=20) as r:
        loc = r.headers.get("Location", "")
    return re.search(r"id=([A-F0-9]+)", loc).group(1)

def scan_status(sid):
    with urllib.request.urlopen(f"{SF}/scanlist", timeout=20) as r:
        rows = json.loads(r.read())
    m = next((s for s in rows if s[0] == sid), None)
    return m[6] if m else None

def export(sid):
    with urllib.request.urlopen(f"{SF}/scanexportjsonmulti?ids={sid}", timeout=20) as r:
        return json.loads(r.read())
```

## What NOT to use

- `sfcli.py` (the interactive client) is **buggy in this version**: `-e <file>` crashes
  with `'str' object has no attribute 'readline'`, and `-s/--auth` handling is broken.
  Prefer the REST API directly.
- The bare `sf.py -u passive` one-shot (no server) — relies on the non-persisting engine.

## Wiring into a job pipeline

`enrich_domain(domain)` should: validate domain (reject `/` or spaces), call the REST
client above, return `(status, summary)` where status ∈
`scanned / no_data / scan_timeout / scan_error / skipped`. Write the result to a
`ScanStatus` column rather than a hardcoded placeholder. Keep it safety-gated: only
scan domains the user owns or authorized (per the operator's no-target-individuals rule).
