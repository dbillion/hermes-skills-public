---
name: uv-cli-development
description: Package a Python script into a uv-installable Click CLI.
---

# uv-cli-development

Turn a monolithic Python script into an installable `uv` CLI (console script). Use this whenever the user wants a script "installed as a cli using uv", or asks to refactor a long script into a package.

## MANDATORY WORKFLOW (user rule — non-negotiable)

The user gave this explicitly and was frustrated by violations. Enforce it on EVERY coding task in this class:

1. **Write a plan, convert it to tasks, tick each task as completed.** Use the `todo` tool. Show the plan before building.
2. **Unit tests are mandatory.** Plan tests from the start. "Any software without unit test is a failure; if you can't test what you built, you have failed — don't claim success." Ship `tests/` with real assertions; run `pytest` and show green before claiming done.
3. **Modular files only.** Never leave a 400-line monolith that could be split. Break into single-responsibility modules (client/cache/forward/cli/score...). The user detests long unmodularized files.
4. **For refactoring/structure, load the `ponytail` skill and/or `code-refactoring` skill** (if available in the session) before restructuring.

Write the rules out explicitly; do not imply them.

## Technique: monolith → uv-installable CLI

1. **Scaffold a package dir** (flat layout): `mypkg/__init__.py` + one module per responsibility. Keep each module small.
2. **`pyproject.toml`** — use **setuptools**, not hatchling (see Pitfalls). Declare the console script:
   ```toml
   [build-system]
   requires = ["setuptools>=68"]
   build-backend = "setuptools.build_meta"
   [project]
   name = "mypkg"
   version = "0.1.0"
   requires-python = ">=3.10"
   dependencies = ["click>=8.0", "rich>=13.0", "python-dotenv>=1.0", ...]
   [project.scripts]
   mycli = "mypkg.cli:cli"
   [tool.setuptools.packages.find]
   include = ["mypkg*"]
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   ```
3. **`mypkg/cli.py`** — Click group; one command per action. Read config from `.env` via `load_dotenv(Path(".env"))` (explicit cwd, NOT `find_dotenv()`).
4. **`tests/test_offline.py`** — pure-logic unit tests (filename suggestion, scoring/verdict, cache dedup, ID parsing). No network/Telegram needed for these.
5. **Install as a real CLI:** `uv tool install .` (builds a wheel, exposes `mycli` on PATH at `~/.local/bin/`). NOT `uv pip install -e .` (does not reliably write the bin into `.venv/bin`).
6. **Verify:** `pytest -q` → green; `mycli --help` works; a read-only live command proves wiring.

## Pitfalls (see references/build-gotchas.md for transcripts)

- **hatchling builds empty wheels here.** `uv build` produced a wheel whose RECORD omitted all package `.py` files, so `uv tool install` installed the script + metadata but NO code (`ModuleNotFoundError`). Fix: switch build backend to **setuptools** (above). Verify with: `python -c "import zipfile,glob; z=zipfile.ZipFile(sorted(glob.glob('dist/*.whl'))[-1]); print([l for l in z.read('*/RECORD').decode().splitlines() if '.py' in l])"` — must list the modules.
- **`find_dotenv()` walks UP and wins a parent `.env`.** Running from the project dir, `find_dotenv()` returned `/home/deeone/.env` (a parent) instead of `./.env`, so project creds/channels were never loaded (`status` said "NO"). Fix: `load_dotenv(Path(".env"))` (cwd-relative, explicit).
- **`uv pip install -e .` does not expose the console script** into `.venv/bin` reliably; `python -m mypkg.cli` works but `mycli` is missing. Use `uv tool install .` for the real bin.
- **Telethon/MTProto:** a *bot* session (token) cannot call `iter_dialogs`/`list_chats` — bots can't list dialogs (fails at `list_chats`). Use a *user* session (`TelegramClient('name', api_id, api_hash)` with a logged-in user) for `tg chats`/scraping. The OCR-forwarder pattern (download → OCR-rename → re-upload) defeats protected-chat forward restrictions.

## Verification checklist

- [ ] `uv build --wheel --no-cache` → wheel contains all modules in RECORD
- [ ] `uv tool install . --no-cache` → `which mycli` resolves, `mycli --help` runs
- [ ] `pytest -q` → all passed (never claim done with 0 tests)
- [ ] Read-only live command executes against real data (e.g. `score` on a real DB)
