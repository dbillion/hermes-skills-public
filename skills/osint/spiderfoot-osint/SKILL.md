---
name: spiderfoot-osint
description: "Automate SpiderFoot v4 passive OSINT via its REST API."
version: "0.1.0"
author: "Hermes (autonomous curation)"
license: MIT
tags: [osint, reconnaissance, spiderfoot, enrichment]
metadata:
  hermes:
    tags: [osint, reconnaissance, spiderfoot]
    related_skills: [osint-toolkit]
---

# SpiderFoot OSINT

## When to Use
- User says "spiderfoot", "sf.py", "sfcli.py", or wants OSINT recon / passive
  company-domain enrichment.
- Wiring SpiderFoot into a cron/agent pipeline (e.g. job-board domain enrichment).
- Debugging "scan command does nothing" — almost always the server isn't up.

SpiderFoot is a multi-source OSINT automation engine. Its CLI layout is **not
intuitive** and trips up first-time integrators — this skill records the facts a
future session needs, verified by live code inspection (2026-08-16).

## Critical architecture (read first)

- **Two binaries, one job.**
  - `sf.py` — the **engine + web server** (default port 5001). It imports
    `cherrypy` at the **top of the file**, so it crashes *even in batch mode*
    without it. There is **no cherrypy-free batch path**.
  - `sfcli.py` — a **thin REST client only**. Its help text says it connects to a
    SpiderFoot server (default `http://127.0.0.1:5001`). The interactive commands
    `scan`, `start`, `find`, `export` are sent to that server over HTTP. If the
    server is not running, sfcli does nothing useful. **Also buggy in v4**:
    `-e <file>` crashes (`'str' object has no attribute 'readline'`) and `-s/--auth`
    is broken — prefer the REST API directly, not sfcli.
  - `sfscan.py` — `SpiderFootScanner` class (the actual scan worker; library, no
    argparse).
  - `sfwebui.py` — the web front-end.

- **The `scan infios.com -u passive` commands work ONLY because the server is up.**
  That's why the historical `~/.spiderfoot_history` shows completed scans — the
  server was running in that session.

## THE WORKING PATH (verified 2026-08-16, end-to-end)

**Run `sf.py` as a server and drive it via REST. Do NOT call the scan engine directly.**

- ❌ `sfscan.startSpiderFootScanner(...)` runs modules but **persists 0 events** to
  `tbl_scan_results` — the scan "completes" empty. Framework quirk when the scanner
  is detached from the web server. Confirmed twice this session; do not debug it.
- ✅ `sf.py -l 127.0.0.1:5001` + REST reliably persists events. Verified live:
  `infios.com` → 28 events, `example.com` → 246 events, `enrich_domain()` called
  from a job-board script returned `scanned | 1 events`.

REST recipe (stdlib `urllib`, no extra deps):
1. Submit: `GET /startscan?scanname=JobHunt-<dom>&scantarget=<dom>&modulelist=<csv>&typelist=&usecase=passive` → **HTTP 303**; scan id is in the `Location` header. Capture it with a redirect handler that returns `None` (don't follow the redirect). Passive modules: `sfp_dnsresolve,sfp_dnsneighbor,sfp_certspotter,sfp_arin,sfp_bingsearch,sfp_threatcrowd,sfp_sublist3r`
2. Poll `/scanlist` (JSON: `[id,name,target,start,end,_,status,eventCount,{...}]`) until `status` ∈ {`FINISHED`,`ERROR`}. A scan takes **1–3 min**; poll ≤ ~180s.
3. Export `GET /scanexportjsonmulti?ids=<id>` → list of `{event_type, data, module, source_data}`. ⚠️ Key is **`event_type`**, NOT `type`.

See `references/spiderfoot-v4-rest.md` for a copy-paste client skeleton + the exact
failure transcripts, and `references/spiderfoot-notes.md` for transcript-level detail.

## Verified setup (working)

```bash
cd /home/deeone/spiderfoot
python3 -m venv venv                       # PEP 668 blocks system pip
./venv/bin/pip install cherrypy             # verified: cherrypy 18.10.0 imports
./venv/bin/pip install netaddr networkx dnspython requests
# lxml needs a C compiler -> `pip wheel` FAILS. SKIP it.
# Passive modules (DNS/cert/whois/...) do not require lxml, so passive recon works.
./venv/bin/python -c 'import spiderfoot, sflib; print("ENGINE OK")'
```

`requests` was importable system-wide; the cherrypy venv install succeeded.

## Pitfalls (learned the hard way)

- **sfcli.py is not a scanner.** No output ⇒ the server isn't up. Don't assume
  `scan` is a local command.
- **`sf.py` needs cherrypy even for `-o json` batch.** No workaround; install it.
- **PEP 668**: `pip install` as the user fails with an external-management error.
  Use the venv. Never casually pass `--break-system-packages`.
- **`lxml` wheel build fails** (no compiler). Skip it; passive recon doesn't need it.
- **User policy**: SpiderFoot is for **company-domain enrichment only**, on domains
  the user owns or is authorized to test. Do **not** target individuals for
  personal email/social harvesting.

## Integration pattern (preferred for cron/agent)

Import the engine directly instead of running the server:

```python
import sys
sys.path.insert(0, "/home/deeone/spiderfoot")
from sfscan import SpiderFootScanner
from spiderfoot.db import SpiderFootDb
# Build a scan, run SpiderFootScanner in a process, then read
# SpiderFootDb(opts).scanResultEvent(scan_id, ...) for the events.
```

Wire this into a job-board script so each company domain gets a passive scan and
the result lands in a `ScanStatus` column (which is otherwise hardcoded to
`"not scanned"`). **No email is ever triggered by enrichment.**

See `references/spiderfoot-notes.md` for full transcript-level detail and the
server-path walkthrough.

## Validation status

- Verified: venv creation, cherrypy/requests/netaddr install, `import spiderfoot,
  sflib` succeeding, sfcli.py being a pure REST client (code-confirmed).
- NOT yet validated end-to-end: the full engine scan loop + DB read inside the
  cron. Validate with one real passive scan on an authorized domain before
  trusting it in automation.
