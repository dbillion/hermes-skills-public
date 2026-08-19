---
name: uv-cli-packaging
description: Package a Python CLI as a `uv tool install .` binary.
---

# uv-cli-packaging

Make a Python package installable as a global CLI (`<bin>` on PATH) via `uv tool install .` — the same mechanism as `tg-cli`. This skill captures the non-obvious failures that occur when doing this the "normal" way and the exact fixes.

## When to use
- You want a Python project installable as a CLI binary via uv, not just `pip install -e .`.
- You hit: wheel installs but `import` fails (`ModuleNotFoundError`); or the installed binary can't find `.env`; or `git push` to GitHub hangs/freezes.

## Packaging steps (setuptools — reliable)
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "tgforwarder"
version = "0.1.0"
dependencies = ["click>=8.0", "rich>=13.0", ...]

[project.scripts]
tgf = "tgforwarder.cli:cli"

[tool.setuptools.packages.find]
include = ["tgforwarder*"]
```
Build + install:
```bash
uv build --wheel --no-cache
uv tool uninstall <name>      # clear any stale tool venv first
uv tool install . --no-cache
```
Verify: `which <bin>` and `<bin> --help`.

## Pitfalls (learned the hard way — embed these)
- **Hatchling emits wheels with an INCOMPLETE RECORD.** The package `.py` modules land in the archive but are omitted from `RECORD`, so `uv tool install` extracts only the script + dist-info → `ModuleNotFoundError` at runtime. **Fix: use the setuptools backend** (above). Verify the wheel is correct:
  ```python
  import zipfile, glob
  z = zipfile.ZipFile(sorted(glob.glob('dist/*.whl'))[-1])
  rec = [l for l in z.read('pkg-0.1.0.dist-info/RECORD').decode().splitlines() if '.py' in l]
  print(len(rec))   # must list your modules, not 0
  ```
  NOTE: RECORD lines end with `,sha256:...,<size>` — filter on `'.py' in l`, NOT `.endswith('.py')`.
- **`uv pip install -e .` does NOT expose the console script** (uv quirk). It installs the package but the `bin/` shim never hits PATH. Always use `uv tool install .` for a real CLI.
- **`find_dotenv()` walks UP to a parent `.env`.** If `/home/user/.env` exists, `load_dotenv(find_dotenv())` loads THAT, not your project's. Fix: `load_dotenv(Path(".env"))` (cwd-relative). Then the binary must be run from the project dir (same as tg-cli expects its config in cwd). Symptom: `python -m pkg.cli status` says "configured: yes" but the installed `<bin> status` says "NO" — cwd/dotenv resolution differs. Debug by reproducing the exact binary invocation: `/path/to/tool-venv/bin/python -m pkg.cli <args>` from the same dir.
- **Installed `uv tool` binary can't find `.env` when run from ANY other directory** (the real-world case: the user runs `<bin>` from `~/Projects/Other`, not the repo). CWD-relative loading fails silently and the tool re-prompts or hard-fails. **Durable fix:** make the env loader ALSO check a fixed home-config path + `$HOME/.env`, last-resort after the package dirs:
  ```python
  candidates = []
  pkg_root = Path(__file__).resolve().parent.parent
  candidates += [pkg_root/".env", pkg_root.parent/".env", pkg_root.parent.parent/".env"]
  candidates.append(Path.home()/".config"/"<pkg>"/".env")   # works from ANY cwd
  candidates.append(Path.home()/".env")
  candidates.append(Path.cwd()/".env")
  for c in candidates:
      if c.exists(): load_dotenv(c, override=False)
  ```
  Then seed creds ONCE into `~/.config/<pkg>/.env` (gitignored, outside the repo) so the installed binary works globally without re-prompting. NEVER write secrets into the repo `.env`. Verify from a foreign dir: `cd /tmp && <bin> status` should report configured: yes.
- **Upgrade an already-installed tool after a fix:** `uv tool install .` says "already installed" and does NOT upgrade. Use `uv tool upgrade <name>` (pulls latest PyPI) or `uv tool install --force .` (rebuild from local repo — picks up un-released fixes instantly, no PyPI round-trip). Check the installed version: `uv tool list` (shows version + bin name). NOTE: the runnable command is the `project.scripts` name (e.g. `tgf`), NOT the package name (`tgforwarder`). Running `tgforwarder` as a command yields "command not found" — tell the user to run `tgf`, not `tgforwarder`.
- **`git push` WORKS from this host via `gh`** (authed as dbillion, `repo`+`workflow` scopes). The previously-held "git push hangs → use git bundle" assumption was STALE/WRONG — the user pushed successfully and corrected it. Preferred create+push: `gh repo create <name> --public --push --source .`. ONLY do **non-destructive** git: no force push, no commit deletion, no `reset`/reflog tricks, no `wipe`. User explicitly forbade destructive GitHub actions. If a direct `git push` ever does stall, the `git bundle` escape hatch still works — but don't *assume* it stalls.
  ```bash
  git bundle create repo.bundle HEAD
  # on egress: git clone <repo> && git fetch repo.bundle HEAD && git push origin HEAD
  ```
  Never put secrets in the bundle — `.env` MUST be gitignored (verify with `git status --short | grep .env`).
- **Distribute the tool without a clone (3 one-liners)** — from pydevtools + dev.to npx-skills:
  ```bash
  uv tool install "git+https://github.com/<owner>/<repo>.git@v0.1.0"   # pinned to TAG (reproducible)
  uvx --from "git+https://github.com/<owner>/<repo>.git@v0.1.0" <bin> --help   # run WITHOUT installing (CI/one-off)
  npx skills --skill <owner>/<repo>/<skill-name>   # install a SKILL.md from the repo (no npm publish)
  ```
  Pin by **tag or SHA**, not branch (branches drift). `npx skills` reads `skills/<name>/SKILL.md` from the repo and installs into the agent — the cleanest "npx skill to install for agent use". Keep an `installer/package.json` + `bin` shim as an alt `npx -y <pkg>` wrapper if you want.
- **DOCUMENTATION SAFETY — never expose real IDs in docs.** User explicitly flagged real Telegram channel/user IDs committed to README/docs as "not needed or necessary". Use PLACEHOLDERS (`-1000000000000`, `<SOURCE_CHANNEL>`, `<YOUR_USER_ID>`) in all committed docs; keep real IDs only in the local, gitignored `.env`.
- **Verify with a LIVE command, not just `--help` — and re-read the actual result.** `--help` only proves import works. For forwarding/messaging tools, a log line saying "forwarded: N" can be a CACHED/phantom count if a broad `except` swallowed a real error. Verify by re-reading the returned object from the destination (e.g. `get_messages(dest, ids=returned_id)` and confirm it actually arrived + correct attribution). Run the real command once (even `--limit 1`) to confirm `.env` loads and the entry point does work AND the delivery is real.

## Publish to PyPI (so `uv tool install <name>` works from anywhere, no clone needed)
`uv tool install .` only works on machines that have the repo. To make the package installable globally WITHOUT a clone, publish to PyPI via a **tag-triggered GitHub Action** — the token never touches the repo or an agent's context.

**1. Check the name is free BEFORE publishing** (HTTP 404 = available, 200 = taken):
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/<name>/json
# NOTE: an unrelated name like 'nonebot-plugin-<name>' does NOT block '<name>' — check the EXACT name.
```

**2. Bump `version` in `pyproject.toml`, commit, tag** (the tag is what triggers publish):
```bash
sed -i 's/version = "0.1.0"/version = "0.2.0"/' pyproject.toml
git add pyproject.toml && git commit -m "chore: bump version to 0.2.0"
git tag -a v0.2.0 -m "release 0.2.0"
git push origin v0.2.0      # triggers the publish workflow
```

**3. Store the PyPI token as a GitHub repo secret (NOT in .env, NOT committed).** The token (`pypi-...`) is itself a secret; never paste it into files. Set it via `gh` reading from stdin (avoids argv/shell-history leakage):
```bash
printf '%s' '<PASTE_TOKEN_HERE>' | gh secret set PYPI_TOKEN --repo <owner>/<repo>
gh secret list --repo <owner>/<repo> | grep -i pypi   # verify, value masked
```
The workflow reads `secrets.PYPI_TOKEN` at runtime.

**4. `.github/workflows/publish.yml` (tag-triggered):**
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
        env: { UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }} }
```
`uv publish` picks up `UV_PUBLISH_TOKEN` (or `TWINE_USERNAME`/`TWINE_PASSWORD`). After push: `gh run watch <id> --repo <owner>/<repo>` → confirm `curl pypi.org/pypi/<name>/json` returns HTTP 200.

**5. Future releases:** bump version → commit → `git tag -a vX.Y.Z` → `git push origin vX.Y.Z`. No re-handling of the token.

## User demand: no monoliths (source OR tests)
The user repeatedly rejected god files during this work. Encode as a hard rule for any package task:
- Source: one concern per module; if a file > ~225 lines OR a single function > ~200 lines with parallel pipelines, SPLIT (e.g. pull a duplicate pipeline into its own module).
- Tests: NEVER leave a single `test_*.py` god file covering many modules. Mirror the source layout — `test_forward.py`, `test_cache.py`, `test_state.py` — one file per module (localizes failures).
- When refactoring a monolith, ADD a unit/integration test for each extracted module (e.g. a stubbed-client integration test that drives the real command body) so coverage is not lost.

## Verification checklist
- [ ] `uv build --wheel`, then inspect RECORD contains package modules
- [ ] `uv tool install . --no-cache`; `which <bin>` resolves
- [ ] `<bin> --help` runs (proves import works)
- [ ] Run `<bin>` FROM the project dir; confirm `.env` loads (status/config reads creds)
- [ ] Live smoke test of the real command (not just --help)

## references/
- `references/telegram-kreuzberg-forwarder.md` — Telegram/MTProto (telethon) forwarder patterns + Kreuzberg (Rust OCR via Python API) technique.
- `references/publish-to-pypi.md` — full PyPI publish recipe: name check, token-as-GitHub-secret, tag-triggered workflow, verification.
