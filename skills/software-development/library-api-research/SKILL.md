---
name: library-api-research
description: "Verify crate/library APIs from docs, not memory."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rust, api, context7, mcp, research, verification]
---

# Library API Research — verify, don't guess

**Trigger:** You are about to write or fix code that calls a third-party library (crate, npm
package, Python SDK) and you are not 100% certain of an exact signature, module path, struct
field, trait name, or feature flag. Stop and verify — do NOT recall it from memory.

**User correction this encodes:** "did you use mcp-cli for context 7 mcp so you dont gues
functions" — guessing library APIs produced 10+ compile errors in one Rust session. Verifying
first avoids the whole loop.

## Method A — Context7 via mcp-cli (preferred when connected)

Context7 is an MCP server that returns version-pinned library docs. Invoke it with `mcp-cli`.

1. Resolve the canonical library id (fuzzy name → id):
   ```bash
   echo '{"libraryName":"grammers","query":"telegram mtproto client rust"}' \
     | mcp-cli call context7/resolve-library-id
   # -> /lonami/grammers
   ```
2. Pull docs for the exact symbols you need:
   ```bash
   echo '{"libraryId":"/lonami/grammers","query":"resolve_peer PeerRef iter_messages self_user saved messages","tokens":6000}' \
     | mcp-cli call context7/query-docs
   ```

**Traps:**
- The docs tool is `query-docs`. `get-library-docs` does NOT exist (`TOOL_NOT_FOUND`). Only
  `resolve-library-id` and `query-docs` exist.
- Broken npx cache: if `mcp-cli call context7/...` fails with
  `ERR_MODULE_NOT_FOUND ... @modelcontextprotocol/server` / `mcp-remote`, clear the stale npx
  cache: `rm -rf ~/.npm/_npx/<hash>` (hash from the error path), then `mcp-cli info context7`.
- Pipe-to-interpreter may be blocked; write JSON to a temp file then parse, or use
  `echo '...' | mcp-cli call ... -` where stdin mode is supported.

## Method B — read crate source from the cargo registry cache (always available offline)

For Rust, the authoritative source is already on disk after any `cargo build`/`cargo fetch`:
```
~/.cargo/registry/src/<index-hash>/<crate>-<version>/
```
Grep for the real symbol rather than guessing:
- `rmcp::Server`? — grep shows there is NO `Server` struct; serve via `rmcp::service::serve_server`
  or `ServerHandler` impl + `ServiceExt::serve`, transport `rmcp::transport::stdio()` (gated
  behind `transport-io` feature).
- `grammers_client::types::Dialog`? — grep: `Dialog` is at `grammers_client::peer::Dialog`;
  `PeerRef` is at `grammers_session::types::PeerRef`; `iter_messages` takes a `PeerRef`.
- `Tool` / `Content` / `CallToolResult` constructors — read `rmcp/src/model/tool.rs`,
  `content.rs` to get exact fields (e.g. `Tool { name, description, input_schema: Arc<JsonObject> }`,
  `Content::text(String)`, `CallToolResult::success(Vec<Content>)`).

## When to use which
- Context7 connected → Method A (cleanest, version-aware, no local path soup).
- Context7 absent → Method B (registry source is equally authoritative and faster than guessing).
- Either way: after the compile, run `cargo check` (not full `cargo build`) for fast error
  iteration — see the `rust-cargo-build` skill.

## Pair with
- `rust-cargo-build` (cargo check fast loop, rmcp/grammers API notes, crates.io publish prep).
