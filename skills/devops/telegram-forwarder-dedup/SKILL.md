---
name: telegram-forwarder-dedup
description: Telethon forwarder dedup and verification architecture.
---

# Telegram Forwarder — Dedup & Verification

Reusable technique for any Telethon-based forwarder that must NOT create duplicates and
must verify delivery without trusting its own cache. Distilled from a session that fixed
tgforwarder's "cache claimed 8255 done but only 2910 landed, user saw duplicates" bug.

## When to use
- Building dedup for a Telegram forwarder/scraper.
- A forwarder reports success but messages are missing OR duplicated in the target.
- Someone asks "can the API tell me how many messages are in a chat without scanning?" or
  "can I filter forwards by their original source?" — answer is in Facts below.

## Core architecture (three layers — do NOT skip any)
1. **Ground-truth rebuild (the cache must not be the source of truth).**
   Before forwarding, derive the real delivered set FROM THE TARGET:
   scan it for messages whose `fwd_from.saved_from_peer == source`, collect their
   `saved_from_msg_id`, and overwrite the cache with exactly that set.
   Dedup key = stable pair `(source_peer_id, msg.id)`. `msg.id` is unique per chat; a
   forwarded copy carries `fwd_from.saved_from_peer` + `fwd_from.saved_from_msg_id` back
   to the origin. NO content hash needed.
2. **Verified write-through.** After `forward_messages`, re-read the returned ids from the
   target (`get_messages(tgt, ids=[...])`) and only persist the ones that genuinely exist.
   Ghost returns (truthy but not in target) are NOT marked — they retry next run, and their
   id is released from the in-memory `done` set so they aren't skipped forever.
3. **Optimistic reservation.** Reserve a msg id in `done` the moment you decide to forward
   it, so a restart/re-run can never re-pick it. Persist only after (2) confirms.

## NEVER full-scan the target on every run
Persist the rebuilt set to SQLite. On normal reruns the cache is already populated →
`load_done_set` is ONE indexed query = **0 messages downloaded**. The full target scan runs
ONLY when the cache is empty or an explicit `--force-rebuild` is passed. A steady-state run
must be instant. (User hard-corrected: "downloading 12000 messages every run is unacceptable.")

## Facts (PROBED — trust these, do not re-derive)
- **No server-side filter for `saved_from_peer`.** `iter_messages(tgt, from_user=src)` returns
  **0** matching forwards, because a forwarded copy in Saved has YOU/the bot as its *sender*,
  not the source peer. There is NO MTProto `messages.search` param for "forwards from peer X".
  Therefore reading `saved_from_msg_id` REQUIRES fetching the message objects. The large
  download is the irreducible cost of a ONE-TIME repair, not of forwarding.
- **Forwarding is id-based, no source download.** `client.forward_messages(tgt, [msg_ids])`
  moves messages by id; the source chat is never downloaded. Batch ~25/call = fast, under
  rate limits.
- **Instant total count (no scan).** `await client.get_messages(chat, limit=0)` → `.total`
  is the full count; or `dialog.message_count` from `iter_dialogs`. Use for progress/verify.
- **Recency-bounded rebuild.** Forwards from a source cluster near arrival; a newest-first
  scan that stops after a cold streak (e.g. 200 consecutive non-matches) turns a 14k download
  into a few-hundred-message window. Use only on a trusted, populated cache (`--quick-rebuild`).

## Duplicate cleanup (after a corrupted run left copies)
Scan target, keep first occurrence of each `saved_from_msg_id`, delete the rest via
`client.delete_messages(tgt, [ids])` chunked (100). Always `--dry-run` first to count.
Telethon does NOT de-dupe native forwards, so copies accumulate from broken runs.

## Session-lock gotcha
Concurrent `tgf` runs (or a killed run leaving a zombie python) hold
`~/.local/share/tg-cli/<session>.session` → "database is locked" on next start.
`ps aux | grep 'tgf forward'`, kill zombies, `rm -f ...session-journal/-wal/-shm`, retry.

## See also
- references/telethon-dedup-truth.md — full repair recipe, command flags, error transcripts.
- The operation skill `devops/tgf-telegram-forwarder-setup` owns setup/build; this skill owns
  the dedup/verification *technique*. If both live, the curator should merge the dedup section
  of that skill into this one (note: that skill is currently not writable from autonomous ctx).
