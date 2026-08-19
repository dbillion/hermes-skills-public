---
name: telegram-mtproto-rust
description: "grammers Rust Telegram client: peers, Saved Messages, COPY."
---

# Telegram MTProto client in Rust (grammers 0.9)

Patterns for building a Telegram forwarder/harvester with `grammers-client` 0.9.x (the high-level
MTProto library). Covers resolving peers, targeting Saved Messages, bypassing forward-locks via a
download→reupload (COPY) fallback, and a cargo build-cache pitfall that cost real time this session.

## When to use
- Building/extending a Rust Telegram tool (forward, harvest, channel enumeration) with grammers.
- `cargo build` says it finished in <1s but the binary is missing your new subcommand (stale cache).
- A channel is forward-locked (`ChatForwardsRestrictedError`) and native `forward_messages` fails.

## CRITICAL: verify the API, do not guess (user requirement)
Use Context7 via mcp-cli, or read the cached crate source — do NOT invent signatures.
- `mcp-cli call context7/query-docs '{"libraryId":"/lonami/grammers","query":"resolve_peer PeerRef self_user iter_messages"}'`
- Cached source: `~/.cargo/registry/src/index.crates.io-*/grammers-client-0.9.0/src/` and `grammers-session-0.9.0/src/`.

## Key API facts (grammers 0.9, verified)
- `Dialog` is `grammers_client::peer::Dialog` (NOT `grammers_client::types::Dialog`). It has only
  `peer()`, `peer_id()`, `peer_ref()`, `last_message()` — NO `chat()`, `unread_count()`, `message_count()`.
- `dialog.peer()` returns `&Peer`, an enum: `Peer::User(_) | Peer::Group(_) | Peer::Channel(_)`.
  - `peer.id()` returns `PeerId`; get the bare i64 via `peer.id().bare_id()`.
  - `peer.name()` -> `Option<&str>`; `peer.username()` -> `Option<&str>`.
  - NO `is_channel()`/`participants_count()` on the `Peer` enum — match the variant instead.
- Resolve a peer from an id: `client.resolve_peer(PeerRef { id: peer_id, auth: Default::default() })`.
  - `PeerRef` is `grammers_session::types::PeerRef` (NOT `grammers_client::types`).
  - For a channel id string, strip a `-100` prefix first, then `PeerId::channel(stripped)`.
- **Saved Messages / "me"**: `client.resolve_peer(PeerRef { id: PeerId::self_user(), auth: Default::default() })`.
  `PeerId::self_user()` is real (grammers-session peer.rs). Map `dest == "me" | "saved" | "self"` to it.
- `iter_messages(peer_ref)` yields newest-first; `.limit(n)` caps it. `peer_ref` is a `PeerRef`.
- Native forward: `client.forward_messages(target_ref, &[msg_id], source_ref).await`.
- Send (the COPY fallback): `client.send_message(peer, text)` / `client.upload_file(path)` then `InputMessage::new().text(c).document(uploaded)`.

## Forward-lock bypass (COPY mode) — the core technique
Native `forward_messages` throws `ChatForwardsRestrictedError` on locked channels. Bypass by
downloading each message's media locally, then re-uploading + sending as a fresh message:
```
for each msg:
    if let Ok(true) = msg.download_media(&path).await { /* OCR optional */ }
    if native forward succeeds -> done (unrestricted path)
    else -> uploaded = client.upload_file(&path).await; client.send_message(target, InputMessage::new().text(c).document(uploaded))
```
This was **live-verified**: forwarding from a locked channel (id 1961116802) to Saved Messages
produced `[DOWNLOAD] -> [OCR] -> [UPLOAD] -> [SUCCESS] Msg N -> Oludayo` with no crash. The fallback
must be the implicit "try native, on Err re-upload" pattern so BOTH restricted and unrestricted
sources work from one code path.

## cargo stale incremental cache (pitfall — cost real time)
Symptom: you edit `src/main.rs`, run `cargo build`, it prints `Finished ... in 0.47s` (no recompile),
and the binary is missing your new subcommand / behaves like the old code. `cargo check` may also
silently reuse the cache and report clean. Fix:
```
touch src/main.rs            # sometimes not enough
cargo clean -p <crate>       # remove only this crate's artifacts (fast, ~5GB but quick)
cargo build                  # now really recompiles (11-21s)
```
Do NOT trust `cargo build` finishing in <1s as "done" when you just changed source. If the subcommand
is unrecognized or behavior is stale, `cargo clean -p <crate>` and rebuild, then re-verify with `--help`.

## Fast iteration
Use `cargo check` to catch type errors quickly (deps already compiled). But remember it shares the
same fingerprint trap above — if `cargo build` then skips recompiling, `cargo check` may also be stale.
When in doubt, `cargo clean -p <crate>` then `cargo build`.

## crates.io publishing notes
- crates.io requires a **verified email** on the publishing account (HTTP 400 otherwise).
- Source must be <10 MB: add `target/` and `temp/` (and runtime `*.db`, `*.session`, `*.log`) to `.gitignore`
  and `git rm --cached` any already-tracked runtime DB before `cargo publish --dry-run`.
- Pass the token via env, never commit it: `CARGO_REGISTRY_TOKEN=<token> cargo publish` (writes to
  `~/.cargo/credentials`, NOT the repo). `cargo login --token` syntax varies by cargo version — prefer the env var.

## See also
- `references/grammers-0.9-api.md` — exact verified symbols and the errors each wrong guess produced.
- Pair with `rust-mcp-server` when exposing these operations as MCP tools.
