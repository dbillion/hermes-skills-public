# Rust: grammers (MTProto) + rmcp 0.10 (MCP) — verified API + version pins

## Version pins (from build errors this session)
- `grammers-client = "0.9.0"` (pinned). Latest `grammers` branch is archived, but
  0.9.0 builds fine on rustc 1.97.
- `telers` latest = `1.0.0-beta.8` and needs **rustc >= 1.96** (transitive
  `takecell@0.1.2` requires 1.96). If you see
  "rustc X not supported by takecell@0.1.2": `rustup update stable` → gets 1.97.
- `rmcp = { version = "0.10", features = ["server"] }`. There is NO `stdio`
  feature. `server` is correct.

## rmcp 0.10 server API (read from registry source — authoritative)
```rust
use rmcp::handler::server::tool_box::ToolBox;
use rmcp::model::*;
use rmcp::service::RoleServer;
use rmcp::tool;          // rmcp_macros::tool re-exported
use rmcp::ServerHandler;
use rmcp::{Server, ServiceExt};

#[derive(Clone)]
struct Handler { /* state */ }

#[tool(tool_box)]
impl Handler {
    #[tool(description = "...")]
    async fn channels(&self, #[tool(param)] args: ChannelsArgs)
        -> Result<CallToolResult, rmcp::ErrorData>
    {
        Ok(CallToolResult::success(vec![Content::text("...".into())]))
    }
}

#[tool_handler]
impl ServerHandler for Handler {}

// Entry:
let server = Server::builder().serve(rmcp::transport::stdio::stdio()).await?;
let running = server.serve(handler).await?;   // server is RunningService
running.waiting().await?;
```
- `rmcp::transport::stdio::stdio()` returns `(Stdin, Stdout)`.
- `Server::builder().serve(transport)` then `.serve(handler)` → `RunningService`;
  call `.waiting().await`.
- `CallToolResult::success(vec![Content::text(s.into())])`.
- Tool args are deserialized from `CallToolRequestParam.arguments` via a
  `#[derive(Deserialize)]` struct; mark each param with `#[tool(param)]`.

## grammers 0.9 client usage (from existing gemini-scraper-rs)
- `TelegramScraper::new(api_id, session, history_cache, last_id_cache, min_id_cache, direction_cache, history_tx)`
- `scraper.resolve_channel(name)` → `Peer`
- `scraper.scrape_history(&src, &[targets], mode)` where `mode: ScrapeMode`
  (`OldestToLatest`, `ResumeOldestToLatest`, `LatestToOldest`, `ResumeLatestToOldest`)
- `scraper.forward_message(source_id, &targets, &msg)` → `Result<bool>`
- `client.iter_messages(peer_ref)` yields messages; `.limit(n)` / `.offset_id(n)`.
- Forward lock (ChatForwardsRestrictedError) → must download + re-upload (copy mode).

## Build note
First `cargo build` with grammers+rmcp takes ~9 min. Run in background
(`notify_on_complete=true`) and fix errors from output. Use `cargo fetch` first to
pull deps, then read `~/.cargo/registry/src/<hash>/<crate>-<ver>/src/` to verify
any API you are unsure of (no network needed).
