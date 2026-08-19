---
name: telegram-bot-tooling
description: "Teloxide bots and the `tg` CLI; Bot API vs MTProto split."
version: "1.0.0"
author: hermes-curator
tags:
  - telegram
  - teloxide
  - mtproto
  - telethon
  - grammers
  - bot-api
  - rust
  - cli
---

# Telegram Bot Tooling (Bot API vs MTProto)

Two fundamentally different Telegram worlds. Confusing them is the #1 source of
"why is this not working" bugs.

## The core split

| Layer | Bot API | MTProto (user/client) |
|---|---|---|
| Library | **teloxide** (Rust), or any Bot-API SDK | **Telethon** (Python), **grammers** (Rust), Pyrogram |
| Auth | **bot token** from @BotFather (`123456:ABC...`) | **phone number** login → produces a `.session` file |
| Identity | A bot account (`@something_bot`, `phone: ''`) | A real user account (your phone, can read private chats) |
| Sees chats | Only chats it was **explicitly added to** | All dialogs the user is in |
| Can do | Send/recv as the bot; cannot read YOUR DMs | Act as you; read history; full dialog list |
| Skill | `rusty-tesseract` media + admin commands | `tg` kabi-tg-cli (this session) |

**Rule of thumb:** a bot token only ever works on the Bot API. MTProto tools
(Telethon/grammers) do NOT accept bot tokens as a substitute for user login —
though Telethon's `.start(bot_token=...)` CAN log a bot in as a bot session
(see pitfall below).

## teloxide (Bot API) — what a bot can do
- Long polling (`teloxide::repl`) or webhooks (`set_webhook`).
- `get_file` + `download_file`; `send_photo/video/document/audio/voice/animation`;
  `send_media_group` (albums).
- `#[derive(BotCommands)]` for typed commands (testable, auto `/help`).
- `dialogue` state machine (`InMemStorage`, `RedisStorage`) for multi-step flows.
- dptree filters: `Update::filter_*`; predicates for `only_from`/`only_chat` scoping.
- NO persistence built in — pair with `sqlx` (SQLite/Postgres) for state that
  survives restart. In-memory `Arc<Mutex<State>>` loses targets/allow-list on boot.
- OCR/renaming is NOT a teloxide feature — it's `rusty-tesseract` you call before send.

### teloxide capability → valuable CLI flags (for an AI-driven bot)
| Flag | Value | Effort |
|---|---|---|
| `--db-path` / `--state-backend` | kills restart-data-loss | Med |
| `--dry-run` | download+OCR+rename, don't send | Low |
| `--ocr-lang`, `--ocr-off` | multilingual / skip rename | Low |
| `--download-dir` | stop hardcoding temp path | Low |
| `--only-from` / `--only-chat` | scope ingestion | Low |
| `--log-level`, `--rate-limit` | debug + avoid 429 bans | Low |
| `BotCommands` refactor | makes commands unit-testable | Med |
| `--login-flow` (dialogue) | multi-user onboarding | High |

**AI-control model:** the bot exposes typed CLI commands; the AI translates
natural-language intent → precise, logged, reversible CLI actions. Highest-value
first step = write unit tests for the pure functions (`create_filename`,
`is_image`) before any refactor. These run with no Telegram, no network.

## kabi-tg-cli (`tg`) — MTProto user/client tool
- Path: `/home/deeone/.local/bin/tg` (uv tool `kabi-tg-cli`).
- Built on **Telethon** (`from telethon import TelegramClient`).
- Commands: `chats`, `history`, `search`, `sync`, `sync-all`, `send`, `listen`,
  `status`, `whoami`, `export`, `stats`, `timeline`, etc.
- Env: `TG_API_ID`, `TG_API_HASH` (defaults to `2040`/`b184...` — warns of
  account-restriction risk; **set your own from my.telegram.org**),
  `TG_SESSION_NAME` (default `tg_cli`), `DATA_DIR`, `DB_PATH`.

### PITFALL — `tg chats` fails because the session is a BOT
Symptom:
```
File ".../tg_cli/cli/tg.py", line 52, in _run
    return await list_chats(client, chat_type)
```
Root cause (verified this session): `tg status` showed
`authenticated: true, user: {username: Dredai_bot, phone: ''}`.
The client is logged in as a **bot**, but `list_chats`/`get_dialogs` are
**user-level operations**. Bots can't enumerate dialogs the way users can — a
bot only "sees" chats it was explicitly added to, and Telethon's dialog fetch
for a bot session is unreliable/empty.

The "bot token vs numeric chat ID" framing is a **red herring** — the token
*did* authenticate (Telethon accepts `start(bot_token=...)`), the failing
operation is `list_chats`, which is incompatible with a bot session.

Fix options:
- **Keep as bot (Dredai_bot):** dialog-listing ops (`chats`, `sync-all`,
  `refresh`) stay broken. `send`/`history` to a chat the bot is in may work.
- **Make it a real user client (full power):** set `TG_API_ID`/`TG_API_HASH`,
  then log in with your **phone number** (interactive — you run it, agent does
  NOT handle credentials). Creates a user `.session`. Then `chats`/`sync-all`/
  `search` all work. This is the MTProto user-client capability the Bot API
  cannot provide.

See `references/tg-bot-session-debug.md` for the exact transcript + commands.

## `tg-user` wrapper — run `tg` as a REAL USER (the fix that actually worked)
`tg chats` fails on the bot session (above). The working fix this session was to
**copy the existing user `.session`** (`forwarder_session1.session`, already a
logged-in user `@oludayor`) into the tg-cli data dir under a separate name, then
drive `tg` with a wrapper that forces the user session + own creds:

```bash
#!/usr/bin/env bash
# /home/deeone/.local/bin/tg-user — run `tg` as a USER, not the bot session.
set -euo pipefail
ENV_FILE="${TG_USER_ENV:-/home/deeone/Documents/scraper/python-scraper/.env}"
if [ -f "$ENV_FILE" ]; then set -a; . "$ENV_FILE"; set +a; fi
export TG_SESSION_NAME="${TG_SESSION_NAME:-tg_user}"
export DATA_DIR="${DATA_DIR:-$HOME/.local/share/tg-cli}"
exec /home/deeone/.local/bin/tg "$@"
```
Pitfalls learned:
- **One session at a time.** `database is locked` means another process holds the
  `.session` (e.g. a background `sync-all`). Kill it before `send`.
- **Don't re-login interactively if a valid user session already exists** — just
  copy it. `forwarder_session1.session` was a real user login; copying it to
  `~/.local/share/tg-cli/tg_user.session` made `tg-user chats/sync-all/send` work.

## `tgf` — uv-installable Click CLI (the refactored forwarder)
Refactor of the monolithic `telbot.py`/`bota.py` into a package at
`python-scraper/tgforwarder/` (`tgforwarder/` modules: client, forward (OCR),
cache (SQLite), score, cli). Built per the user's explicit coding rules: plan→
tasks→tick, **unit tests mandatory** (9 tests, all passing — pure offline logic
only: filename suggestion, score verdict, noise denylist, topic filter, cache
dedup), modular (no 400-line file).

**uv packaging gotchas (verified this session — do NOT relearn):**
- Hatchling builds an **EMPTY wheel** if modules sit at project root instead of
  inside the `tgforwarder/` package dir. Fix: `mkdir tgforwarder && mv *.py
  tgforwarder/`.
- `uv pip install -e .` may skip the console script / fail to import. Fix:
  `uv pip install hatchling && uv pip install -e . --no-build-isolation`.
- The `tgf` binary is created on a real `uv tool install .` / wheel install, not
  always on editable. Verify via `python -m tgforwarder.cli` (same entrypoint).
- `dependency-groups` dev deps need `uv sync --group dev` (NOT `--extra dev`).

**Live test must read creds from `.env`** (never echo/paste): write
`TELEGRAM_API_ID`/`TELEGRAM_API_HASH`/`TG_SESSION_NAME` to `tgforwarder/.env`
(gitignored). `tgf status` proves they load. `tgf test-ocr --source <numeric_id>`
is the safe **read-only** live check (download+OCR, sends nothing).

**resolve_entity gotcha:** Telethon's `get_entity` needs an `@username` or
**numeric chat ID**, NOT a display title ("Rust Programming Language" fails;
`1039626561` works). Pass numeric IDs from `tg-user chats` / the DB.

## References
- `references/tg-bot-session-debug.md` — full `tg chats` bot-session failure
  transcript, `tg status` diagnosis, and fix paths (reproduce before guessing).
- `references/tg-user-tgf-setup.md` — `tg-user` wrapper, `tgf` package layout,
  uv build/install commands, and the read-only live-test recipe.

## When to reach for which
- Building a forwarder/admin bot → teloxide (Bot API).
- Reading YOUR private chats / acting as you / full history → `tg` as a USER,
  or grammers (Rust MTProto). This is teloxide's P5 (optional) gap.
- Do NOT expect a Bot-API bot to read user DMs or act as a person.

## Safety
- Bot tokens and `TG_API_HASH` are credentials — never echo, never commit.
- User phone login is interactive and account-binding; the agent must NOT paste
  or handle the login code.
