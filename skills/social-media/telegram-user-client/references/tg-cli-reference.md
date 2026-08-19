# tg-cli reference — command map, session layout, failure/repair transcripts

## Session file map
- `tg` resolves session as: `~/.local/share/tg-cli/<TG_SESSION_NAME>.session`
- Default `TG_SESSION_NAME=tg_cli` → bot session (`Dredai_bot`, phone empty)
- User session used here: `TG_SESSION_NAME=tg_user` → `~/.local/share/tg-cli/tg_user.session`
- Source of the working user login: `/home/deeone/Documents/scraper/python-scraper/forwarder_session1.session`
  (verified USER: phone=37258041861, username=@oludayor, id=1255087768)
  → copied (NOT moved) to the tg_user location.

## `tg status` output shape
```
ok: true
data:
  authenticated: true
  user:
    id: 6574292251
    username: Dredai_bot      # bot session
    phone: ''                 # EMPTY = bot; non-empty = user
```

## Full command signatures (from `tg <cmd> --help`)
- `tg chats`                list dialogs (USER sessions only)
- `tg sync-all -n 200`      pull messages into local SQLite DB; 1s/chat delay;
                            SLOW → run background. `--max-chats N` to limit.
- `tg recent -n 10`        browse recent from local DB (empty until synced)
                            flags: `-c/--chat`, `-s/--sender`, `--hours N`,
                            `--sync-first`, `--sync-limit N`
- `tg search KEYWORD`       search local DB. flags: `-c`, `-s`, `--hours`,
                            `--regex`, `--sync-first`, `--sync-limit`, `-n`
- `tg history <chat> -n N`  fetch history for one chat
- `tg export <chat> --json` export to file
- `tg status` / `tg whoami` auth state

## Failure transcript → repair
### Symptom A: `tg chats` traceback
```
File ".../tg_cli/cli/tg.py", line 52, in _run
    return await list_chats(client, chat_type)
```
Cause: active session is a BOT (Dredai_bot). Bots cannot `iter_dialogs()`.
Repair: switch to a user session (set TG_SESSION_NAME=tg_user to a user .session).

### Symptom B: `recent -c "GroupName"` / `search -c "GroupName"`
```
telethon.errors.rpcerrorlist.UsernameNotOccupiedError:
  The username is not in use by anyone else yet
```
Cause: `-c` resolves the string as a @username; group NAMES with spaces are
not usernames.
Repair: omit `-c`, or use the numeric chat ID from `tg chats` output.

### Symptom C: interactive login "Please enter your phone... Aborted!"
Cause: no TTY (headless/agent session) → `client.start()` aborts immediately.
Repair: DO NOT run login via the agent. Either reuse an existing user .session
(copy it), or run the one-off login script in a real local terminal.

## One-off user login script (run locally, needs TTY)
```python
import os
from dotenv import load_dotenv; load_dotenv(".env")
from telethon import TelegramClient
c = TelegramClient("~/.local/share/tg-cli/tg_user",
                   int(os.environ['TG_API_ID']), os.environ['TG_API_HASH'])
c.start()              # prompts phone + code + 2FA
me = c.get_me(); print(me.username, me.phone)
c.disconnect()
```
NOTE: never paste TG_API_ID/TG_API_HASH into chat; put them in a local .env.

## venv gotcha
`python3 -m venv` FAILS under uv-managed CPython (prefix `/install`):
  "failed to get the Python codec of the filesystem encoding"
Fix: `uv venv .venv && . .venv/bin/activate && uv pip install telethon python-dotenv`
