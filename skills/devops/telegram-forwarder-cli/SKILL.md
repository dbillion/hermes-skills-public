---
name: telegram-forwarder-cli
description: Build a Telegram MTProto forwarder/scraper CLI with uv.
license: MIT
---

# Telegram Forwarder / Scraper CLI (Telethon + uv)

Build a Telegram MTProto client as an installable CLI. MTProto = user-client
protocol (Telethon). Bots (Bot API / teloxide) CANNOT list dialogs or read
private chats — only a *user* session can. This skill is for the user-client case.

## Hard coding mandate (this user — non-negotiable)

Embedded from an explicit correction ("as a rule going forward…"):
1. **Write a plan, turn it into a task list, tick each task as done.**
2. **Unit tests are MANDATORY.** "Any software without unit test is a failure;
   if you can't test what you just built, you have failed." Ship `tests/test_*.py`
   covering offline logic (filename helpers, scoring/verdict, state persistence,
   cache dedup) BEFORE claiming success.
3. **Modular, never a ~400-line monolith.** Split into single-responsibility
   files: `client.py` (session+resolve), `cache.py` (SQLite), `forward.py`
   (OCR), `score.py` (usefulness), `report.py` (logging), `state.py` (resume),
   `cli.py` (Click commands).
4. Load `ponytail` / `code-refactoring` for structure work. (Note: `ponytail`
   is user-owned here — recommend `hermes curator adopt ponytail` to edit it.)

## Modular layout (reference shape)

```
tgforwarder/
  pyproject.toml        # setuptools backend, [project.scripts] tgf = ...
  tgforwarder/
    __init__.py
    client.py           # make_client(), resolve_entity() (handles -100 prefix)
    cache.py            # ForwardCache: SQLite dedup (UNIQUE src,src_msg,tgt)
    forward.py          # extract_text() per extension; OCR-rename
    score.py            # score_chats(): recency/diversity/topic/noise verdict
    report.py           # ForwardLogger: count, by-type, 5-min window, rich+emoji
    state.py            # resume persistence: last_message_id per source
    cli.py              # Click group: forward / score / test-ocr / status
  tests/test_offline.py # offline: filename, score verdict, cache dedup, state, logger
```

## uv packaging — CRITICAL pitfalls (seen live, cost real time)

See `references/packaging_pitfalls.md` for full detail + verification snippets.
Summary:
- **hatchling builds empty wheels** (RECORD omits package code) → use **setuptools**.
- **`find_dotenv()` walks UP** to a parent `.env` → load `Path(".env")` (cwd) explicitly.
- **editable install doesn't expose the bin** → `uv tool install .` (real wheel);
  reinstall clean with `--no-cache` if a stale broken wheel is cached.
- Never claim "it's a uv CLI" until `which tgf` resolves and `tgf --help` runs.

## Telegram session patterns

- **User vs bot:** `tg chats` fails on a bot session (bots can't list dialogs).
  A real *user* `.session` (e.g. `forwarder_session1.session`) works.
- **Reuse an existing user session:** copy it to the client's `DATA_DIR`
  (`~/.local/share/tg-cli/<name>.session`) so `resolve_entity` finds it.
- **Login once, interactively:** Telethon `start()` needs a TTY for the phone
  code; an agent can't run it. Provide a helper that writes the session, then the
  user runs it in a real terminal. Keep creds in a local `.env` (gitignored),
  never in chat.
- **One session at a time:** "database is locked" means another process holds the
  `.session` (e.g. a `sync-all` running). Don't run `send` while sync is active.

## Chat usefulness scoring (research triage)

Rank chats from a local SQLite cache (`tg-cli` `messages.db`) so scoring is
offline. Metrics: recency (age decay), sender diversity, topic relevance
(`--topic` boosts; <15% relevant -> cap as NOISE), link density, noise denylist
(prayer/telecom/leech/forex). Verdict: USEFUL >=55, OK >=35, else NOISE. Pure
SQLite, no Telegram — the "which chat is useful vs not" research tool.

## Commands shape (Click)

- `tgf forward --source X --dest Y --path ./downloads [--resume|--start]`
  reads `SOURCE_CHANNELS`/`DEST_CHANNELS`/`FORWARD_PATH` from `.env` as defaults;
  launches an interactive menu when run with no args (source/dest/path/mode).
- `tgf score --db messages.db --topic "java,rust,devops" --top 20 [--json]`
- `tgf test-ocr --source ID` (read-only: download+OCR+delete, sends nothing)
- `tgf status` (shows api configured, never prints secrets)

## Verify before claiming done

1. `uv build --wheel --no-cache` -> wheel contains all `.py` modules.
2. `pytest -q` -> green (offline tests).
3. `uv tool install . --no-cache` -> `which tgf` resolves, `tgf --help` runs.
4. Live smoke: `tgf test-ocr` (read-only) connects + resolves + OCR. Only then
   run a real `forward` (it's a write — confirm source/target with user).
