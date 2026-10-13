# Telethon Dedup & Verification — Probed Facts & Repair Recipe

Condensed from the 2026-07-28 session that fixed the tgforwarder duplicate/cache-lie bug.

## The bug we hit
Naive dedup: `mark done` the instant `forward_messages` returned truthy. With a
deleted-account source peer (558372819), `forward_messages` returned truthy for
messages that NEVER persisted. The cache claimed 8,255 done while only 2,910 truly
landed. Re-runs skipped the 5,345 real messages forever and reported false success.
User saw duplicates + "only 2910 saved" and rightly called the logger/cache unacceptable.

## Telethon capability facts (PROBED — do not re-derive, do not full-scan blindly)
- NO server-side filter for `fwd_from.saved_from_peer`. `iter_messages(tgt, from_user=src)`
  returns 0 matching forwards: a forwarded copy in Saved has YOU/the bot as its *sender*,
  not the source. No `messages.search` param exists for "forwards from peer X".
  => Reading `saved_from_msg_id` REQUIRES fetching message objects. The 14k-message
  download is the irreducible cost of a ONE-TIME repair, NOT of forwarding.
- Forwarding is id-based, no source download: `client.forward_messages(tgt, [msg_ids])`.
  Batched 25/call = fast, under rate limits.
- Instant total count (no scan): `await client.get_messages(chat, limit=0)` -> `.total`,
  or `dialog.message_count` from `iter_dialogs`.
- Dedup identity: stable pair `(source_peer_id, msg.id)`. Forwarded copies carry
  `fwd_from.saved_from_peer` + `fwd_from.saved_from_msg_id` back to origin. No content hash.

## Repair / truth architecture (what shipped in 4f3eb58)
1. Ground-truth rebuild: scan target for `fwd_from.saved_from_peer == src`, collect
   `saved_from_msg_id`, call `cache.rebuild_done_set(src.id, tgt.id, delivered)`.
2. Verified write-through: after forward, `get_messages(tgt, ids=[...])`; only `mark_many`
   ids that exist. Ghost returns -> not marked (retry) + released from `done`.
3. Optimistic reservation: reserve id in `done` before sending; persist only after verify.
4. Conditional rebuild: `load_done_set` (indexed SQLite query) when cache populated =
   O(1), 0 downloads. Full scan ONLY when cache empty or `--force-rebuild`.
5. `--quick-rebuild`: newest-first scan, stop after `cold_after=200` consecutive non-
   matches (recency-bounded). Fast; use only on a trusted, populated cache.

## Commands added
- `tgf forward --rebuild-cache` (default on) / `--no-rebuild-cache` / `--force-rebuild`
  (full authoritative scan) / `--quick-rebuild` (recency-bounded).
- `tgf dedupe --source ID --target ID [--dry-run]`: removes duplicate forwarded copies
  from target, keeping one per `saved_from_msg_id` (deletes via `client.delete_messages`,
  chunked 100). Run `--dry-run` first to count.

## Gotcha: session DB lock
Concurrent `tgf` runs (or a killed run leaving a zombie python process) hold
`~/.local/share/tg-cli/forwarder_session1.session` -> "database is locked" on next run.
Kill zombies (`ps aux | grep 'tgf forward'`), `rm -f ...session-journal/-wal/-shm`, retry.
