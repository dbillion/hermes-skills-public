# OpenCLI capability inventory

OpenCLI ("Make any website your CLI. Zero setup. AI-powered.") is the Browser
Bridge that lets Agent Reach drive your real Chrome — that's why login-backed
platforms (Reddit/Facebook/Instagram/XiaoHongShu/Bilibili) work without you
pasting cookies. It is far broader than social.

## Top-level commands
list, validate, verify, skills (list/read), auth (refresh/status),
convention-audit, browser (analyze/back/bind/check/click/close/console/
dblclick/dialog/drag/eval/extract/fill/find/focus/frames/get/hover/init/
keys/network/open/screenshot/scroll/select/state/tab/type/unbind/uncheck/
upload/verify/wait), doctor, completion, plugin (create/install/list/
uninstall/update), adapter (eject/reset/status), profile (list/rename/use),
daemon (restart/status/stop), external (install/list/register).

## External CLIs bundled (13)
discord (discord-cli), docker, dws (DingTalk Workspace), gh, lark-cli,
longbridge, ntn (notion), obsidian, tg (tg-cli), vercel, wecom-cli (企业微信),
wrangler, wx (wx-cli).

## App adapters (10+) — control desktop AI apps / sites via Chrome
- antigravity — 30+ subcommands (send/read/model/nav/history/dump/state-get…)
- chatgpt-app — ask/send/read/model/new/status
- chatwise — ask/send/read/export/history/model/new/screenshot
- codex — archive/ask/send/read/...
- cursor, doubao-app, qoder, trae-cn, chatwise, codex, antigravity,
  chatgpt-app (and more)
- Plus a generic `browser` adapter that can click/fill/type/screenshot/
  extract on ANY website open in Chrome.

## Social adapters used by Agent Reach (login-backed)
reddit, facebook, instagram, xiaohongshu, bilibili, twitter (via opencli).
General form: `opencli <platform> <subcommand> -f yaml`.
Examples:
  opencli reddit hot -f yaml
  opencli facebook search "query" -f yaml
  opencli instagram profile nasa -f yaml
  opencli xiaohongshu note "NOTE_URL" -f yaml   # NOTE_URL must include xsec_token
  opencli bilibili subtitle BVxxx

## Notes
- Requires Chrome open with the OpenCLI extension, and you logged into the
  target site in that Chrome.
- `opencli doctor` diagnoses browser-bridge connectivity.
- xsec_token: XiaoHongShu forces it — you must search/feed first to get a
  full URL (with xsec_token), then read with that URL. Never a bare note_id.
