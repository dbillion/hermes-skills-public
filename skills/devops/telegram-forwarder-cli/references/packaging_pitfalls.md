# uv packaging pitfalls (verified fixes)

All seen live while building `tgforwarder` as a `uv tool install`-able CLI.

## 1. hatchling builds empty wheels

Symptom: `uv tool install .` installs `tgf` but it dies with
`ModuleNotFoundError: No module named 'tgforwarder'`. The tool venv has only
`tgforwarder-0.1.0.dist-info`, no `tgforwarder/` package dir.

Root cause: hatchling 1.31 wrote a wheel whose `RECORD` listed only
`bin/tgf` + dist-info — the package `.py` files were in the zip but NOT in
RECORD, so the installer skipped them. (Confirmed: `zipfile` showed cli.py at
6322 bytes, but `RECORD` had zero `.py` entries. Filter with `'py' in line`,
NOT `line.endswith('.py')` — RECORD lines end with `,sha256,size`.)

Fix: use **setuptools**, not hatchling.

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project.scripts]
tgf = "tgforwarder.cli:cli"

[tool.setuptools.packages.find]
include = ["tgforwarder*"]
```

Do NOT add `[tool.hatch.build.targets.wheel] packages` / `only-include` /
`[tool.hatch.build] sources` — those overrides were what confused hatchling's
RECORD generation. Flat layout (`tgforwarder/` next to `pyproject.toml`) with
auto-find is enough.

Verify after build:
```python
import zipfile, glob
w = sorted(glob.glob('dist/*.whl'))[-1]
z = zipfile.ZipFile(w)
rec = [l for l in z.read('tgforwarder-0.1.0.dist-info/RECORD').decode().splitlines() if '.py' in l]
print(len(rec), "py files in RECORD")   # must be > 0
```

## 2. find_dotenv() walks UP to a parent .env

Symptom: `tgf status` said "api configured: NO" even from the project dir, while
running the tool's python directly with `load_dotenv()` found the creds.

Root cause: `load_dotenv(find_dotenv())` from `/proj/tgforwarder` returned
`/home/deeone/.env` (a parent dir's `.env`), which lacked TELEGRAM_API_ID. The
project's `.env` was ignored.

Fix: load the cwd `.env` explicitly — do NOT use `find_dotenv()`:
```python
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(".env"), override=False)
```
The CLI must be run from the project dir (same constraint as tg-cli / tg-user).
Document this in the command help.

## 3. editable install doesn't expose the console script

`uv pip install -e .` records metadata but does not write `tgf` into `.venv/bin/`.
Use `uv tool install .` (builds a real wheel) to get the bin on PATH.

If a stale/broken wheel is cached from before a fix, the reinstall reuses it:
```
uv tool uninstall tgforwarder
uv tool install . --no-cache
```
Always re-verify: `which tgf` resolves and `tgf --help` runs — only then claim
"it's a uv CLI like tg-cli".

## 4. wheel cache masks the fix

`uv build` caches wheels by content hash; if you edit source but the filename
stays `tgforwarder-0.1.0-py3-none-any.whl`, a rebuild may reuse a cached bad
wheel. Safe habit: `rm -rf dist && uv build --wheel --no-cache`.

## 5. push-to-remote from this host hangs

`git push` to github.com stalls (pack upload) from this machine. Verified path:
`git bundle create repo.bundle HEAD`, then on an egress machine
`git fetch repo.bundle HEAD && git push origin HEAD`. Commit locally first;
never rely on a direct push here.
