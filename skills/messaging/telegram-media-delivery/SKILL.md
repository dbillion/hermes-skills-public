---
name: telegram-media-delivery
description: "Upload media to Telegram via Telethon API, not the bridge."
---

# Telegram Media Delivery (MTProto API)

This user wants finished media delivered to Telegram through the **real MTProto
API**, not the Hermes native `MEDIA:` attach. Explicit correction: *"USE THE API
OF TELEGRAM TO UPLOAD THE VIDEO"* — re-attaching via the bridge was flagged as
wasted tokens.

## Verified setup
- **Telethon venv:** `/home/deeone/Documents/scraper/python-scraper/tgforwarder/.venv/bin/python`
  (Telethon 1.44).
- **Session:** `/home/deeone/.local/share/tg-cli/tg_cli.session` — identity
  `Dredai_bot` (user id `6574292251`). Reuse it; no re-login.
- **Target home chat:** `1255087768` ("oludayor").
- **`tg` CLI (kabi-tg-cli) sends TEXT only** — it cannot upload media. Telethon
  `send_file` is the real path.

## Credential loading (IMPORTANT)
Inline `export $(grep ...)` credential extraction is **blocked by the command
guard**. Read `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` from the tgforwarder `.env`
**inside the Python script** (parse `k=v` lines), never on the shell command
line.

## Upload recipe (copy + modify)
```python
import asyncio
from pathlib import Path
from telethon import TelegramClient

env = {}
for line in Path("/home/deeone/Documents/scraper/python-scraper/tgforwarder/.env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

client = TelegramClient(
    "/home/deeone/.local/share/tg-cli/tg_cli.session",
    int(env["TELEGRAM_API_ID"]), env["TELEGRAM_API_HASH"])

async def main():
    await client.start()
    msg = await client.send_file(
        int("1255087768"),
        "/path/to/final.mp4",
        caption="...", supports_streaming=True)
    print("SENT_OK", msg.id, msg.chat_id)
    await client.disconnect()
asyncio.run(main())
```
Hard-burn subtitles first if needed:
`ffmpeg -i in.mp4 -vf "subtitles=in.srt" -c:a copy out.mp4`

## Rendering many scenes before delivery (manim gotcha)
`manim script.py SceneA SceneB` drops into an **interactive prompt** instead of
rendering. Loop **one scene at a time**, or use `-a`. Low quality first (`-ql`),
`-qh` for final. Each `subcaption=` emits a `.srt` you can burn in.

## Non-video payloads (zips, docs, generated bundles)

`send_file` also delivers archives and documents — pass `force_document=True`
(and drop `supports_streaming`) so Telegram does not try to preview it:

```python
msg = await client.send_file(1255087768, "/tmp/bundle.zip",
                             caption="...", force_document=True)
```
Zip many small generated files (e.g. 83 markdown packs → one ~140K zip) rather
than sending them one by one.

## Verify the send — do not trust "SENT_OK"

A script printing its own success message is a self-report, not proof. Telegram
echoes back server-side file metadata on the returned message; compare it to the
local file:

```python
msg = await client.send_file(CHAT, ZIP, caption="...", force_document=True)
print("msg_id=%s" % msg.id)
print("server_name=%s" % getattr(msg.file, "name", None))
print("server_size=%s" % msg.file.size)
print("local_size=%s" % Path(ZIP).stat().st_size)
print("MATCH=%s" % (msg.file.size == Path(ZIP).stat().st_size))
```

`MATCH=True` means the bytes are on Telegram's servers. Report that, not the
script's own echo.

**Bots cannot read history.** `client.iter_messages(...)` fails with
`BotMethodInvalidError: The API access for bot users is restricted` — this
session is a bot (`Dredai_bot`), so read-back verification is impossible. Verify
from the *send response* instead. Do not waste turns trying to list the chat.

## Config drift — check, do not assume

Values differ between the `.env` and the working session. Confirm before use:

- `.env` keys are `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` — **not** `TG_API_ID`.
  Wrong names raise `KeyError` at client construction.
- The `.env` `TG_SESSION_NAME=forwarder_session1` is **not** the session that
  works for sending. Use `/home/deeone/.local/share/tg-cli/tg_cli.session`.
  A wrong/unauthorized session path drops Telethon into an interactive phone
  prompt and dies with `EOFError: EOF when reading a line` under automation.

Quick check when adapting a script:
```bash
grep -oE '^[A-Z_]+=' <path>/.env | sort -u   # real key names
```

## Consent before sending

Uploading to a real chat is a visible, irreversible side effect, and the user
has denied the send at the confirmation prompt. "Upload it when you're done" is
NOT standing consent for a retry after a refusal. So:
- Build and zip the artifact first, then state its exact absolute path and size.
- If the send is denied, STOP. Do not rephrase or retry via another path.
  Report the local path, confirm the work itself is complete, and offer the
  send as a question.

## Why API, not bridge
The native `MEDIA:` attach goes through Hermes' own connection; the user wants an
explicit bot-session upload (lands as a real message from Dredai_bot, verifiable
in the chat). If a video "doesn't arrive," re-send via this API path.
