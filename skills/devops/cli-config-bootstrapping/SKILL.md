---
name: cli-config-bootstrapping
description: CLI crashes on missing .env when run outside its repo dir.
---

# CLI Configuration Bootstrapping

A recurring failure class for Python CLIs: the tool loads config from `Path(".env")`
(CWD-relative) and then `raise SystemExit("Set X in your .env")` when creds are
missing. This breaks the moment the user runs the installed console script from
another directory, or on a different OS where the CWD isn't the repo root. The
symptom is a confusing "Set TELEGRAM_API_ID / DATABASE_URL / etc" error even
though the `.env` file is correct and right there in the project.

## When to use this skill
- A CLI raises SystemExit / prints "set X in your .env" despite a valid .env.
- The same command works from the repo root but fails from `~/` or `/tmp` or via
  an installed `pipx`/`uv tool install` console script.
- You are building or fixing a CLI that needs API keys / tokens at startup.

## The footgun (what NOT to do)
```python
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env"))   # ONLY looks in the current working directory
```
If the process CWD ≠ repo root, `Path(".env")` resolves to the wrong (or a
non-existent) path, `.env` is never loaded, env vars stay empty, and the
credential check fails.

## The robust fix
Resolve `.env` from several candidate locations, most specific first:

```python
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import os

def load_project_env() -> None:
    candidates = []
    try:
        pkg_root = Path(__file__).resolve().parent.parent   # .../pkg -> repo
        candidates += [pkg_root / ".env", pkg_root.parent / ".env",
                       pkg_root.parent.parent / ".env"]
    except Exception:
        pass
    candidates.append(Path.cwd() / ".env")
    loaded = False
    for c in candidates:
        if c.exists():
            load_dotenv(c, override=False)
            loaded = True
    if not loaded:
        load_dotenv(find_dotenv(usecwd=True, raise_error_if_not_found=False),
                    override=False)
    # Defensive strip of stray whitespace in credential vars.
    for k in ("API_ID", "API_HASH", "TOKEN"):
        if k in os.environ and os.environ[k] != os.environ[k].strip():
            os.environ[k] = os.environ[k].strip()
```

This makes the CLI work from ANY directory and ANY OS (no hardcoded
`/home/...` or `~/` assumptions for the env file).

## Interactive credential fallback (replace the hard crash)
Never `SystemExit` on missing creds. Prompt once, validate, persist to `.env`,
and never echo the secret back:

```python
import click
from rich.console import Console

def ensure_credentials():
    if get_api_id() and get_api_hash():
        return
    console = Console()
    console.print("[yellow]🔑 Credentials not found.[/yellow] "
                  "Get them free at https://my.telegram.org")
    if not get_api_id():
        while True:
            v = click.prompt("API_ID", default="", type=str).strip()
            if v.isdigit():
                os.environ["API_ID"] = v
                break
            console.print("[red]Enter a numeric id.[/red]")
    if not get_api_hash():
        os.environ["API_HASH"] = click.prompt("API_HASH", default="", type=str).strip()
    _persist_to_env("API_ID", os.environ["API_ID"])
    _persist_to_env("API_HASH", os.environ["API_HASH"])
```
`_persist_to_env` rewrites the repo `.env` (regex replace existing key, else
append) best-effort; it must never print the value.

## Verification recipe (proves the fix)
Reproduce the failure scenario WITHOUT the fix, then confirm the fix:

```bash
# 1. Strip inherited env vars + run from a FOREIGN dir (the bug's trigger):
cd /tmp
env -u TELEGRAM_API_ID -u TELEGRAM_API_HASH \
  /path/to/.venv/bin/python -m mypkg.cli status
# BEFORE fix: "Set TELEGRAM_API_ID ..."  AFTER fix: "api configured: yes"

# 2. Offline test that loads .env from foreign CWD (pytest):
def test_load_from_foreign_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("API_ID", raising=False)
    monkeypatch.setattr(cl, "load_project_env", lambda: None)  # pretend no .env
    assert cl.get_api_id() == 0                                # precondition
    # stub click.prompt -> ensure_credentials() must NOT raise SystemExit
```

## Worked example
See `references/tgforwarder-env-worked-example.md` for the real-world fix
(tgforwarder `tgf` CLI: CWD-relative `.env` crash + Telethon channel-peer matching
bug), including the exact `env -u` + `/tmp` reproduction and the regression tests.

## Pitfalls
- Don't `import click` at module top just for prompting if click is optional —
  import it inside `ensure_credentials()` so non-interactive/CI imports don't fail.
- `monkeypatch.setattr(module, "load_project_env", lambda: None)` is the clean way
  to force the "no creds anywhere" branch in tests; deleting env vars alone is not
  enough if the package `.env` still resolves and re-populates them at import.
- If a `status` command checks `os.environ` AFTER import-time `load_dotenv` already
  populated it, it will report "yes" even in your test — neutralize `load_project_env`
  before asserting the "no" branch.
- Persisting creds to `.env` is fine ONLY if `.env` is gitignored. Confirm before
  writing, and never write the value to logs/stdout.
