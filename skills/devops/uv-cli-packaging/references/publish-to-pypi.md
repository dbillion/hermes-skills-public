# Publish a uv package to PyPI (tag-triggered)

Goal: make `<name>` installable anywhere via `uv tool install <name>` / `pip install <name>`, no repo clone.

## 0. Name availability (do first)
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/<name>/json
# 404 = free, 200 = taken. An unrelated name like nonebot-plugin-<name> does NOT block <name>.
```

## 1. Build sanity check (local, no token)
```bash
uv build
ls dist/                       # expect <name>-X.Y.Z-py3-none-any.whl + .tar.gz
```

## 2. Token -> GitHub repo secret (never in .env, never in repo)
```bash
printf '%s' '<PASTE_pypi-TOKEN>' | gh secret set PYPI_TOKEN --repo <owner>/<repo>
gh secret list --repo <owner>/<repo> | grep -i pypi    # value masked on success
```

## 3. Workflow (.github/workflows/publish.yml)
```yaml
name: Publish to PyPI
on:
  push:
    tags: ["v*"]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with: { python-version: "3.12" }
      - run: uv build
      - run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

## 4. Release
```bash
sed -i 's/version = "0.1.0"/version = "0.2.0"/' pyproject.toml
git add pyproject.toml && git commit -m "chore: bump version to 0.2.0"
git tag -a v0.2.0 -m "release 0.2.0"
git push origin v0.2.0
```

## 5. Verify publish actually landed
```bash
gh run watch <id> --repo <owner>/<repo>     # expect "Publish to PyPI ✓"
curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/<name>/json   # 200 = live
```

## Gotchas
- `uv publish` needs `UV_PUBLISH_TOKEN` (or `TWINE_USERNAME`+`TWINE_PASSWORD`).
- A tag that already exists won't re-trigger the workflow — use a NEW version+tag.
- `dist/` should be gitignored so stray wheels never get committed.
- First upload of a name CLAIMS it on PyPI for that account.
