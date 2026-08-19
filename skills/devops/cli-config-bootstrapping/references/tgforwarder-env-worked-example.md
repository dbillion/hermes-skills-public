# Worked example: tgforwarder (`tgf`) credential crash

## Symptom
Running `tgf forward ...` from a directory other than the repo root printed:
```
Set TELEGRAM_API_ID and TELEGRAM_API_HASH in your .env (from my.telegram.org).
```
Yet `.env` in the repo had correct keys.

## Root cause
`tgforwarder/cli.py` and `client.py` did:
```python
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env"))   # CWD-relative -> only works if CWD == repo root
```
When invoked from elsewhere, `Path(".env")` pointed at the wrong dir, no env was
loaded, and `make_client()` hit `if not api_id or not api_hash: raise SystemExit(...)`.

Note: it "worked" inside the agent's own shell only because that shell *inherited*
TELEGRAM_API_ID/TELEGRAM_API_HASH as real env vars — masking the bug. Always
reproduce with `env -u` to strip inherited vars.

## Fix applied (commits on branch fix/channel-peer-dedup)
1. `client.load_project_env()` resolves `.env` from package/repo + parents, then
   CWD, then `find_dotenv` upward walk; strips whitespace defensively.
2. `client.ensure_credentials()` replaces the `SystemExit` with a `click.prompt`
   fallback (cross-platform), validates numeric API id, and persists to `.env`
   so it asks only once. Never prints the secret.
3. `cli.status` now guides the user toward the prompt instead of a dead-end "NO".

## Reproduction / verification
```bash
cd /tmp
env -u TELEGRAM_API_ID -u TELEGRAM_API_HASH -u TG_API_ID -u TG_API_HASH \
  /home/deeone/Documents/scraper/python-scraper/tgforwarder/.venv/bin/python \
  -m tgforwarder.cli status
# BEFORE fix: "Set TELEGRAM_API_ID..."   AFTER fix: "api configured: yes"
```
Regression test `test_load_project_env_finds_repo_dotenv_from_foreign_cwd` and
`test_ensure_credentials_prompts_when_missing` guard this.

## Telethon domain note (separate bug, same repo)
For a channel source, `fwd_from.saved_from_peer` is `PeerChannel`, NOT `PeerUser`.
Comparing it to `PeerUser(src.id)` is ALWAYS False, so dedup rebuild / final
verification / `dedupe` silently skipped every channel-sourced message. Fix:
match via `telethon.utils.get_peer(src_id)` (typed peer). See commit c49e9e7.
