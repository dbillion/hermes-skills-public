# Telegram MTProto Forwarder + Kreuzberg (Rust OCR via Python)

Condensed patterns from building `tgforwarder` (a `tg-cli`-style CLI that
forwards media from one Telegram channel to others, OCR-renames files, and
logs the run).

## Architecture (modular, no 400-line monolith)
- `client.py` — `make_client(session)` + `resolve_entity(client, name)` (handles numeric `-100…` IDs, `@handle`, display title fails on title).
- `cache.py` — `ForwardCache` (SQLite, `UNIQUE(source_id, source_msg_id, target_id)`). For 5000+ scale add `load_done_set()` → Python `set` (O(1) membership, no per-row SQL) and `mark_many()` (executemany, one txn/50).
- `forward.py` — download → OCR-rename → `send_file(force_document=True)` (defeats protected-chat block).
- `report.py` — `ForwardLogger`: `deque(maxlen=50)` + `Counter` + window `deque` → O(1) at any scale. Render via `rich` with emoji table.
- `state.py` — resume persistence JSON: `last_message_id` + `direction` (oldest/newest).
- `cli.py` — Click group; `forward` with `--source/--dest/--path/--order/--all/--resume/--start`; interactive menu when no args.

## Kreuzberg = Rust OCR through a Python API (the fast path)
- `pip install kreuzberg` (verified 4.10.2). It is a PRECOMPILED Rust library with a Python API — no custom Rust needed.
- API: `from kreuzberg import extract_file_sync, batch_extract_files`.
  `extract_file_sync(path)` → `ExtractionResult` with `.text`, `.images`, `.tables`.
  `batch_extract_files([paths])` → Rust does them in parallel (fast for 5000+ files).
- Pattern: try `extract_file_sync` first; fall back to per-format Tesseract only if kreuzberg import fails. Wrap both in `try/except` so a missing optional dep never kills import.
- Note: kreuzberg needs no system Tesseract for its own path; keep `pytesseract` only as fallback.

## Forward ordering (oldest-first default)
- `iter_messages(src, reverse=(order=="oldest"))` → oldest = chronological from channel start (default). `min_id=offset_id` resumes AFTER the saved id (NOT `offset_id`, which means older in Telethon).
- Resume: persist `max_id` + direction; on `--resume` restore both.

## Throughput: batch many messages into ONE API call
- Native `forward_messages(target, [msg1, msg2, …])` accepts a **list** and moves all of
  them in a single request. This is the key speed lever vs. one `await` per message.
- Loop: collect `batch=[]`; when `len(batch) >= BATCH` (default 25) call
  `forward_messages(t, [m for m,_ in batch])` once per target, then `batch.clear()`.
  Flush a trailing partial batch at the end.
- Apply `--delay` **per batch**, not per message (e.g. `--batch 25 --delay 1` ≈ 25 files/s).
  Raise `--batch` (50–100) / drop `--delay` toward 0 only if not rate-limited.
- Keep dedup (`msg.id in done` set) and `mark_many()` (executemany / 50) — unchanged.
- Pitfall: a broad `except Exception: sent=None` around `forward_messages` previously
  swallowed a `Message has no attribute 'caption'` error and reported a phantom
  "forwarded: N" from cache. Verify by re-reading the returned id from the target.

## Deleted-account chats (resolve_entity fallback)
- A chat with a deleted user can't be resolved by ID: `get_entity(id)` /
  `get_input_entity` raise "Could not find the input entity for PeerUser".
- But the session's CACHED dialog still holds a valid `InputPeer`. Fix in `resolve_entity`:
  on numeric-ID resolution failure, scan `client.iter_dialogs(limit=1000)` for an entity
  whose `.id` matches, then `get_input_entity(ent)` → returns the cached
  `InputPeerUser(user_id, access_hash)` which works for `iter_messages`/`forward_messages`.
- Verified forwarding from a deleted-account chat to Saved Messages this way.

## Verify delivery (don't trust log lines)
- Re-read the returned message id from the target to confirm it arrived:
  `got = await client.get_messages(target, ids=returned_id)`; check `got.fwd_from.saved_from_peer`.
- Count-from-target (scan last N, match `fwd_from.saved_from_peer == PeerUser(src_id)`)
  is the definitive "did it actually land" check — a log "forwarded: N" can be inflated by cache.

## Env config (mirror tg-cli's cwd-config style)
- `.env` in project dir: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TG_SESSION_NAME`,
  `SOURCE_CHANNELS`, `DEST_CHANNELS`, `FORWARD_PATH`.
- Load with `load_dotenv(Path(".env"))` (NOT `find_dotenv()` — walks up to parent). Run the CLI from the project dir.
- For an INSTALLED `uv tool` binary (run from any dir), also load `~/.config/<pkg>/.env`
  and `$HOME/.env` (see uv-cli-packaging Pitfalls). Seed creds once in `~/.config/<pkg>/.env`.

## Telegram login / auth rate-limit avoidance (critical — easy to self-lock)
Creating a new session (`client.start(phone)` → `SendCodeRequest`) is the MOST
rate-limited Telegram operation. Repeated attempts during debugging caused
`FloodWaitError` (wait N seconds) then `SendCodeUnavailableError` ("all available
options for this number were already used"). Both are CODE-DELIVERY throttles, NOT
password errors — a correct 2FA password still fails if Telegram won't send a code.

Rules to avoid locking an account:
- **One login attempt at a time; wait for full completion before retrying.** Never
  loop/hammer `tgf login`. Each attempt = a fresh `SendCodeRequest` that burns quota.
- **Pre-seed creds** so login does exactly ONE `SendCodeRequest`: put
  `TELEGRAM_API_ID`/`TELEGRAM_API_HASH` (and `TG_SESSION_NAME`) in env/config BEFORE
  running login. Re-prompting wastes an attempt AND can overwrite `.env` with a
  placeholder if a test fixture leaks (guard `_persist_creds` in tests!).
- **Use a fresh, valid `api_id`/`api_hash`** from my.telegram.org. Reusing an app id
  that's already throttled doesn't help.
- **Separate session name per account** (`tgf login --session acc2` or
  `TG_SESSION_NAME=acc2`) so two accounts don't collide in `~/.local/share/tg-cli/`.
- **New Telegram accounts are MORE rate-limited** than established ones — expect
  FloodWait even on the first login, and limits on chats they can join/forward to.
  Prefer an older account for forwarding work.
- **If it fails with a wait error, STOP for the cooldown (hours).** Don't retry.
  The error text states the wait. After cooldown, ONE clean attempt.
- The 2FA ("cloud password") prompt is separate from the code; a correct 2FA password
  with `SendCodeUnavailableError` means the code couldn't be delivered, not that the
  password was wrong — don't reset 2FA (that triggers a 7-day lock).
- `ApiIdInvalidError` = creds present but invalid (regenerate at my.telegram.org),
  distinct from rate-limit errors. Handle each with a clear, distinct message.

## Verification
- Offline unit tests must cover: state roundtrip + direction, logger count/types + 5-min window + name-cap, cache bulk load (5000 rows) + mark_many, dedup set membership.
- Live: `tgf forward --order oldest --limit 3 --start` from project dir; confirm `.env` loads and real sends happen (check `Done. {forwarded: N}`).
- Secrets: `.env` gitignored; verify `git status --short | grep .env` is empty before bundling.
