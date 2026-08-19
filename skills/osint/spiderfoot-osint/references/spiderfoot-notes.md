# SpiderFoot — verified facts & integration notes

> Source: live code inspection during 2026-08-16 session. Some items verified,
> the full engine scan loop was NOT validated end-to-end (blocked on user
> approval of a bulk dependency install). Do not present the untested parts as a
> confirmed workflow.

## What is actually installed

- Repo: `/home/deeone/spiderfoot`
- Entry points:
  - `sf.py` — **engine + web server**. Imports `cherrypy` at module top (line 25),
    so it fails with `ModuleNotFoundError: No module named 'cherrypy'` even when
    you only want batch/`json` output. There is no cherrypy-free path.
  - `sfcli.py` — **REST client only**. Its help text says it connects to a
    SpiderFoot server (default `http://127.0.0.1:5001`). Code-confirmed:
    `requests.get/post` calls target `self.ownopts['cli.server_baseurl']`.
    The interactive commands `scan <target> -u passive`, `start`, `find`,
    `export` are sent to that server. If the server is not running, sfcli does
    nothing useful.
  - `sfscan.py` — `SpiderFootScanner` class (the actual scan worker). Library,
    no argparse. This is the hook for programmatic (server-less) integration.
  - `sfwebui.py` — the web UI front-end.

## Verified setup (working)

```bash
cd /home/deeone/spiderfoot
python3 -m venv venv                       # PEP 668 blocks system pip
./venv/bin/pip install cherrypy             # verified: cherrypy 18.10.0 imports
./venv/bin/pip install netaddr networkx dnspython requests
# lxml needs a C compiler -> `pip wheel` fails here. SKIP it.
# Passive modules (sfp_dnsresolve, sfp_dns, sfp_certspotter, sfp_whois, ...) do
# not require lxml, so passive recon works without it.
./venv/bin/python -c 'import spiderfoot, sflib; print("ENGINE OK")'
```

`requests` was already importable system-wide; `cherrypy` install into the venv
succeeded and imported cleanly.

## How a scan is intended to run (the server path)

1. Launch the server: `./venv/bin/python sf.py -l 127.0.0.1:5001` (background).
2. Drive it via the client: `./venv/bin/python sfcli.py` then at the prompt:
   `scan infios.com -u passive -n Infios-Outreach-Recon`
   (this is exactly the pattern in `~/.spiderfoot_history`, which shows a real
   completed `infios.com` passive scan exported via `export 4E5E4544`).
3. Pull results: `find 4E5E4544` / `export 4E5E4544` inside the client.

## Programmatic integration (preferred for cron/agent)

Instead of running the server, import the engine directly:

```python
import sys
sys.path.insert(0, "/home/deeone/spiderfoot")
from sfscan import SpiderFootScanner
from spiderfoot.db import SpiderFootDb
# Build a scan, run SpiderFootScanner in a process, then read
# SpiderFootDb(opts).scanResultEvent(scan_id, ...) for the events.
```

This is the pattern to wire into `jobhunt-board.py` so each company domain gets
a passive scan and the result lands in the `ScanStatus` column (which was
hardcoded to `"not scanned"`). No email is ever triggered by enrichment.

**Status:** the import path is verified; the full scan-loop + DB-read was NOT
run to completion in-session. Validate with one real passive scan on an
authorized domain before trusting it in the cron.

## Pitfalls (learned the hard way)

- **sfcli.py is not a scanner.** If you run it and get no output, the server
  isn't up. Don't assume `scan` is a local command.
- **`sf.py` needs cherrypy even for `-o json` batch.** No workaround; install it.
- **PEP 668**: `pip install` as the user fails with an external-management error.
  Use the venv. Never pass `--break-system-packages` casually.
- **`lxml` wheel build fails** (no compiler). Skip it; passive recon doesn't need it.
- **User policy**: SpiderFoot is for company-domain enrichment only, on domains
  the user owns/is authorized to test. Do not target individuals for personal
  email/social harvesting.
