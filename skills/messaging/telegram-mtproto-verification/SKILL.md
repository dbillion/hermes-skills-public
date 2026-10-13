---
name: telegram-mtproto-verification
description: Telethon forward/verify counts, delivery proof, pitfalls.
---

# telegram-mtproto-verification

Techniques and pitfalls for Telethon MTProto work (message forwarders, chat tools,
delivery verification). Distilled from a real 12,255-message forwarder build where the
local dedup cache reported 8,255 "done" but only 2,910 messages actually landed in
Saved Messages — the job declared success on a lie, and the user rightly rejected it.

## Trigger
Use when: forwarding/copying Telegram messages programmatically; verifying whether
messages actually arrived; counting messages in a chat WITHOUT scanning; or
distributing a Telegram CLI tool via uv/npx.

## Instant message counts (no full scan)
Telethon exposes the server-reported total without iterating a single message:
- `await client.get_messages(chat, limit=0)` returns a `TotalList` whose `.total`
  attribute is the full chat count.
- `dialog.message_count` on each `Dialog` from `client.iter_dialogs()`.
Never iterate all messages just to count — it is slow and rate-limited. This is the
answer to "does Telethon know the total messages in a chat?" — YES, use `.total`.

## Ground-truth delivery verification
A forwarded message in the TARGET carries `m.fwd_from`:
- `fwd_from.saved_from_peer` (e.g. `PeerUser(src_id)`) — points back to the source chat.
- `fwd_from.saved_from_msg_id` — the original message id in that chat.
To verify delivery, scan the TARGET (not the source) and count messages where
`fwd_from.saved_from_peer == PeerUser(src_id)`. Collect `saved_from_msg_id`s into a set
— that set IS the ground truth of what was delivered. Each message has a stable unique
`(chat_id, msg.id)` key; Telegram has no content hash, so use that + `fwd_from` for dedup.

## Pitfall: the cache lies (mark-after-forward-without-verify)
If you `done.add(id)` / write a "forwarded" row the moment `forward_messages()` returns
truthy, you record deliveries that never persisted — especially with deleted-account
peers where `forward_messages` can return a hollow/placeholder result. The cache then
grows while Saved Messages stays empty, and every resume skips those messages forever
(premature "Done"). Two fixes:
1. Before forwarding, REBUILD the dedup cache from ground truth: scan the target, collect
   `saved_from_msg_id`s for `saved_from_peer == src`, overwrite the cache's done-set with
   exactly that. Dedup is then honest.
2. At the end, re-scan the target and PRINT `VERIFIED in target: N / source total: T
   (X%)` — never report the cache's count as proof.
Reference: references/telethon-counting-verification.md — ready-to-copy code for the
instant-count call, the target-scan delivered-set, the rebuild_done_set API, and the
regression test that proves an inflated cache is replaced by truth.

## Deleted-account chat fallback
A chat from a deleted account is NOT resolvable by numeric ID (`resolve_entity(558372819)`
fails). It IS reachable via its cached dialog InputPeer: `client.iter_dialogs()` → find the
`InputPeerUser(id, access_hash)` → use that entity directly. `forward_messages(target,
[msgs])` then works and lands in Saved Messages with correct `fwd_from`.

## Distribution: uv + npx (verified forms)
- uv (pinned, reproducible): `uv tool install "git+https://github.com/<owner>/<repo>.git@v0.1.0"`
  (pin to a tag/SHA, NOT a branch — `@master` drifts).
- uvx one-off (CI): `uvx --from "git+https://github.com/<owner>/<repo>.git@v0.1.0" <cmd> --help`.
- npx skills (install agent skills, NO npm publish): `npx skills add <owner>/<repo> -y`.
  WARNING: older write-ups show `npx skills --skill <repo>/<skill>` — that flag is INVALID
  in the current `skills` CLI (it errors "Unknown command: --skill"). Use `add`.
- npm wrapper: `npx -y <pkg>` that shells out to `uv tool install ...` is a valid alternative.

## Secret hygiene in READMEs / docs
Never commit real channel IDs, user IDs, API hashes, or session names. Use placeholders
(`<SOURCE_CHANNEL>`, `<YOUR_USER_ID>`). The user WILL notice and ask you to scrub them.
Keep `.env` gitignored; before push, `git ls-files` and confirm no `.env`/`.session`/`.db`
is tracked. `gh repo create <n> --public --push --source .` works from this host (the
"git push hangs" assumption was STALE/WRONG — push works fine via gh).

## Verify, don't claim
Mandate from this work: never report "forwarded: N" from a cache or log line. Re-read the
target and report the verified count. A run that printed "cache total: 4711" while only
2,910 landed was a failure of honesty, not just a bug. The logger must distinguish
"this run forwarded" from "cumulative cache rows" and expose the gap.
