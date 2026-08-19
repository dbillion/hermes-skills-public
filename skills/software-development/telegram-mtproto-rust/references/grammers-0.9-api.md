# grammers 0.9 — verified API facts (from cargo registry source)

Source: `~/.cargo/registry/src/index.crates.io-*/grammers-client-0.9.0/src/` and `grammers-session-0.9.0/src/`

## `Dialog` (peer/dialog.rs)
- Path: `grammers_client::peer::Dialog`  (NOT `grammers_client::types::Dialog`)
- Methods: `peer() -> &Peer`, `peer_id() -> PeerId`, `peer_ref() -> PeerRef`, `last_message() -> Option<&Message>`.
- NO `chat()`, `unread_count()`, `message_count()`. Use `peer()` then `Peer` methods.

## `Peer` (peer/mod.rs) — an enum
- `Peer::User(user)`, `Peer::Group(group)`, `Peer::Channel(channel)`.
- `id() -> PeerId`; bare i64 via `id().bare_id()`.
- `name() -> Option<&str>`, `username() -> Option<&str>`.
- NO `is_channel()` / `participants_count()` on the enum. Match the variant; `Channel::participants_count()`
  exists on the `Channel` variant only.

## Resolving peers (client.rs / session peer.rs)
- `client.resolve_peer(PeerRef { id: peer_id, auth: Default::default() }) -> Result<Peer>`
- `PeerRef` is `grammers_session::types::PeerRef` (NOT `grammers_client::types`).
- Resolve by numeric id: strip `-100` prefix, then `PeerId::channel(stripped)`.
- **Saved Messages / "me"**: `PeerRef { id: PeerId::self_user(), auth: Default::default() }`.
  `PeerId::self_user()` is real (grammers-session peer.rs:165).
- `PeerId(i64)`; `bare_id() -> i64`; `PeerId::channel(id)`, `PeerId::user(id)`, `PeerId::chat(id)` return `Option<PeerId>`.

## Messages
- `client.iter_messages(peer_ref)` — `peer_ref: PeerRef`; yields newest-first. `.limit(n)` caps.
- `msg.download_media(&path) -> Result<bool>` (true if downloaded).
- `msg.id() -> i32`, `msg.text() -> &str`, `msg.media() -> Option<&Media>`, `msg.peer() -> Option<Peer>`, `msg.sender() -> Option<&User>`, `msg.fmt_entities()`.
- Native forward: `client.forward_messages(target_ref, &[msg_id], source_ref) -> Result<Vec<Option<Message>>>`.
- `client.send_message(peer, text)`, `client.upload_file(&path) -> Result<Uploaded>`, `InputMessage::new().text(c).document(uploaded)`.

## Borrow pitfall (cost a compile error)
`&[dst]` where `dst: Peer` MOVES `dst` into the array literal (Peer is not Copy), so the next loop
iteration fails with `error[E0382]: use of moved value: dst`.
Fix: `client.forward_message(source_id, std::slice::from_ref(&dst), &msg)` — borrows without moving.

## Session errors → fixes (this project)
| Error | Cause | Fix |
|-------|-------|-----|
| `unresolved import grammers_client::types` | wrong module | `grammers_client::peer::Dialog`; `grammers_session::types::PeerRef` |
| `no method chat/unread_count/message_count` on Dialog | API mismatch | use `dialog.peer()` then `Peer` methods |
| `no method named resolve_peer_by_id` | not a method | `client.resolve_peer(PeerRef { id, auth })` |
| `cannot find type PeerRef` | wrong import | `grammers_session::types::PeerRef` |
| `use of moved value: dst` | `&[dst]` moves | `std::slice::from_ref(&dst)` |
| `sender.id()` expected i64, found PeerId | type mismatch | `sender.id().bare_id()` |
