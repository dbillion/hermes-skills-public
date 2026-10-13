# tg-user + tgf setup (verified this session)

## The bot-session problem
`tg chats` / `tg sync-all` fail because the default `tg_cli.session` is the BOT
`Dredai_bot` (phone:''). `list_chats`/`get_dialogs` are user-level ops; bots
can't enumerate dialogs. Symptom: traceback at `tg_cli/cli/tg.py` line 52
`list_chats(...)`.

## Fix A — reuse an existing USER session (no interactive login)
A real user login already existed: `forwarder_session1.session` (`@oludayor`).
Copy it under the tg-user session name:
```bash
mkdir -p ~/.local/share/tg-cli
cp python-scraper/forwarder_session1.session ~/.local/share/tg-cli/tg_user.session
```
Then drive `tg` with the `tg-user` wrapper (loads creds from `.env`, sets
`TG_SESSION_NAME=tg_user`). Now `tg-user chats`, `tg-user sync-all -n 200`,
`tg-user recent`, `tg-user send <id> "<msg>"` all work as a USER.

## Fix B — the `tg-user` wrapper
`/home/deeone/.local/bin/tg-user` (bash): sources a local `.env` for
`TG_API_ID`/`TG_API_HASH`, exports `TG_SESSION_NAME=tg_user`, `DATA_DIR`, then
`exec /home/deeone/.local/bin/tg "$@"`. Make executable: `chmod +x`.

## Pitfalls
- `database is locked` → another process holds the `.session` (e.g. background
  `sync-all`). Kill it before `send`.
- `tg` has no interactive `login` command; `connect()` calls `start()` which
  prompts for phone when the session is new. Don't run login from the agent —
  it needs a TTY + the code Telegram pushes to your app.

## tgf — uv Click CLI (refactored forwarder)
Package: `python-scraper/tgforwarder/` → modules `client, forward, cache, score, cli`.
Install / dev loop:
```bash
cd python-scraper/tgforwarder
uv sync --group dev            # dev deps (pytest) — NOT --extra dev
uv pip install hatchling      # needed for editable
uv pip install -e . --no-build-isolation   # editable; makes import work
# verify:
python -m tgforwarder.cli --help
python -m pytest -q           # 9 passed (offline logic only)
```
Build a real wheel (creates the `tgf` console script on `uv tool install .`):
```bash
uv build --wheel              # modules MUST be inside tgforwarder/ or wheel is EMPTY
```
Run the safe read-only live check (creds from `tgforwarder/.env`, never echoed):
```bash
python -m tgforwarder.cli status            # "api configured: yes"
python -m tgforwarder.cli test-ocr --source 1039626561   # download+OCR, sends nothing
python -m tgforwarder.cli score --db ~/.local/share/tg-cli/messages.db --topic "java,rust,devops,ai"
```
`resolve_entity` needs `@username` or numeric ID — NOT a display title.

## User coding rules enforced on this class of task
Plan → tasks → tick each. Unit tests mandatory (no tests = failure). Break into
modules; no 400-line monoliths. Load `ponytail`/`code-refactoring` for structure.
