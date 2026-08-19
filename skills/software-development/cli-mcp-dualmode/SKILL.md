---
name: cli-mcp-dualmode
description: Build CLI-MCP dual-mode agent-driven tools.
version: 1
author: hermes
license: MIT
metadata:
  hermes:
    tags: [mcp, cli, rust, python, telegram, agent-tooling, dual-mode]
    related_skills: [software-development/angular-developer, devops/golang-track]
---

# Dual-Mode CLI + MCP Tooling (agent-controllable)

## When to Use
- User asks for a tool "as both a cli and an mcp", "agent-controllable", or wants an
  agent (Hermes/Claude) to drive a Telegram/forwarder/scraper.
- Building or extending `tgforwarder`, `gemini-scraper-rs`, or any CLI that should
  also be reachable as MCP tools over stdio.
- Rate-limit-aware Telegram forwarding (FloodWait) is in scope.

Build a tool so it runs as a normal CLI **and** exposes the same operations as MCP
tools over stdio. This lets an agent (Hermes, Claude, etc.) drive it. The user
explicitly wants this pattern for Telegram forwarding tooling; it generalizes to
any agent-drivable CLI.

## Core contract
1. **One implementation, two fronts.** The CLI subcommand and the MCP tool must
   call the *same* async function. Never fork logic.
2. **Deliver BOTH when asked.** If the user says "both a cli and an mcp", shipping
   CLI-only is a miss — they will call it out. Same for rate-limiting: if Telegram
   is involved, FloodWait handling is part of the deliverable, not optional.
3. **Check for an existing project FIRST.** Before scaffolding a new repo, search
   the user's workspace (sibling dirs, `~/Documents/*/`, known project roots) for
   an existing implementation. Scaffolding a duplicate `tgforwarder-rs` next to an
   existing `gemini-scraper-rs` wasted a build. Prefer extending the existing repo.
4. **Rate-limit discipline.** Telegram returns `FloodWaitError` / `RpcError
   FLOOD_WAIT_X`. Honor the `.seconds` hint (sleep that window) — do NOT blind-retry.

## Python path (mcp SDK >= 2.0)
The `mcp` PyPI SDK is at **2.0.0** — its API differs from 1.x. Verified working:
- Install into the project venv with `uv pip install "mcp"` (the venv has no pip;
  `python -m pip` fails under PEP 668).
- Server uses **callback constructor**, not decorators:
  `Server("name", on_list_tools=fn, on_call_tool=fn)` where handlers return
  `ListToolsResult` / `CallToolResult` (from `mcp.types`).
- `stdio_server()` in 2.0 returns a **tuple** `(read, write)`, NOT an async context
  manager. Run: `read, write = await stdio_server()` then
  `await server.run(read, write, server.create_initialization_options())`.
- Smoke test over stdio: pipe `initialize` → `notifications/initialized` →
  `tools/list` JSON-RPC lines; assert the tool list echoes back.
- See `references/python-mcp-2.0.md`.

## Rust path (grammers + rmcp)
- **MTProto lib:** use `grammers = "0.9.0"` (pinned, builds fine). `grammers` latest
  branch is archived but 0.9.0 is stable. `telers` latest is `1.0.0-beta.8` and
  needs **rustc >= 1.96** (a transitive dep `takecell` requires 1.96) — if you hit
  "rustc X not supported by takecell@0.1.2", run `rustup update stable` (gets 1.97+).
- **MCP SDK:** `rmcp = { version = "0.10", features = ["server", "transport-io"] }`.
  `transport-io` is REQUIRED for `rmcp::transport::stdio()` (without it: "could not
  find `stdio` in `transport`"). CORRECTION (this session): the `#[tool(...)]`
  macro + `#[tool_handler]` approach does NOT compile on rmcp 0.10 — use a manual
  `ServerHandler` trait impl instead:
  - `rmcp::handler::server::ServerHandler` (NOT `rmcp::handler::ServerHandler`);
    `rmcp::Server` (struct) does not exist.
  - `Tool` is `rmcp::model::Tool`; `ListToolsResult` has NO `meta` field.
  - `request.arguments` is `Option<serde_json::Map<String,Value>>` — use directly.
  - Entry: `svc.serve(rmcp::transport::stdio()).await?.waiting().await?`.
  - See `references/rust-rmcp-grammers.md` for the full verified skeleton.
- First build is SLOW (~9 min for grammers+rmcp). Kick it off in the background
  with `notify_on_complete=true`; fix errors from its output.
- See `references/rust-rmcp-grammers.md`.

## Resolving crate versions WITHOUT Context7 / web search
Context7 may not be connected — but it CAN be reached via `mcp-cli` if its npx
cache is healthy:
- `mcp-cli info context7` lists `resolve-library-id` + `get-library-docs`.
- If it errors with `ERR_MODULE_NOT_FOUND: ...@modelcontextprotocol/server/dist/index.mjs`,
  that's a **stale npx cache** — fix with `rm -rf ~/.npm/_npx/<hash>` then retry
  `mcp-cli info context7`. After that it works (verified this session: confirmed
  `grammers` is a high-reputation lib, validating the 0.9.0 pin).
- Reliable fallbacks when even mcp-cli Context7 is down (all verified this session):
  - **Version pins:** let `cargo build` fail — it prints exact candidate versions.
  - **Feature-name errors:** cargo prints `package X does not have feature Y`.
  - **API verification:** read the compiled crate source from the cargo registry
    cache: `~/.cargo/registry/src/<hash>/<crate>-<ver>/src/`. Use `search_files` for
    `pub fn`, `trait`, `macro_rules!`. Authoritative, no network. (Equivalent to a
    Context7 lookup — this is what actually unblocked the rmcp 0.10 API this session.)
- Do NOT `curl crates.io` — outbound curl is blocked without consent.

## FAST iteration (user directive this session)
- Rust builds of grammers+rmcp are ~9 min first time. **Use `cargo check` after
  every edit** to catch type/API errors in seconds; do ONE `cargo build` only when
  you need the binary. User: "use cargo check to quickly catch errors, this makes
  your work fast, with less guessing."

## Verification checklist
- [ ] CLI subcommand runs non-interactively (reads from env/args, no `prompt()`).
- [ ] MCP `tools/list` returns every operation the CLI exposes.
- [ ] A `call_tool` smoke test (e.g. `channels`) returns structured output.
- [ ] FloodWait path sleeps instead of crashing on rate-limit.
- [ ] For Rust: `cargo build` green; for Python: `pytest` + MCP stdio smoke green.
- [ ] Each logical change committed separately (user expects per-edit commits).

## crates.io publish (gated)
- Source packages capped at **10 MB**; exclude `target/`, `temp/`, `*.db`,
  `*.session`, `*.db-shm`, `*.db-wal` via `.gitignore`/`exclude`. Also untrack any
  already-committed runtime DB (`git rm --cached gemini_scraper.db`).
- Requires the user's crates.io token. User gave it this session with the explicit
  rule: **"ensure you dont add it to the git commit"** → use the env var, never a
  file in the repo:
  `CARGO_REGISTRY_TOKEN="<token>" cargo publish`.
  - `cargo login --token <tok>` is NOT valid syntax in current cargo; `cargo login`
    prompts interactively. The env-var form is the non-interactive path and writes
    nothing into the repo (token lands in `~/.cargo/credentials`, outside the tree).
  - Verify with `git status` that no `credentials`/`token` file is staged.
- `cargo publish` refuses a **dirty git tree**: every untracked/modified file
  blocks it (even `*.log`, `bota.py`, `.env.temp`). Before publishing, either
  commit intended changes or add strays to `.gitignore` (gitignored files are
  treated as clean AND not packaged). Do NOT use `--allow-dirty` (it packages the
  strays, blowing the size limit / leaking).
- **Verified-email required**: crates.io rejects the upload with HTTP 400
  "A verified email address is required to publish crates" even when the token is
  valid. The fix is on the crates.io account (Settings → Profile → add + verify
  email), not the code. After that, re-run publish.
- `cargo publish --dry-run` builds + packages + validates metadata/size WITHOUT
  uploading — run it first.
- Confirm the crate name with the user (e.g. `gemini-scraper-rs` vs `tgforwarder-rs`);
  first publish of a name is permanent.
- See `references/cratesio-publish.md`.
