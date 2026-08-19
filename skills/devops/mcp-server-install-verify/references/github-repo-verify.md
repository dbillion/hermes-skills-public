# Verify a GitHub repo exists BEFORE cloning

User-supplied repo slugs are frequently misspelled. This session hit two:
- `scottsttss/threejs-awesome-graphics` → real is `scottstts/Threejs-Awesome-Graphics-Agent-Skills`
  (username has double `t`; repo name has caps + `-Agent-Skills`)
- `raresence/nova3d` → real is `RareSense/Nova3D` (owner capitalization differs)

A blind `git clone` on a wrong slug wastes a round-trip and returns an unhelpful
"Repository not found". Verify first.

## Order of probes (cheap → informative)
1. **`git ls-remote --heads <url>`** — definitive existence check, no download.
   `remote: Repository not found.` ⇒ 404, stop and search.
2. **API user-repo lookup** (rate-limited but precise):
   `curl -s https://api.github.com/repos/<owner>/<repo>` → `full_name`, `description`,
   `stargazers_count`, `size` (KB), `language`, `topics`, `clone_url`, `pushed_at`.
   Empty/garbage response ⇒ likely rate-limited or wrong slug.
3. **API search as fallback** when the exact slug fails:
   - `https://api.github.com/users/<owner>/repos?per_page=100` → list that user's repos,
     match by name fragment.
   - `https://api.github.com/search/repositories?q=<fragment>` → global fuzzy match.
     e.g. `q=nova3d+user:raresence` then broaden to `q=nova3d+3d`.

## What to report after verification
- Correct `full_name` + `clone_url`
- `description`, `stars`, `language`, `size` (KB → MB), `topics`
- Whether it needs local GPU/VRAM/models (storage-constrained users care)
- Whether the backend is hosted/closed-source vs local (Nova3D generates server-side)

## Note on API rate limits
Unauthenticated GitHub API allows ~60 req/hr. If it returns `{}` or an empty
`items`, don't trust it as "doesn't exist" — fall back to `git ls-remote`
(which is unauthenticated and unlimited) before concluding 404.
