# GitHub search via `gh` — verified patterns

## Field-name gotchas (gh 2.96.0)
`gh search repos --json` does NOT accept `stargazerCount`, `nameWithOwner`.
Use: `stargazersCount`, `name`, `owner`, `url`, `description`, `pushedAt`, `updatedAt`.

## Ranked search (relevancy + language + stars)
```
gh search repos "linkedin scraper" --language python --stars ">300" --sort stars --order desc \
  --limit 12 --json name,owner,url,description > out.json
# exact star counts: gh api repos/{owner}/{name}  (search --json lacks stargazerCount)
```

## Trending (no "downloads" on GitHub; stars-gained-today is the proxy)
Scrape https://github.com/trending HTML; parse `<article class="Box-row">`:
- repo slug: first `href="/owner/repo"` not a login/return_to
- stars today: regex `([\d,]+)\s+stars today`
- language: `<span itemprop="programmingLanguage">`

## Other surfaces
`gh search code` (usage), `gh search issues`/`prs` (solutions), `gh search users`.
