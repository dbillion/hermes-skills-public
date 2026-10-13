---
name: rust-mcp-server
description: Rust stdio MCP server with rmcp 0.10, manual ServerHandler.
---

# Rust MCP server (rmcp 0.10)

Build a stdio MCP server in Rust so an agent (e.g. Hermes) can drive your binary. rmcp 0.10's
documented `#[tool]` macro path is fragile across versions; implement `ServerHandler` **manually**
— it is more verbose but compiles deterministically and you control every field.

## When to use
- A Rust CLI must also be agent-controllable over MCP (dual CLI + MCP, like tgforwarder).
- `cargo build` fails on `rmcp::Server`, `rmcp::tool_box`, `rmcp::handler::ServerHandler`, or `transport::stdio::stdio()`.
- The server starts but never answers `tools/call` from a piped test.

## CRITICAL: verify library APIs, do not guess
The user explicitly requires this: **use Context7 (via `mcp-cli`) or read the crate source from the
cargo registry cache** (`~/.cargo/registry/src/<hash>/rmcp-<ver>/src/`) instead of inventing signatures.
- `mcp-cli call context7/query-docs '{"libraryId":"/lonami/grammers","query":"..."}'` for grammers.
- For rmcp, grep the cached source: `grep -rn "pub trait ServerHandler\|pub fn serve\b\|pub use" ~/.cargo/registry/src/*/rmcp-*/src/`.

## Cargo.toml
```toml
[dependencies]
rmcp = { version = "0.10", features = ["server", "transport-io"] }
# transport-io is REQUIRED for the stdio transport. Without it:
#   error[E0433]: cannot find `stdio` in `transport`  (it is gated behind feature "transport-io")
serde_json = "1.0"
```
`rmcp` has **no** `"stdio"` feature — only `"server"` (and you need `"transport-io"` for stdio()).

## Correct module paths (rmcp 0.10) — verified against source
- `ServerHandler` trait: `use rmcp::handler::server::ServerHandler;`  (NOT `rmcp::handler::ServerHandler`)
- Model types: `use rmcp::model::{CallToolResult, Content, ListToolsResult, PaginatedRequestParam, Tool};`
  - `Tool` lives at `rmcp::model::tool::Tool` but is re-exported, so `rmcp::model::Tool` works.
  - `ListToolsResult` has fields `tools` + `next_cursor` only — there is **no `meta` field** (don't add one).
- Transport + serve: `use rmcp::service::{RequestContext, RoleServer, ServiceExt};`
  - stdio transport is a **function**: `rmcp::transport::stdio()`  (NOT `rmcp::transport::stdio::stdio()`).
  - Serve: `svc.serve(rmcp::transport::stdio()).await?` then `.waiting().await?`.

## Manual ServerHandler skeleton
```rust
use rmcp::handler::server::ServerHandler;
use rmcp::model::{CallToolResult, Content, ListToolsResult, PaginatedRequestParam, Tool};
use rmcp::service::{RequestContext, RoleServer, ServiceExt};
use serde_json::json;
use std::sync::Arc;

#[derive(Clone)]
pub struct MyServer { pub scraper: Arc<TelegramScraper>, pub client: Arc<Client> }

fn tool(name: &'static str, description: &'static str, schema: serde_json::Value) -> Tool {
    Tool {
        name: name.into(),
        title: None,
        description: Some(description.into()),
        input_schema: Arc::new(schema.as_object().cloned().unwrap_or_default()),
        output_schema: None,
        annotations: None,
        icons: None,
        meta: None,
    }
}

impl ServerHandler for MyServer {
    async fn list_tools(&self, _req: Option<PaginatedRequestParam>, _ctx: RequestContext<RoleServer>)
        -> Result<ListToolsResult, rmcp::ErrorData> {
        Ok(ListToolsResult { tools: vec![ tool("forward", "Forward messages", json!({...})) ], next_cursor: None })
    }
    async fn call_tool(&self, request: rmcp::model::CallToolRequestParam, _ctx: RequestContext<RoleServer>)
        -> Result<CallToolResult, rmcp::ErrorData> {
        let name = request.name.as_ref();
        let args = request.arguments.unwrap_or_default(); // args is already Option<Map<String,Value>>, NOT Option<Value>
        match name {
            "forward" => { /* do real work; return CallToolResult::success(text_block(...)) */ }
            other => Ok(CallToolResult::error(text_block(format!("unknown tool: {other}")))),
        }
    }
}
```
- `CallToolResult::success(Vec<Content>)` and `CallToolResult::error(Vec<Content>)` both exist.
- `Content::text(String)` and `String: IntoContents` — build content with `vec![Content::text(s)]`.
- `request.arguments` is `Option<serde_json::Map<String, Value>>` (already a map). Do NOT wrap it in
  another `match v { Value::Object(_) => ... }` — that was a wrong guess that failed to compile.
- To return errors without guessing `ErrorData` constructors, prefer `CallToolResult::error(text_block(...))`
  over `rmcp::ErrorData::internal_error(...)` (the latter's signature varies by version).

## Entry point
```rust
pub async fn serve(scraper: Arc<TelegramScraper>, client: Arc<Client>) -> anyhow::Result<()> {
    let svc = MyServer { scraper, client };
    let running = svc.serve(rmcp::transport::stdio()).await.map_err(|e| anyhow::anyhow!(e.to_string()))?;
    running.waiting().await.map_err(|e| anyhow::anyhow!(e.to_string()))?;
    Ok(())
}
```

## Smoke-testing over stdio (no client needed)
Piping JSON-RPC to the binary is unreliable unless you send the `initialized` notification AND keep
stdin open long enough for the response to flush. Use a group with a trailing sleep, capture to a file:
```bash
{
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'
  echo '{"jsonrpc":"2.0","method":"notifications/initialized"}'
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"forward","arguments":{"source":"123","dest":"me","limit":2}}}'
  sleep 3
} | timeout 120 ./target/debug/mybin serve-mcp > /tmp/mcp_out.txt 2>&1
```
Pitfalls observed:
- Without `notifications/initialized`, rmcp answers `initialize` then drops `tools/call` and exits on EOF.
- If the tool does slow work (e.g. OCR, network), the `sleep 3` may be too short and you'll only see the
  `initialize` response + side-effect logs (e.g. a Tesseract command line). Side-effect logs prove the tool
  RAN even when the JSON result hasn't flushed — trust them.
- To prove a `forward` tool is real (not a stub), grep the captured file for the tool's side-effect logs
  (download/OCR/upload lines), not just the JSON result.

## See also
- `references/rmcp-0.10-api.md` — exact verified symbols and the errors each wrong guess produced.
- Pair with `telegram-mtproto-rust` when the MCP tools drive a grammers Telegram client.
