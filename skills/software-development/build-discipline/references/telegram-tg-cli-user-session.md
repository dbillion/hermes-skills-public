# Telegram `tg` (kabi-tg-cli) — making `tg chats` / sync work as a USER

## Symptom
`tg chats` (or any dialog-listing command) fails with a traceback at
`tg_cli/cli/tg.py` `list_chats` / `iter_dialogs`.

## Root cause
`tg` is Telethon (MTProto **user-client**), not Bot API. If its session file
(`~/.local/share/tg-cli/tg_cli.session` by default) is authenticated as a **bot**
(`phone: ''`, e.g. `Dredai_bot`), `iter_dialogs()` returns nothing / errors —
bots can't list dialogs. The CLI calls `TelegramClient(...).start()` with no args,
so it reuses whatever session exists and never re-prompts.

Also: using the default `api_id=2040` (Telegram Desktop shared creds) makes
Telegram silently **drop the login code** ("code not sent"). Need your own creds.

## Fix (verified this session)
1. Get your own `TG_API_ID` / `TG_API_HASH` from https://my.telegram.org.
2. Put them in a local `.env` (NOT in chat):
   ```
   TG_API_ID=28150103
   TG_API_HASH=2a08e3e1c377472a2dc8fc60976bc921
   ```
3. You likely already have a real **user** session from another scraper
   (`forwarder_session1.session` in the python-scraper dir — it resolves to your
   personal account, e.g. `@oludayor`). Copy it to the tg-cli session location
   under a separate name so the bot session is untouched:
   ```bash
   cp forwarder_session1.session ~/.local/share/tg-cli/tg_user.session
   ```
4. Run via a wrapper that sets creds + the user session name:
   ```bash
   TG_API_ID=... TG_API_HASH=... TG_SESSION_NAME=tg_user tg chats
   ```
   Also works: `tg-user` wrapper script that sources the `.env` and execs `tg`.

## Notes
- One session file at a time. `database is locked` means another tg process
  (e.g. `sync-all`) holds the SQLite session — kill it before `send`.
- `tg send <chat> "<msg>"` posts AS YOU (user). Useful for channels you're in.
- Local-first: `tg sync-all -n 200` populates `~/.local/share/tg-cli/messages.db`;
  `tg recent` / `tg search` then read that DB offline.
- `tg_chat_scorer.py` ranks chats by usefulness (recency, sender diversity, topic
  relevance, noise denylist) — pure SQLite read, no Telegram needed.
