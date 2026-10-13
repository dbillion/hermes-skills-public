# rmcp 0.10 — verified API facts (from cargo registry source)

Grep location: `~/.cargo/registry/src/index.crates.io-*/rmcp-0.10.0/src/`

## Module paths (what compiled)
- `use rmcp::handler::server::ServerHandler;`   (trait) — NOT `rmcp::handler::ServerHandler`
- `use rmcp::model::{CallToolResult, Content, ListToolsResult, PaginatedRequestParam, Tool};`
- `use rmcp::service::{RequestContext, RoleServer, ServiceExt};`
- stdio transport: `rmcp::transport::stdio()`  (a function; requires Cargo feature `"transport-io"`)
  - Without `transport-io`: `error[E0433]: cannot find 'stdio' in 'transport'`
- Serve: `svc.serve(rmcp::transport::stdio()).await?` then `.waiting().await?`

## `Tool` struct fields (model/tool.rs)
```rust
pub struct Tool {
    pub name: String,
    pub title: Option<String>,
    pub description: Option<String>,
    pub input_schema: Option<serde_json::Value>,   // actual type: Option<Arc<JsonObject>>
    pub output_schema: Option<serde_json::Value>,
    pub annotations: Option<...>,
    pub icons: Option<...>,
    pub meta: Option<...>,   // NOTE: ListToolsResult has NO meta field
}
```
When building manually:
```rust
Tool { name: name.into(), title: None, description: Some(d.into()),
       input_schema: Arc::new(schema.as_object().cloned().unwrap_or_default()),
       output_schema: None, annotations: None, icons: None, meta: None }
```

## `ListToolsResult` (model)
- Fields: `tools: Vec<Tool>`, `next_cursor: Option<...>`. **No `meta` field.**
- Wrong: adding `meta: None` to `ListToolsResult` → `error[E0433]: cannot find 'meta' in this scope`.

## `ServerHandler` trait methods (handler/server.rs)
```rust
async fn list_tools(&self, _request: Option<PaginatedRequestParam>, _context: RequestContext<RoleServer>)
    -> Result<ListToolsResult, ErrorData>;
async fn call_tool(&self, request: CallToolRequestParam, _context: RequestContext<RoleServer>)
    -> Result<CallToolResult, ErrorData>;
```
- `CallToolResult::success(Vec<Content>)` and `CallToolResult::error(Vec<Content>)` both exist.
- `Content::text(String)` exists; `String: IntoContents`.

## `call_tool` request
- `request.name: Cow<str>` (use `request.name.as_ref()`).
- `request.arguments: Option<serde_json::Map<String, Value>>` (already a Map — NOT `Option<Value>`).
  - Wrong guess that failed: `request.arguments.map(|v| match v { Value::Object(m) => m, _ => ... })`
    → "mismatched types: expected Option<Map>, found Option<Value>".

## Feature gates
- `rmcp = { features = ["server", "transport-io"] }`
- There is NO `"stdio"` feature. `transport-io` enables `rmcp::transport::stdio`.

## Session errors → fixes (this project)
| Error | Cause | Fix |
|-------|-------|-----|
| `unresolved import rmcp::Server` | no such struct | use `serve(...)` / `ServiceExt`, not `rmcp::Server` |
| `unresolved import rmcp::tool_box` | macro path wrong | implement `ServerHandler` manually, drop macros |
| `unresolved import rmcp::handler::ServerHandler` | wrong module | `rmcp::handler::server::ServerHandler` |
| `cannot find stdio in transport` | missing feature | add `"transport-io"`; call `rmcp::transport::stdio()` |
| `cannot find type ServerResult` | not in `rmcp::model` | remove import |
| `cannot find RequestContext in model` | wrong module | `rmcp::service::RequestContext` |
| `ListToolsResult ... no meta` | phantom field | drop `meta` |
