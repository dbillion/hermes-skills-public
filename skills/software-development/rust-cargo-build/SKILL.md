---
name: rust-cargo-build
description: "Rust cargo build/check loop and crates.io publish prep."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rust, cargo, rmcp, grammers, crates.io, mcp]
---

# Rust Cargo Build & Publish

Class-level skill for iterating on a Rust binary that talks to Telegram (grammers) and/or exposes
an MCP server (rmcp), ending in a crates.io publish. Pair with `library-api-research` to verify
any API before writing it.

## When to Use
- Building/iterating a Rust CLI or MCP server (especially grammers for Telegram, rmcp for MCP).
- Preparing a crate for crates.io (`cargo publish`), hitting the 10 MB source limit or 400 errors.
- Debugging `E0382` move errors from `&[x]` slice literals, or rmcp/grammers API mismatches.

## Fast compile-error loop
- Use `cargo check` for iterating on errors (full `cargo build` re-emits codegen every time).
  Grep results: `cargo check 2>&1 | grep -A 8 -E "^error"`.
- Slow first compile after a toolchain bump (e.g. rustc 1.93→1.97 for `takecell`): run
  `cargo build` in the **background** with `notify_on_complete`, then `cargo check` is fast.

## Borrow bug to avoid
`&[dst]` where `dst: Peer` (not `Copy`) MOVES `dst` into an array literal, so a second loop
iteration fails with `E0382: use of moved value`. Fix: `std::slice::from_ref(&dst)` returns
`&[Peer]` by borrow without moving. Use it for any `fn targets: &[Peer]` call.

## Verify library APIs via Context7 (mcp-cli) — NEVER guess
The user explicitly corrected this: do NOT invent grammers/rmcp/rusty-tesseract function signatures
from memory. Verify before writing/editing Rust that calls them:
- `mcp-cli call context7/query-docs` on the resolved library id (e.g. `/lonami/grammers`).
  Tools are `resolve-library-id` + `query-docs` (NOT `get-library-docs`). If it throws
  `ERR_MODULE_NOT_FOUND`, clear the stale `~/.npm/_npx/<hash>` dir for `@modelcontextprotocol/server`.
- Or read the cached registry source: `find ~/.cargo/registry/src -maxdepth 1 -type d -name "<crate>-<ver>"`
  then grep the `.rs` files (e.g. `grep -rn -A16 "pub struct Args" "$F/src"`).
Guessing a signature (e.g. `PeerId::self_user()`, `Args` fields) and finding out at compile/test time
wastes a full round-trip. Verify first.

## Stale incremental-cache trap (cargo build reports 0.x s, no recompile)
A real failure mode this session: after editing `src/main.rs`, `cargo build` finished in **0.33s–0.47s
with no recompile**, so the produced binary was STALE — a just-added subcommand reported
`unrecognized subcommand`. `cargo check` also silently reused cache and reported "clean" without
recompiling, so the green check was misleading. Cause: incremental fingerprint got out of sync
(can happen after a `cargo publish --dry-run` build, a toolchain bump, or `touch`/patch churn).

**Fix:** force a real rebuild before trusting any runtime test of new code:
- Fast, scoped: `cargo clean -p <crate>` (drops only that crate's artifacts; deps untouched), then `cargo build`.
- Or: `touch src/main.rs && cargo build`.
Then run the binary and confirm the new behavior (e.g. `--help` shows the new subcommand).
**Rule:** if `cargo build` finishes in <1s after you edited source, the binary is stale — rebuild.

## Optional heavy dependency via feature flag (e.g. Tesseract/OCR)
To make an optional/non-required dependency (so end users don't need it installed to build/run):
```toml
[features]
default = ["ocr"]
ocr = ["dep:rusty-tesseract", "dep:image"]
[dependencies]
rusty-tesseract = { version = "1.1", optional = true }
image = { version = "0.24", optional = true }
```
Then gate EVERY use behind `#[cfg(feature = "ocr")]`:
- the `use rusty_tesseract::...` import (if left ungated, `cargo check --no-default-features` fails
  with `E0432: unresolved import rusty_tesseract`),
- the whole `impl`/struct block,
- the processor registration in `new()` (`#[cfg(feature = "ocr")] processor.add_processor(...)`).
Prove it's gone: `cargo check --no-default-features` compiles with zero OCR deps.
Expose a runtime bypass too (e.g. `--skip-ocr` CLI flag + `skip_ocr` MCP arg) that calls a
`*_skip_ocr` variant so users can opt out per-run even with the feature compiled in.
Verified `rusty_tesseract::Args` fields (v1.1.10, read from registry source
`.../rusty-tesseract-1.1.10/src/tesseract/input.rs`): `lang: String`,
`config_variables: HashMap<String,String>`, `dpi: Option<i32>`, `psm: Option<i32>`, `oem: Option<i32>`.
Defaults: dpi 150, psm 3, oem 3. For cleaner infographic/meme text set `dpi: Some(300)` +
`psm: Some(6)` (uniform block) + `oem: Some(1)` (LSTM only). Put the FULL cleaned
`res.extracted_text` into the message caption (not a 30-char truncation) so forwarded media is
searchable in Saved Messages.
See `references/ocr-engine-eval.md` for the multi-engine comparison method (Kreuzberg vs
Tesseract vs PaddleOCR) and PaddleOCR 3.x environment caveats (ccache + PIR/ONNX backend crash).

## Ship checklist: CLI + MCP parity + npx wrapper
When the user wants a tool "easy for AI to call", the bar is:
1. **Every capability exposed BOTH as a CLI subcommand AND as an MCP tool** (same args/behavior).
   A stub MCP tool (`return "queued"`) is not done — wire it to the real call and verify live.
2. **npx wrapper** so an AI agent can `npx <name>` (downloads the prebuilt binary, supports
   `serve-mcp`). See `references/npx-cross-release.md` for the wrapper + GitHub Actions pattern.
3. **MCP server must list the tool in `list_tools` AND `call_tool` must actually execute it.**
   Test with a real `tools/call` over stdio: send `initialize`, then `notifications/initialized`,
   then `tools/call`; give it a few seconds for the response to flush.
   **Pitfall:** a piped `printf`/`echo` heredoc closes stdin immediately after the last line, so
   rmcp may process `initialize` then exit on EOF before reading `tools/call`. Send
   `notifications/initialized` BETWEEN initialize and tools/call, and keep stdin open (use a
   heredoc + trailing `sleep 3`, or write the JSON lines to a file and `cat file | timeout ...`).
   Also the server's response may not flush to captured stdout before the `timeout`/pipe closes —
   capture to a file (`> /tmp/out.txt 2>&1`) and read it rather than relying on the pipe tail.
   Confirm liveness by checking the captured output shows real side-effect logs (e.g. Tesseract
   firing), not just the `initialize` result.
4. **Monorepo git-root trap (CI workflows only run from the REPO ROOT `.github/`).** If the crate
   lives in a SUBFOLDER of a larger repo (e.g. `gemini-scraper-rs/` inside a `scraper/` monorepo),
   `git rev-parse --show-toplevel` is the PARENT, and GitHub Actions only executes
   `<repo-root>/.github/workflows/*.yml` — NOT a stray `<subfolder>/.github/workflows/*.yml`.
   Editing the subfolder copy makes `git status` look clean and commits "succeed", but the CI run
   keeps using the OLD root workflow (you'll see jobs named `Build and Publish` while your matrix
   never runs). **Always confirm the tracked path first:** `git ls-files | grep workflows`, then
   edit the ROOT-path file, and build steps must use `working-directory: <subfolder>`. Verify after
   commit: `git show HEAD:.github/workflows/release.yml` (NO subfolder prefix) contains YOUR matrix.
   **Tag the release on the RIGHT commit:** `git rev-parse v0.1.0` must equal `git rev-parse HEAD`,
   and that root-path file must contain your matrix (not a stale prototype). A tag on a stale/older
   HEAD makes Actions execute an OLD workflow and fail obscurely. Fix a wrong tag WITHOUT force-push
   (user-preferred, avoids any rewrite): `git push origin --delete v0.1.0` + `git tag -d v0.1.0` +
   `git tag -a v0.1.0 -m ... <correct_commit>` + `git push origin v0.1.0`. (Force-tag-push
   `git tag -f && git push -f` is also safe — only moves a ref — but the user prefers the
   delete-and-recreate route.) Confirm the new run via `gh run list --repo <owner>/<repo> --limit 3`
   shows your workflow name + matrix job names.

## rmcp 0.10 (MCP stdio server) — verified paths
- NO `rmcp::Server` struct. Implement `rmcp::handler::server::ServerHandler` manually
  (`list_tools(RequestContext<RoleServer>) -> ListToolsResult`, `call_tool(...) -> CallToolResult`),
  then `.serve(rmcp::transport::stdio())` via `ServiceExt`.
- `transport::stdio` is gated behind the **`transport-io`** feature: `rmcp = { version="0.10", features=["server","transport-io"] }`.
- `Tool` is `rmcp::model::tool::Tool` with fields `{ name, description, input_schema: Arc<JsonObject> }`.
- `Content::text(String)`; `CallToolResult::success(Vec<Content>)`. `ListToolsResult { tools, next_cursor }`
  (no `meta` field). `request.arguments` is already `Option<Map<String,Value>>` — use directly.

## grammers 0.9 (Telegram MTProto) — verified paths
- `Dialog` is `grammers_client::peer::Dialog`; get the peer with `dialog.peer()` (returns `&Peer`,
  an enum User/Group/Channel). No `dialog.chat()` / `dialog.unread_count()` / `dialog.message_count()`.
- `PeerRef` is `grammers_session::types::PeerRef { id: PeerId, auth }`; `PeerId(i64)` with
  `.bare_id()` and `PeerId::self_user()` (for Saved Messages / "me").
- `client.iter_messages(peer_ref)` takes a `PeerRef` (newest-first by default; `.limit(n)`).
- `client.resolve_peer(PeerRef{..})`, `client.forward_messages(dest, &[id], source)`,
  `client.send_message(peer, text)`.
- `FLOOD_WAIT` errors are handled by the client with backoff — a real run will sleep+retry, not crash.

## crates.io publish prep (avoid the 10 MB limit + 400 errors)
- `.gitignore` MUST exclude `target/` and `temp/` (a build can be 250 MB–2 GB; the crate packages
  git-tracked files, so untracked-but-not-ignored dirs still get included). Also `*.db`, `*.session`,
  `*.log`, `.env`.
- `cargo publish` refuses a dirty tree: only `git add` the intended source/config files, NOT
  stray untracked artifacts (`bota.py`, `errorlogs.md`, `*.log`). Add strays to `.gitignore` so
  they're treated as clean and not packaged.
- `Cargo.toml` needs `description` + `license` (e.g. `license = "MIT"`); `cargo publish --dry-run`
  validates metadata + size before the real upload.
- **Bump `version` in `Cargo.toml` BEFORE `cargo publish` + tagging.** `cargo publish` does NOT
  auto-increment it; whatever is in `Cargo.toml` is what gets published, and the git tag is
  independent. This session hit a real mismatch: the crate published as `v0.1.0` while later tags
  were `v0.1.1`/`v0.1.2` and `Cargo.toml` still said `0.1.0`, making it unclear which artifacts
  carried which README. Fix: edit `version = "X.Y.Z"` to the next semver, commit, then
  `cargo publish`, then `git tag -a vX.Y.Z` and push the tag (triggers the release workflow). Confirm
  `grep '^version' Cargo.toml` equals the tag you intend.
- Auth: `cargo login --token` is NOT valid syntax in current cargo. Use
  `CARGO_REGISTRY_TOKEN=<token> cargo publish` (env only — never write the token into a repo file).
- CRITICAL account rule: crates.io rejects publish with **"A verified email address is required"**
  (HTTP 400) until the token's account has a verified email at crates.io/settings/profile. This is
  an account step the user must do; the code/build is otherwise ready.

## References
See `references/telegram-forwarder-patterns.md` for the forward-vs-copy (restricted channel) design.
See `references/npx-cross-release.md` for the npx wrapper + cross-platform GitHub Actions release pattern.
See `references/ocr-engine-eval.md` for the multi-engine OCR comparison method + PaddleOCR 3.x caveats.
