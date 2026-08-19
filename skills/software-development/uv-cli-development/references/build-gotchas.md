# build-gotchas.md — uv packaging failures seen in the tgforwarder session

## 1. hatchling produces a wheel with an EMPTY RECORD (package code not installed)

Symptom: `uv build --wheel` succeeds, wheel *contains* the `.py` files (visible via
`zipfile.ZipFile(w).namelist()`), but `uv tool install .` installs only `bin/mycli` +
`*.dist-info` — running `mycli` gives `ModuleNotFoundError: No module named 'mypkg'`.
Root cause: the wheel's `RECORD` listed only the script + dist-info, omitting the package
modules, so the installer skipped them.

Verification that caught it:
```python
import zipfile, glob
w = sorted(glob.glob('dist/*.whl'))[-1]
z = zipfile.ZipFile(w)
rec = [l for l in z.read('mypkg-0.1.0.dist-info/RECORD').decode().splitlines() if '.py' in l]
print(len(rec))   # 0 = broken, should be 6 (one per module)
```
NOTE: filtering with `l.endswith('.py')` is WRONG — RECORD lines are
`path,sha256:...,size` and end with the size. Use `'.py' in l`.

Fix: switch build backend to setuptools in pyproject.toml:
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
[tool.setuptools.packages.find]
include = ["mypkg*"]
```
After switching, the RECORD correctly lists all modules and `uv tool install` works.

## 2. find_dotenv() walks UP and loads a PARENT .env

Symptom: run `mycli status` from the project dir; it reports config missing even though
`./env` exists with the creds. `find_dotenv()` returned `/home/deeone/.env` (a parent
directory) instead of `./.env`, so the project's values were never loaded.

Debug that exposed it (temporary print in cli.py):
```
[debug] cwd=/home/deeone/.../mypkg dotenv='/home/deeone/.env'
```
Fix: load the cwd-relative file explicitly (do NOT use find_dotenv):
```python
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(".env"), override=False)
```

## 3. uv pip install -e . vs uv tool install .

- `uv pip install -e .` (into a project `.venv`) recorded the package but did NOT write
  `mycli` into `.venv/bin`; `python -m mypkg.cli` worked, `mycli` did not.
- `uv tool install .` builds a real wheel and installs `mycli` to `~/.local/bin/` on PATH.
  This is the tg-cli-equivalent path. Use `--no-cache` and `--force` when re-installing
  after a build fix, otherwise a stale cached wheel is reused.

## 4. Telethon/MTProto session gotchas

- A *bot* session (created with a bot token) cannot call `iter_dialogs` / `list_chats`
  (bots can't list dialogs → fails at `list_chats`). For `tg chats` / scraping, use a
  *user* session: `TelegramClient('name', api_id, api_hash)` with a logged-in user.
- The OCR-forwarder pattern: download media → OCR-rename file → re-upload with
  `send_file(force_document=True)` defeats "protected chat can't forward" restrictions.
- A running sync (`tg-user sync-all`) holds the session .session file lock
  (`database is locked`); don't run `send` while sync/listen is active on the same session.
