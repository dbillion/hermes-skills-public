# Stubbed async-client testing (offline verification of network code)

When you cannot reach the real service (Telegram, etc.) but must prove a command
body works, drive it with an in-memory async stub. This was the key technique that
let us verify `forward_run` and `run_copy_mode` end-to-end without a live session.

## Pattern
1. Build a stub client class with `async def start/disconnect`, `async def
   get_messages/get_entity`, `def iter_messages(...)` that returns an async
   generator (`async def gen(): for m in pool: yield m; return gen()`), and the
   mutating methods (`async def forward_messages/send_message/download_media`).
2. `monkeypatch` the module's `make_client` to return your single stub instance,
   and `resolve_entity` to an `async def` returning SimpleNamespace stubs (it is
   AWAITED in the code — a plain lambda returning a value will raise
   "can't be awaited").
3. For files the code opens internally with a default path (state JSON, cache DB),
   monkeypatch the default-path helper (e.g. `state.DEFAULT_STATE`,
   `cache.default_db_path`) to point at `tmp_path` — otherwise the code writes to
   the CWD and your assertion reads a different file (silent empty result).
4. Drive the coroutine with `asyncio.run(forward_run(...))` — do NOT introduce
   `pytest-asyncio` as a dependency just for this; plain sync fns + asyncio.run keep
   the suite dependency-free.

## Gotchas hit
- `resolve_entity` is awaited → stub must be `async def`, not a lambda.
- `state.load_state()/save_state(st)` use `DEFAULT_STATE` when called with no path
  (CWD) → patch `DEFAULT_STATE`, not an env var the code ignores.
- `ForwardCache()` with no arg uses `default_db_path()` (CWD) → patch
  `default_db_path`, then read the SAME path in your assertion.
- After a failed run, clean up stray `.forward_state.json` / `forward_cache.db` the
  code wrote to the repo root.
- Give stub messages any attributes the code reads (`message_count`, media
  `.document.attributes[].file_name` for `original_filename`) or you'll get
  AttributeError inside the pipeline.

## What this proves vs. what it doesn't
Proves: dedup logic, cache mark/rebuild, verify-after-forward, resume-state save,
final report counts. Does NOT prove: real auth, real API acceptance, rate limits.
State that boundary honestly — live login still needs valid creds + the user's phone.
