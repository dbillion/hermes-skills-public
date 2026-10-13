# LinkedIn channel — verified enablement

LinkedIn has no zero-config path. It needs a running MCP server (`linkedin-scraper-mcp`).

## Install
```bash
pip install linkedin-scraper-mcp
# installs linkedin_scraper_mcp_shim (renamed-> mcp-server-linkedin) + deps
# binary lands in venv/bin: linkedin-scraper-mcp (forwards to mcp-server-linkedin)
```
Note: the PyPI package `linkedin-scraper-mcp` is now a shim; the real server is `mcp-server-linkedin` (v4.14.0). Both shim and real entry points exist.

## Launch (background HTTP server)
```bash
export PATH="/home/deeone/.venv/bin:$PATH"   # or use absolute venv bin path
linkedin-scraper-mcp --transport streamable-http --host 127.0.0.1 --port 3000 --log-level WARNING
```
- Run as a BACKGROUND process (do NOT use nohup/disown — the harness can't track those; use the background flag).
- A bare `curl http://127.0.0.1:3000/mcp` returns HTTP 406 — that is EXPECTED for an MCP streamable-http endpoint. It is NOT down.
- Server drives a headless browser that logs into LinkedIn. It needs a valid LinkedIn session (auto-imported from Chrome, or via `--login` / `--import-from-browser chrome`). If sessions expire, re-run with `--login` while Chrome has a live LinkedIn session.

## Register with mcporter (HOME config — see mcporter-config.md)
```bash
cd ~
mcporter config add linkedin http://127.0.0.1:3000/mcp
mcporter config list   # confirm 'linkedin' is present, no stray project config
```

## Verify
```bash
# doctor should now show linkedin status: ok
timeout 30 agent-reach doctor --json | grep -A4 '"linkedin"'

# real call (NOTE arg shape): use linkedin_username, NOT linkedin_url
mcporter call 'linkedin.get_person_profile(linkedin_username: "williamhgates")'
# other tools:
# linkedin.search_people(keyword: "AI engineer", limit: 10)
# linkedin.get_company_profile(linkedin_url: "https://linkedin.com/company/xxx")  # this one DOES take url
# linkedin.search_jobs(keyword: "software engineer", limit: 10)
```

## Pitfalls
- Argument shapes differ per tool: `get_person_profile` wants `linkedin_username` (handle); `get_company_profile` wants `linkedin_url`. Read pydantic errors — they name the correct field.
- Server must stay running or every `mcporter call linkedin.*` fails to connect. For persistence either (a) add a startup service, or (b) switch to stdio transport in mcporter so it auto-spawns per call (but stdio + headless browser per call is slower).
