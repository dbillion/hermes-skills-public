# mcp-cli scoped recipes (cron-friendly)

Companion to the SKILL.md "mcp-cli ITSELF hangs / times out" section.
All snippets verified live on this host (mcp-cli v0.3.0, agent-reach v1.5.0).

## 1. Scope config template

Save as e.g. `/home/deeone/.hermes/scripts/jobhunt-mcp-scope.json`. Only the
servers THIS step touches — never the full `~/.mcp_servers.json`.

```json
{
  "mcpServers": {
    "exa": {"type":"http","url":"https://mcp.exa.ai/mcp"},
    "ga4-manager": {"type":"stdio","command":"node","args":["/home/deeone/mcp_servers/ga4-manager/mcp/dist/index.js","/home/deeone/go/bin/ga4-manager"]},
    "linkedin": {"type":"http","url":"http://127.0.0.1:3000/mcp"}
  }
}
```

Run: `mcp-cli -c /home/deeone/.hermes/scripts/jobhunt-mcp-scope.json call exa web_search_exa '{"query":"Java AI backend engineer jobs Canada","numResults":8}'`

## 2. Real tool names discovered (scoped `grep "*"`)

- **exa**: `web_search_exa`, `web_fetch_exa`
- **ga4-manager**: `ga4_setup`, `ga4_report`, `ga4_cleanup`, `ga4_link`, `ga4_validate`, `gsc_sitemaps_list`, `gsc_sitemaps_submit`, `gsc_sitemaps_delete`, `gsc_sitemaps_get`, `gsc_inspect_url`, `gsc_analytics_run`, `gsc_monitor_urls`, `gsc_index_coverage`
- **linkedin**: `get_person_profile`, `search_people`, `connect_with_person`, `get_my_profile`, `get_company_profile`, `search_companies`, `get_job_details`, `search_jobs`, `get_saved_jobs`, `get_inbox`, `search_conversations`, `send_message`, `search_posts`, `get_sidebar_profiles`, `get_company_posts`, `get_company_employees`

## 3. LinkedIn `search_jobs` schema (verified — pydantic rejects wrong args)

Rejects `remote` / `limit`. Correct args:
```json
{"keywords":"Java backend engineer","location":"Remote","max_pages":1}
```
- `location` is a **STRING** (`"Remote"`), NOT a boolean.
- `max_pages` integer 1–10 (default 3).
- Returns `job_ids` → pass to `get_job_details` for full info.
- Other LinkedIn gotcha: `get_person_profile` takes `linkedin_username` (handle), NOT `linkedin_url`.

## 4. LinkedIn server reachability quirk

`curl http://127.0.0.1:3000/mcp` → **HTTP 406 is EXPECTED** (streamable-http
MCP endpoint). It proves the server is listening. A 406 does NOT mean search
will succeed — `search_jobs` can still **TIME OUT** when the cached session is
stale. Treat LinkedIn as best-effort; refresh with `linkedin-scraper-mcp --login`
when leads stop appearing.

## 5. Cron collector skeleton (best-effort + fallback)

Working example: `/home/deeone/.hermes/scripts/jobhunt-collect.sh`
- Exa primary (free, reliable, no auth).
- LinkedIn secondary wrapped in `timeout 50` with a grep guard on output for
  `validation error|timed out|expired|session` → fall back to an Exa-only note.
- `rm -rf` the tmp dir at the end.
- Cron `script:` field references the script by **FILENAME ONLY**
  (`jobhunt-collect.sh`), not an absolute path — absolute paths are rejected by
  the scheduler ("Script path must be relative to ~/.hermes/scripts/").
