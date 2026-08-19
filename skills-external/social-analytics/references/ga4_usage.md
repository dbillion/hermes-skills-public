# GA4 Manager Usage

## Prerequisites (REQUIRED)
The CLI and the `ga4-manager` MCP server both need a Google Cloud service-account
credential file. Set this environment variable before running any `ga4` command:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/home/deeone/kings-sales-key.json
```

Service-account email (already provisioned):
`kings-sales-agent@future-abode-338616.iam.gserviceaccount.com`

> **CRITICAL — GSC permission gotcha (this is why it "didn't work before"):**
> Authenticating succeeds, but every live Search Console call returns
> `403 Forbidden: User does not have sufficient permission for site ...`.
> GSC access is granted PER PROPERTY and is NOT inherited from the GCP project.
> You must add the service account as a user on the Search Console property itself:
> 1. Go to https://search.google.com/search-console
> 2. Select the property (e.g. `sc-domain:kings-sales.com`)
> 3. Settings → Users and permissions → Add user
> 4. Email: `kings-sales-agent@future-abode-338616.iam.gserviceaccount.com`
> 5. Permission: Owner (Full also works)
> Until this is done, the tool installs and runs but cannot read any property data.

## Binary location
- Installed at `/home/deeone/go/bin/ga4-manager` (symlinked as `ga4`).
- `ga4` is on PATH in interactive zsh (`$HOME/go/bin` via `~/.zshrc`).
- If `ga4` is not found, run it by absolute path: `/home/deeone/go/bin/ga4-manager`.

## Commands

### GA4 (Analytics Admin)
- `ga4 setup  --config config.yaml` : Set up GA4 from a YAML definition.
- `ga4 report --config config.yaml` : Run and display quick analytics reports.
- `ga4 cleanup --config config.yaml` : Identify and remove unused events/dimensions.
- `ga4 validate --config config.yaml` : Validate a GA4 configuration file.

### Google Search Console (NOTE: there is NO `ga4 gsc list` command)
The real subcommands are:
- `ga4 gsc analytics run --site sc-domain:example.com --days 30`
  Query search performance: top queries, landing pages, CTR, avg position,
  with `--dimensions query,page,country,device` and
  `--format table|json|csv|markdown`.
- `ga4 gsc inspect --site sc-domain:example.com --url https://example.com/page`
  Inspect a URL's indexing status.
- `ga4 gsc sitemaps list   --site sc-domain:example.com`  (list)
  `ga4 gsc sitemaps submit --site sc-domain:example.com --url https://example.com/sitemap.xml`
  `ga4 gsc sitemaps get    --site sc-domain:example.com --url <url>`
  `ga4 gsc sitemaps delete --site sc-domain:example.com --url <url>`
- `ga4 gsc monitor --config configs/mysite.yaml` : Monitor URL indexing status.

Site URL forms:
- Domain property: `sc-domain:example.com` (covers all subdomains/protocols)
- URL prefix:      `https://example.com/` (exact match, must end with `/`)

## MCP Tools (ga4-manager server)
The `ga4-manager` MCP server exposes these tools:
1. `list_properties`        : Find GA4 property IDs.
2. `get_report`             : Run reports for specific dimensions/metrics.
3. `search_console_query`   : Query GSC data directly (maps to `ga4 gsc analytics`).
4. `gsc_sitemaps_*`         : List/submit/get/delete sitemaps.
5. `gsc_inspect_url`        : Inspect a URL's indexing status.
6. `gsc_analytics_run`      : Run search-analytics reports.
7. `gsc_monitor_urls`       : Monitor URL indexing status.
8. `gsc_index_coverage`     : Index coverage report.

## Quick verification
After adding the service account in Search Console, confirm with:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/home/deeone/kings-sales-key.json
ga4 gsc sitemaps list --site sc-domain:kings-sales.com
```
A successful response (not a 403) means the permission blocker is resolved.
