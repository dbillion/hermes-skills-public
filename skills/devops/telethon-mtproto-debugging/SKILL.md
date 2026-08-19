---
name: telethon-mtproto-debugging
description: tgf VERIFIED=0 or dedup fails? Telethon peer-type match bug.
---

# Telethon / MTProto Forwarder Debugging

Use when building or fixing a Telegram MTProto forwarder (any descendant of the
tgf / tg-cli / telbot family: native `forward_messages`, COPY-mode re-post,
dedup cache, ground-truth rebuild, `dedupe` cleanup). The single most common,
silent, hard-to-spot bug class is **peer-type mismatches when matching forwarded
messages** — captured below with a regression test pattern.

## Trigger
- "tgf is re-forwarding everything / not deduping"
- "VERIFIED count is always 0 / n/a"
- "dedupe finds no duplicates but I know there are copies"
- "cache keeps getting wiped on --rebuild-cache"
- Any code that compares a message's `fwd_from.saved_from_peer` to a hardcoded
  `PeerUser(...)` or `PeerChat(...)`.

## The core gotcha: saved_from_peer type follows the SOURCE type
When Telegram forwards a message, the copy's `Message.fwd_from.saved_from_peer`
is typed by what the ORIGINAL sender was:
- forwarded FROM a **channel**  → `PeerChannel(channel_id)`  (note: `channel_id` is
  the bare id WITHOUT the `-100` prefix)
- forwarded FROM a **user**     → `PeerUser(user_id)`
- forwarded FROM a **chat/group** → `PeerChat(chat_id)` (legacy) or `PeerChannel` for
  megagroups/supergroups.

So if SOURCE_CHANNELS is a channel like `-1001961116802`, Telegram stores the
forward as `PeerChannel(1961116802)`. A check like:

```python
if fwd and fwd.saved_from_peer == PeerUser(src.id):   # BUG
```

is **always False** for channel sources, because `PeerChannel(...) != PeerUser(...)`.
The symptom is not a crash — it is silent data corruption:
- ground-truth rebuild returns an empty set → `rebuild_done_set` deletes the real
  cache → every run re-forwards the whole source;
- final verification counts 0;
- `dedupe` never matches.

It works fine for a *user* source (PeerUser == PeerUser), which is why the bug
ships untested.

## The fix
Match against the **correctly-typed** peer derived from the source id, never a
hardcoded type:

```python
from telethon import utils

def _is_from_source(fwd, src_id: int) -> bool:
    return bool(fwd and getattr(fwd, "saved_from_peer", None) == utils.get_peer(src_id))
```

`utils.get_peer(-1001961116802)` → `PeerChannel(channel_id=1961116802)`, which
compares equal to the stored `fwd_from.saved_from_peer`. This is correct for
channel, user, and chat sources alike. Route ALL match sites through this helper
(scan, rebuild, final verification, dedupe).

## Regression test pattern (offline, no network)
Add a unit test that builds `MessageFwdHeader` objects for both a channel and a
user source and asserts `_is_from_source` matches the right type and rejects the
wrong one. No Telegram session or network required — `MessageFwdHeader` needs a
`date` kwarg. See `references/peer_matching_gotcha.md` for the exact recipe that
reproduced the tgf bug.

## Other MTProto forwarder gotchas to keep in mind
- **Ghost forwards**: `forward_messages` can return a truthy result for a message
  that never persisted (common with deleted-account peers). Always RE-READ the
  target (`client.get_messages(target, ids=...)`) and only mark `done` for ids that
  survive verification; release the reservation otherwise so it retries next run.
- **Per-target dedup**: each target must end up a complete copy, so track a done
  SET PER TARGET, not one global set. A message is "done" only if present in EVERY
  target.
- **COPY mode** (protected chats that block forwarding): no `saved_from_peer`
  exists, so dedup by `content_hash` (text + media name/size/type), and
  download→upload→delete in batches to keep the disk footprint flat at scale.
- **Cache inflation**: the cache can be inflated by false "done" marks; rebuild
  from ground truth before treating the cache as authoritative.
- **min_id vs truthful done set**: when rebuilding from ground truth, do NOT also
  filter by `min_id` — a lower-id message that was never actually delivered would
  be wrongly excluded.
