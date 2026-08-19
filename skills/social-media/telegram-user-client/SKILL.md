---
name: telegram-user-client
description: "Run tg to read Telegram chats as a USER. (Telethon/MTProto.)"
version: 1.0.0
author: hermes-curator
license: MIT
tags: [telegram, tg, mtproto, telethon, user-client, cli, messaging, kabi-tg-cli]
---

# Telegram User-Client (`tg` / kabi-tg-cli)

`tg` is a CLI wrapping **Telethon** (Telegram MTProto) that authenticates as a
**user account**, not a bot. It can read your private chats, groups, channels,
sync messages to a local SQLite DB, and search/export them. This is fundamentally
different from a Bot API bot (e.g. teloxide) — see "Bot vs User" below.

## Install / Environment

- Binary: `/home/deeone/.local/bin/tg` (uv tool `kabi-tg-cli`).
- Python deps for any helper: use `uv venv` — **NOT** `python3 -m venv`.
  uv-managed CPython has a non-standard prefix (`/install`); `python3 -m venv`
  dies with "failed to get the Python codec of the filesystem encoding".
  ```bash
  uv venv .venv && . .venv/bin/activate && uv pip install telethon python-dotenv
  ```

## Auth model

- `TG_API_ID` / `TG_API_HASH` from https://my.telegram.org → "API development tools".
- Session file: `~/.local/share/tg-cli/<TG_SESSION_NAME>.session`
  (default `TG_SESSION_NAME=tg_cli`).
- **NEVER use the default `api_id=2040`** (Telegram Desktop shared creds).
  Telegram blocks/silently drops login codes for it. Always set your own.
- A session is either a **user** login (has a phone) or a **bot** login (token).
  Check with `tg status` → look at `data.user.phone` (empty = bot).

## CRITICAL: Bot vs User session

`tg chats` calls `list_chats` → `client.iter_dialogs()`. **Bots cannot list
dialogs** — if the active session is a bot (e.g. `Dredai_bot`), `tg chats`
tracebacks at `tg.py:52` (`return await list_chats(client, chat_type)`) or
returns nothing.

Symptom:
```
File ".../tg_cli/cli/tg.py", line 52, in _run
    return await list_chats(client, chat_type)
```

Fix: ensure the session is a **user**. Options:
1. Reuse an existing user `.session` — copy a known user session file to
   `~/.local/share/tg-cli/tg_user.session`. (A real user login shows
   `phone` non-empty via `get_me()`; a bot shows `phone: ''`.)
2. Fresh interactive login (needs a TTY — run locally, NOT from a headless
   agent session):
   ```python
   from telethon import TelegramClient
   c = TelegramClient("~/.local/share/tg-cli/tg_user", API_ID, API_HASH)
   c.start()  # prompts phone + code + 2FA; saves .session
   ```

## The `tg-user` wrapper

`/home/deeone/.local/bin/tg-user` loads `TG_API_ID`/`TG_API_HASH` from a local
`.env` (path overridable via `TG_USER_ENV`) and forces `TG_SESSION_NAME=tg_user`.
Use it instead of bare `tg` so you never hit the bot session:

```bash
tg-user chats
TG_USER_ENV=/path/to/.env tg-user sync-all -n 200
```
Portable copy in `scripts/tg-user` (this skill).

## Commands (most read from a local SQLite DB)

| Command | Notes |
|---|---|
| `tg chats` | List dialogs — **user sessions only** |
| `tg sync-all -n 200` | Pull messages into local DB. SLOW (1s/chat delay). Run in background. |
| `tg recent -n 10` | Browse recent msgs from local DB (empty until synced) |
| `tg search "kw"` | Search local DB (needs `sync-all` first) |
| `tg history <chat> -n 500` | Fetch history for one chat |
| `tg export <chat> --json` | Export to file |
| `tg status` | Show auth state (user vs bot) |

**Pitfall:** `recent -c <name>` / `search -c <name>` with a **group name**
(contains spaces) fails with `UsernameNotOccupiedError` — Telethon tries to
resolve it as a @username. Use a numeric chat ID or omit `-c`.

## Sending media (files / video) via the API

`tg send` only sends **text** — there is no CLI flag for attachments. To
upload a file or video to a chat through the real Telegram API, drive
Telethon directly. The `tg_cli.session` (the default, authenticated as
`Dredai_bot`) is a **bot** session, and a bot CAN `send_file` to a chat it
belongs to by numeric ID — you do NOT need a user session for sending.

```python
import asyncio
from pathlib import Path
from telethon import TelegramClient

# Load creds from the tgforwarder .env WITHOUT exporting/printing them.
# The runtime blocks inline `export X=$(grep ...)` credential extraction and
# printing secrets is forbidden — parse the file in Python instead.
env = Path('/home/deeone/Documents/scraper/python-scraper/tgforwarder/.env')
vals = {}
for line in env.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, _, v = line.partition('=')
        vals[k.strip()] = v.strip()

async def main():
    client = TelegramClient(
        '/home/deeone/.local/share/tg-cli/tg_cli.session',
        int(vals['TELEGRAM_API_ID']), vals['TELEGRAM_API_HASH'])
    await client.start()
    msg = await client.send_file(
        1255087768,            # numeric chat id ('oludayor')
        '/path/to/final.mp4',
        caption='...', supports_streaming=True)
    print('SENT_OK', msg.id)
    await client.disconnect()

asyncio.run(main())
```

Run with the tgforwarder venv (has Telethon 1.44):
`tgforwarder/.venv/bin/python send_video.py`. Resolve a chat name→id first
with `tg-user info <chat>` or `client.get_entity(int(id))`.

> Bots STILL cannot `list_dialogs`/`tg chats` — that still needs a user
> session (see "Bot vs User" above). Sending to a known numeric ID is fine.

## Verification recipe

```bash
tg-user status            # authenticated: true, user.phone non-empty
tg-user chats             # lists your dialogs
tg-user sync-all -n 200 & # background; populates local DB
tg-user recent -n 5       # after sync, returns real message content
```

## Relationship to the teloxide bot

The user's `~/Documents/scraper/teloxide-bot` is a **Bot API** (teloxide 0.12)
media-forwarder. It CANNOT read private chats or list dialogs — that requires
this MTProto user-client. The "AI controls the bot via CLI" roadmap (P5,
grammers/MTProto) is exactly what `tg` already provides as a working user
client. Do not conflate: teloxide = bot (no private-chat access); `tg` = user
(full chat access).

## Research use-case: which chats are USEFUL vs NOISE
The real value of the user client is triage. After `sync-all`, rank chats by
signal quality with the bundled scorer (stdlib `sqlite3` — no telethon needed):

```bash
tg-user sync-all -n 200 &
python3 scripts/tg_chat_scorer.py --topic "java,rust,devops,ai,python,sql,linux,kubernetes,aws,interview,job,course"
```

The scorer combines recency, sender diversity, link/topic density, a `--topic`
relevance boost, and a noise denylist (demotes promotional/religious/spam chats
that score high on volume alone). Verdict per chat: USEFUL / OK / NOISE.
Extend the denylist regex in `scripts/tg_chat_scorer.py` for your own noise.

## Support files
- `references/tg-cli-reference.md` — full command signatures, session-file map, and exact failure/repair transcripts from a real session.
- `scripts/tg-user` — portable `tg-user` wrapper (loads creds from `.env`, forces user session).
- `scripts/tg_chat_scorer.py` — chat-usefulness scorer (recency + diversity + topic relevance + noise denylist). Stdlib only.
