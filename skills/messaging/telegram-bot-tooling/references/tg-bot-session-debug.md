# `tg chats` bot-session debug (reproduction recipe)

## Symptom
```
File "/home/deeone/.local/share/uv/tools/kabi-tg-cli/lib/python3.14/site-packages/tg_cli/cli/tg.py", line 52, in _run
    return await list_chats(client, chat_type)
```
Reported by user as "failing when given a bot token instead of a number."

## Diagnosis steps that pinned the root cause
1. Read the failing file: `tg.py` `tg_chats` → `async with connect() as client: return await list_chats(client, chat_type)`.
2. Read `client.py`: `from telethon import TelegramClient` → confirms MTProto/Telethon, NOT Bot API.
3. `tg status` → the decisive output:
   ```
   authenticated: true
   user:
     id: 6574292251
     username: Dredai_bot
     phone: ''
   ```
   Session IS authenticated, but as a **bot** (phone empty, bot username).

## Root cause (corrected a misdiagnosis)
- The "bot token vs numeric chat ID" framing is a **red herring**. Telethon's
  `.start(bot_token=...)` accepts a bot token and logs in as a bot session —
  so the token authenticated fine.
- The failing call `list_chats` → `client.get_dialogs()` is a **user-level
  operation**. Bots cannot enumerate dialogs the way users can. A bot session's
  dialog list is sparse/empty, and Telethon's dialog fetch for a bot is
  unreliable → error at tg.py:52.

## Fix paths
- Keep as bot (Dredai_bot): `chats`/`sync-all`/`refresh` stay broken; `send`/
  `history` to a chat the bot is in may work.
- Convert to user client (full power):
  - Set `TG_API_ID` / `TG_API_HASH` from https://my.telegram.org (default
    `2040` warns of restriction risk).
  - Log in with your **phone number** interactively (agent must NOT handle the
    code). Produces a user `.session`.
  - Then `chats`/`sync-all`/`search` work.

## Quick command reference used
- `tg status` — show authenticated user (bot vs user tells you the session type)
- `tg chats` — the failing dialog-listing command
- `tg --help` — lists all subcommands (no `login` subcommand; auth is
  interactive on first `connect()`)

## Key teaching point for future sessions
When a `tg`/Telethon command fails on a "dialog" operation, ALWAYS run
`tg status` first. If `phone: ''` and the username ends in `_bot`, the session
is a bot and dialog-listing ops are expected to fail — do NOT chase the chat-ID
argument. The fix is a user login, not a different chat reference.
