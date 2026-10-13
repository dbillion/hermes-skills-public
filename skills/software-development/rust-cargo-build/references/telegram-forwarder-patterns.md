# Telegram forwarder patterns (restricted vs unrestricted channels)

Verified design from a real Rust (grammers) + Python (Telethon) Telegram forwarder.

## The forward-lock problem
Many channels set `ChatForwardsRestricted` (a "forward lock"). Native `forward_messages` then
throws `ChatForwardsRestrictedError` and nothing lands. To still copy content into a reachable
destination (or Saved Messages), you must **download then re-upload** (COPY mode) instead of
forwarding.

## Native-then-upload fallback (works for both cases)
A single path handles unrestricted AND restricted sources:
1. Try native `client.forward_messages(dest, &[id], source)`.
2. On `Err` (any reason, including restriction), fall through to: download media to a temp dir,
   then `client.upload_file(path)` + `client.send_message(dest, text/media)`. For text-only,
   just `client.send_message(dest, text)`.

This is implicit but effective. Downside vs an explicit `--copy` flag: it re-uploads on ANY
native failure (including transient errors that should be retried), so behavior can be
inconsistent. Prefer an explicit copy mode when the source is known-restricted.

## Rate limiting
grammers client handles `FLOOD_WAIT` with built-in backoff — a real run will sleep (e.g. 15s)
and retry rather than crash. In Python (Telethon), wrap forward/send in a `FloodWaitError` catch
that sleeps `e.seconds` and retries. Always cap concurrency (e.g. a 15-worker semaphore) for
bulk harvests.

## Target resolution
- Saved Messages ("me"): `client.resolve_peer(PeerRef { id: PeerId::self_user(), auth: Default::default() })`.
- Numeric channel id: grammers `resolve_channel` treats a bare id as `PeerId::channel(id)`
  (strip a `-100` prefix first). User ids need `PeerId::user(id)`, not `channel`.

## Dedupe
Record forwarded (source_msg_id, target_msg_id) in a cache (DashMap / JSON file) and skip if
present, so re-runs / retries don't duplicate. `history_cache.contains_key(key)` before forwarding.
