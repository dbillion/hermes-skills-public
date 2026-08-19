---
name: nestjs-neon-agentic
description: Build/debug a NestJS 11 API wired to Neon Postgres (PostGIS + pgvector + pg_graphql) with Mastra agents exposed via the AG-UI protocol. Covers the ks-knowledge-sharing stack (NestJS + Angular 20 Material 3). Use when connecting a NestJS backend to Neon, adding semantic search (pgvector), geospatial (PostGIS), knowledge-graph (pg_graphql), or agentic workflows (Mastra + CopilotKit/AG-UI) — and when debugging TypeORM column mismatches, pgvector ORDER BY returning 0 rows, or agent SSE endpoints.
---

# NestJS + Neon Postgres + Agentic (Mastra/AG-UI)

Class-level skill for the ks-knowledge-sharing backend: a NestJS 11 API on Neon
Postgres 17 with `postgis`, `vector`, `pg_graphql` extensions, plus Mastra agents
streamed over the AG-UI protocol.

## Environment facts (this project)
- Repo: `~/ks-knowledge-sharing` (branch `master`). API: `knowledge-sharing-api`,
  frontend: `knowledge-sharing-app` (Angular 20, Material 3, dark theme — user loves it).
- Neon project id: `weathered-forest-50229673`. MCP command (works):
  `mcp-cli -c ~/.config/mcp-cli/mcp_servers.json call neon run_sql '{"params":{"projectId":"weathered-forest-50229673","sql":"<q>"}}'`
  - Returns `[]` for BOTH success and silent failure — never trust a silent `[]`;
    re-query `information_schema` to confirm DDL actually landed. Run DDL ONE
    statement per call (loops that batch multiple statements silently drop some).
- DB creds in `knowledge-sharing-api/.env` (gitignored). Never hardcode. Loaded via
  `import 'dotenv/config'` at top of `database.config.ts` BEFORE the config function
  evaluates (else `DATABASE_URL` reads undefined at module-eval time).
- Extensions enabled: `postgis`, `postgis_topology`, `vector`, `pg_graphql`.
- **`pg_search` and `pg_bm25` (ParadeDB BM25) are DEPRECATED and BLOCKED on Neon** —
  `CREATE EXTENSION pg_search` / `pg_bm25` returns `NeonDbError: extension "pg_search"
  is deprecated and no longer allowed`. Do NOT try them. For BM25-style keyword
  search use NATIVE Postgres FTS (`tsvector` + GIN index + `ts_rank`), which is
  always available and works. See the "Hybrid / BM25 search" section below.
- **Git push is expected by default for this repo.** Commit a tested backend state
  AND `git push` to `origin master` unless the user explicitly says hold. The user
  was surprised a committed state was left unpushed. (Deploying live is a SEPARATE
  action that still needs explicit ask — "commit + push" ≠ "deploy".)
- **Stale "LSP" red squiggles in this CLI harness are PHANTOM.** No `tsserver`
  process runs in this environment (verify with `ps aux | grep -E
  'tsserver|vtsls'`). The inline TS linter sometimes reports against a cached
  pre-edit file version. `npx tsc --noEmit` (exit 0) is the authoritative check;
  `touch` the file to force a re-read. Never block on the overlay.

## Wiring NestJS to Neon (verified path)
1. `database.config.ts`: `type: 'postgres'`, `url: process.env.DATABASE_URL`,
   `synchronize: false` (schema is source-of-truth via `db/schema.sql`, applied
   through the MCP — auto-sync throws FK errors on `graph_edges`). Add
   `namingStrategy: new SnakeNamingStrategy()` — see Pitfalls.
2. `entities` glob MUST be scoped: `['**/modules/**/*.entity{.ts,.js}']`. The repo
   ships broken skeleton entities under `database/entities/**` (e.g. `Attachment`
   with no `@Column` type → `DataTypeNotSupportedError: "Object"`). A broad
   `src/**/*.entity` glob pulls them in and breaks metadata validation.
3. `npm i pg` (driver). `node dist/main.js` (not `nest start`) for fast restart;
   kill the stale :3000 listener by PID (`ss -ltnp | grep :3000`) — do NOT `pkill
   -f dist/main.js`, it signals the shell and aborts the command.

## Mastra + AG-UI agent layer (verified)
- Install: `npm i @mastra/core @ag-ui/mastra @ag-ui/core`. In this Mastra version
  the exports are split: `Mastra` from `@mastra/core`, `Agent` from
  `@mastra/core/agent`, `createTool` from `@mastra/core/tools`. `Agent` config
  REQUIRES an `id` field (not just `name`).
- Define agents with Neon-backed tools (ragSearch via pgvector, nearbyFeatures via
  PostGIS, graphNeighbours via graph). See `references/mastra-agents.md`.
- Expose as AG-UI SSE: `POST /api/agents/:name/run` streaming
  `RUN_STARTED → TEXT_MESSAGE_START → TEXT_MESSAGE_CONTENT → TEXT_MESSAGE_END →
  RUN_FINISHED`. This IS the CopilotKit/AG-UI protocol — Angular consumes it via
  `@ag-ui/client` RuntimeClient, no React needed. (Full CopilotKit `/copilotkit`
  handler via `@ag-ui/mastra/copilotkit` `registerCopilotKit` is also available.)
- LLM creds: Hermes already has `OPENROUTER_API_KEY` in `~/.hermes/.env`. Copy it
  into the API `.env` as BOTH `OPENAI_API_KEY` and `OPENROUTER_API_KEY`, plus
  `OPENAI_BASE_URL=https://openrouter.ai/api/v1` (OpenRouter is OpenAI-compatible,
  so Mastra's `openai` provider just works). Model: `openai/gpt-4o-mini`.
  Pull the value from `~/.hermes/.env` at write time; never echo the secret.

## Clerk auth (Angular + NestJS) — partial, keyless blocker
The Clerk *skill* is React/Next-oriented and has no Angular/NestJS path. For this
stack the intended integration is:
- **Angular**: `@clerk/clerk-angular` `ClerkProvider` (publishable key from env) for
  sign-in UI; read the session JWT and send as `Authorization: Bearer`.
- **Nest**: verify the Clerk JWT via `@clerk/backend` `verifyToken` (JWKS, using
  `CLERK_SECRET_KEY` + issuer). Alternatively keep Nest's OWN JWT (JwtModule +
  JwtStrategy already present) and use Clerk only for UI gating.
- **BLOCKER this session**: the Clerk CLI is not installed and no Clerk keys exist
  in the environment (`CLERK_SECRET_KEY`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` all
  empty). Cannot provision an app or issue real Clerk JWTs without keys. Write the
  integration code with env placeholders and ask the user for keys; do not claim
  Clerk auth works until keys are supplied and `clerk login`/`clerk env pull` runs.
- Meanwhile the Nest auth controller is STUBBED (returns `mock-jwt-token`). The
  AuthModule already wires JwtModule + JwtStrategy but points `User` at the broken
  `database/entities/user.entity`; repoint to `modules/users/user.entity.ts` and
  implement login/register (bcrypt + real entity) for a functional non-Clerk path.

## Swagger
- `@nestjs/swagger` is present and `main.ts` calls `setupSwagger`, but
  `swagger-ui-express` (the package that serves the UI) is NOT a dep by default —
  `/api/docs` 500s without it. `npm i swagger-ui-express` → UI lives at
  `http://localhost:3000/api/docs`.

## Hybrid / BM25 search (verified)
`pg_search`/`pg_bm25` are blocked on Neon, so build search with native Postgres FTS
+ pgvector + reciprocal rank fusion (RRF) reranking:
1. Add a `search_vector tsvector` column, GIN-index it, and keep it fresh with a
   BEFORE INSERT/UPDATE trigger combining `title` (weight A), `excerpt`+`tags`
   (weight B), `content` (weight C) via `setweight(to_tsvector('english', ...), ...)`.
2. Keyword score: `1 - (1 / (1 + exp(-ts_rank(search_vector,
   websearch_to_tsquery('english', q)))))` over rows matching
   `search_vector @@ websearch_to_tsquery(...)`.
3. Semantic score: `1 - (embedding <=> '<vec>'::vector)` (use the subquery-form
   from the pgvector pitfall — `<=>` in ORDER BY silently returns 0 rows).
4. **Rerank with RRF (k=60)**: assign dense `row_number()` ranks to each result
   set, then `score = 1/(60+r_fts) + 1/(60+r_vec)`, ORDER BY score DESC. This fuses
   keyword + semantic into one ranked list and degrades gracefully when one side
   is empty.
Exact working SQL + the `hybridSearch()` TS function: `references/hybrid-search.md`.

## Pitfalls (hit and fixed this session)
- **camelCase vs snake_case 500**: entity props `authorId/createdAt` query a column
  that doesn't exist because the DB is `author_id/created_at`. TypeORM does NOT
  auto-convert. Fix: `SnakeNamingStrategy` (import from `'typeorm'`) in config, OR
  `@Column({ name: 'author_id' })` per prop. Verify by querying the real table
  columns via the MCP and diffing against the entity.
- **pgvector `<=>` in ORDER BY returns 0 rows**: on this Neon/pgvector build,
  `ORDER BY embedding <=> '<vec>'::vector` silently returns 0 rows (even though
  `SELECT embedding <=> vec` works and `WHERE embedding IS NOT NULL` has rows).
  Fix: wrap in a subquery and ORDER BY the materialized numeric column:
  `SELECT id,title,score FROM (SELECT id,title, 1-(embedding <=> '<vec>'::vector) AS score FROM articles WHERE embedding IS NOT NULL) sub ORDER BY score DESC LIMIT $1`.
  Also: parameterized `$1::vector` with a JS string returns 0 rows in the `pg`
  pool here — INLINE the vector literal instead (server-generated numeric array,
  safe). See `references/pgvector-rag.md`.
- **RAG 0 results despite valid vectors**: the query embedding MUST be computed by
  the SAME function/text as the stored embedding. Seed embeds `title + ' ' +
  excerpt`; if the agent queries only the title, similarity is low but non-zero
  (still returns rows). If they share NO token dims, you'll see low scores — keep
  seed and query embedding inputs aligned. Use a deterministic pseudo-embedder
  (FNV hash → dims) so it's reproducible without an external API key.

## Verification checklist (real output, not status claims)
- `npx nest build` AND `npx tsc --noEmit` must both exit 0.
- curl `/api/articles` → HTTP 200 with real rows.
- curl the agent SSE → see `RUN_STARTED` then `TEXT_MESSAGE_CONTENT` with a real
  retrieved article title + cosine score.
- `/api/docs` → HTTP 200.

## References
- `references/pgvector-rag.md` — exact working RAG query, the ORDER BY bug, and the
  pseudo-embedder that matches the seed.
- `references/hybrid-search.md` — BM25 FTS DDL (column + GIN + trigger), the RRF
  hybrid SQL, and the `hybridSearch()` TS function for `GET /api/search`.
- `references/mastra-agents.md` — agent + tool definitions and the AG-UI SSE
  controller skeleton.
