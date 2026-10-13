---
name: tgf-telegram-forwarder-setup
description: Setup/operate the tgf Telegram MTProto forwarder CLI.
---

# tgf (tgforwarder) — Telegram MTProto Forwarder Setup & Ops

A modular, `uv`-installable CLI (`tgf`) that forwards media/text from one Telegram
channel to others via MTProto (Telethon), OCR-renames files (Rust **kreuzberg**),
dedups locally (SQLite), and logs an emoji summary. Built for research/scraping
triage by dbillion (Oludayo Adeoye).

## Architecture (modular — NO monoliths)
- `tgforwarder/client.py` — TelegramClient session + `resolve_entity` (numeric/-100 ID, @handle, name)
- `tgforwarder/cache.py` — `ForwardCache` SQLite dedup; `load_done_set()` (bulk→set), `mark_many()` (batched executemany)
- `tgforwarder/forward.py` — OCR via **kreuzberg** (Rust) primary, Tesseract fallback; `extract_text`, `batch_extract`
- `tgforwarder/state.py` — resume persistence: `last_message_id` + `direction` per source
- `tgforwarder/report.py` — `ForwardLogger`: deque(maxlen)+Counter+window deque → O(1) at 5000+ files
- `tgforwarder/cli.py` — Click CLI: `forward` (--order oldest|newest, --all, --dest, --path, --resume/--start), `score`, `test-ocr`, `status`
- `tests/test_offline.py` — 14 offline tests (no network/API)

## Setup (fresh machine)
1. Creds: create `tgforwarder/.env` (gitignored — NEVER commit):
   ```
   TELEGRAM_API_ID=<id>
   TELEGRAM_API_HASH=<hash>
   TG_SESSION_NAME=forwarder_session1
   SOURCE_CHANNELS=-100...
   DEST_CHANNELS=-100...,-100...
   FORWARD_PATH=downloads
   ```
2. Session: need a **user** `.session` (MTProto can't use a bot token for this).
   Copy an existing logged-in user session to `~/.local/share/tg-cli/forwarder_session1.session`
   OR generate one with a Telethon login helper. One session at a time (DB lock if a sync runs concurrently).
3. Python env:
   ```
   cd tgforwarder
   uv venv .venv && . .venv/bin/activate
   uv pip install -e .
   # OCR fast path:
   uv pip install kreuzberg        # precompiled Rust, Python-callable
   ```
4. Install the CLI globally (same mechanism as tg-cli):
   ```
   uv tool install . --no-cache
   ```
   → binary at `~/.local/bin/tgf`, package in `~/.local/share/uv/tools/tgforwarder/`.

## CRITICAL: build-backend + dotenv pitfalls (learned the hard way)
- **Use `setuptools`, NOT hatchling.** Hatchling produced wheels whose RECORD omitted
  the package `.py` files → `uv tool install` installed the script+metadata but NO code
  (`ModuleNotFoundError` at runtime). Setuptools builds correct wheels.
  pyproject: `requires=["setuptools>=68"]`, `build-backend="setuptools.build_meta"`,
  `[tool.setuptools.packages.find] include=["tgforwarder*"]`.
- **`find_dotenv()` is a trap.** It walks UP from cwd and finds the NEAREST parent `.env`
  — e.g. it loads `/home/deeone/.env` instead of the project's. Always load the project
  `.env` explicitly: `load_dotenv(Path(".env"), override=False)`. Run `tgf` from the
  project dir (or via `python -m tgforwarder.cli`) so cwd=.env location.
- **`uv tool install` caches wheels by content hash.** After fixing the build, use
  `rm -rf dist && uv build --wheel --no-cache && uv tool uninstall tgforwarder && uv tool install . --no-cache`.
- **`min_id` vs `offset_id`:** Telethon `iter_messages(offset_id=X)` returns OLDER msgs
  (<X). For "resume from last forwarded", use `min_id=X` (newer than X). `reverse=True`
  yields oldest-first.
- **Deleted-account chats:** a chat with a deleted user can't be resolved by ID
  (`resolve_entity`/`get_input_entity` raise "Could not find the input entity for
  PeerUser"). But the session's CACHED dialog still holds a valid InputPeer. Fix: in
  `resolve_entity`, on numeric-ID failure, scan `client.iter_dialogs(limit=1000)` for an
  entity whose `.id` matches, then `get_input_entity(ent)` — returns the cached
  `InputPeerUser(user_id, access_hash)` which works for `iter_messages`/`send_file`.
  Verified forwarding from deleted-acct chat 558372819 -> Saved Messages (1255087768).

## OCR: kreuzberg (Rust) is the fast path
- `kreuzberg` is a precompiled Rust library with a Python API. No custom Rust needed.
- `from kreuzberg import extract_file_sync, batch_extract_files`
- `extract_file_sync(path)` → `ExtractionResult` with `.text`, `.images`, `.tables`.
- `batch_extract_files([paths])` → Rust-parallel extraction (use for 5000+ files).
- If kreuzberg import fails, `forward.py` falls back to per-format Tesseract
  (needs system `tesseract` + `pdf2image`/`opencv`/`docx2txt`).
- To verify: `python -c "from kreuzberg import extract_file_sync; print('ok')"`.

## Forward ordering & scaling (the 5000-file design)
- Default `--order oldest` = forward the channel's OLDEST posts first (chronological).
  Interactive menu prompts oldest/newest + start/resume.
- **Dedup at scale:** `cache.load_done_set(src.id, tgt.id)` loads done msg_ids into a
  `set` (O(1) lookup); loop checks `msg.id in done`. `mark_many()` flushes every 50.
- **Logging at scale:** `ForwardLogger` uses `deque(maxlen=50)` for names, `Counter` for
  types, `deque` for the 5-min window — all O(1), memory-bounded regardless of file count.
- `--all` processes the entire channel; `--limit N` caps; `--resume` continues from saved id.

## Commands (cheat-sheet)
```
tgf status                       # api configured? (reads .env from cwd)
tgf forward --order oldest --limit 10 --start
tgf forward --resume             # continues from .forward_state.json
tgf forward --order newest --all --path ./downloads --delay 2
tgf score --db ~/.local/share/tg-cli/messages.db --topic "rust,devops,ai" --top 5
tgf test-ocr --source <numeric_id>   # OCR-only, read-only, needs numeric ID not title
```
- `test-ocr` / `resolve_entity` need a **numeric channel ID** (e.g. `-1001961116802`) or
  `@handle` — NOT a display title ("Rust Programming Language" fails to resolve).
- `score` reads the tg-cli `messages.db` (populated by `tg-user sync-all -n 200`).

## tg-user wrapper (run kabi-tg-cli AS THE USER, not the bot)
- `tg-user` = bash wrapper at `~/.local/bin/tg-user`; loads `TG_API_ID/TG_API_HASH` from
  `python-scraper/.env`, sets `TG_SESSION_NAME=tg_user`, then `exec tg "$@"`.
- Why: the `Dredai_bot` session can't list dialogs; the user session (`forwarder_session1`
  or `tg_user`) can. Copy your logged-in `.session` to `~/.local/share/tg-cli/`.
- `tg-user chats` / `tg-user sync-all -n 200` / `tg-user recent` / `tg-user send <id>`.

## PUSH (PUSH STALL — verified 2026-07-18)
`git push github.com` HANGS from this host (pack stalls; ls-remote/ssh -T work).
- Do NOT attempt direct push. Instead: `git bundle create tgforwarder.tgf.bundle HEAD`
  then push the bundle from an egress machine:
  `git clone <repo> && cd repo && git fetch /path/tgforwarder.tgf.bundle HEAD && git push origin HEAD`
- Always `git status --short | grep '\.env'` to confirm NO secret file is staged before commit.

## Verification checklist (finish = prove it works)
1. `python -m pytest -q` → 14 passed (offline, no network).
2. `rm -rf dist && uv build --wheel --no-cache` → wheel contains `tgforwarder/*.py`
   in RECORD (verify: `python -c "import zipfile,glob; z=zipfile.ZipFile(sorted(glob.glob('dist/*.whl'))[-1]); print([n for n in z.namelist() if n.endswith('cli.py')])"`).
3. `uv tool install . --no-cache` → `which tgf` resolves; `tgf --help` works.
4. `tgf status` from project dir → "api configured: yes".
5. Live smoke (needs user session): `tgf forward --start --order oldest --limit 2` →
   forwards, writes `.forward_state.json`, prints emoji report.
6. `git status` shows `.env` UNTRACKED.

## Gotchas summary
- Secrets (API id/hash, session) are gitignored `.env` only — never paste into code.
- Run `tgf` from the project dir (dotenv loads `./.env`).
- Hatchling wheel RECORD bug → use setuptools.
- Numeric channel IDs, not titles, for resolve/test-ocr.
- One Telegram session at a time (concurrent sync holds the DB lock).
- Direct `git push` hangs → use `git bundle`.
