---
name: neon-postgres-integration
description: "Provision and wire a Neon Postgres database to a NestJS/TypeORM (or any Node) backend using the Neon MCP through mcp-cli, and avoid the schema/entity pitfalls that break the connection at runtime. Covers driving neon run_sql via mcp-cli (one statement per call, persistence gotchas), enabling postgis/vector/pg_graphql, applying a schema file reliably, and connecting TypeORM to a live Neon DATABASE_URL with the exact column/naming-strategy/synchronize settings that work. Also captures the verified Mastra + AG-UI + CopilotKit agent pattern for a seamless agent UX. Trigger when the user says use Neon, connect to Postgres, create a Neon DB, wire NestJS to Neon, add PostGIS/pgvector, or any task where a Postgres backend must be provisioned via the Neon MCP rather than a local DB."
---

# Neon Postgres Integration (MCP-driven + NestJS/TypeORM)

Use this skill when a task needs a live Neon Postgres database created/provisioned through
the Neon MCP (exposed via `mcp-cli`), and a NestJS/TypeORM (or plain `pg`) backend wired to it.
The Neon MCP works, but it has sharp edges that cause silent failures. Encode these up front.

## 0. Preconditions (verify, don't assume)
- The Neon MCP server is configured at `~/.config/mcp-cli/mcp_servers.json` under the server name `neon`.
- The project id is a STRING (e.g. `"weathered-forest-50229673"`), NOT a number. Passing a number fails silently.
- You may also have a `context7` server in the same config (used for library docs, e.g. `/mastra-ai/mastra`).

## 1. Driving `neon run_sql` via mcp-cli (THE reliable form)
Call it explicitly with the config path and server name. Do NOT rely on a default mcp-cli config —
the `neon` server lives in the user's `~/.config/mcp-cli/mcp_servers.json`.

```
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json call neon run_sql \
  '{"params":{"projectId":"<PROJECT_ID_STRING>","sql":"<SINGLE STATEMENT>"}}'
```

### CRITICAL quirks (these waste hours if unknown)
1. **ONE statement per call.** `run_sql` cannot execute multiple commands in one prepared statement.
   `CREATE EXTENSION a; CREATE EXTENSION b;` -> `NeonDbError: cannot insert multiple commands into a prepared statement`.
   Always send one `CREATE`/`ALTER`/`INSERT`/`SELECT` per invocation. Loop in bash or python.
2. **`[]` response is NOT proof of persistence.** A successful DDL call returns `{"content":[{"type":"text","text":"[]"}]}`.
   But a *batch* of statements where some fail can also return `[]` per call while never persisting
   (observed: a python loop splitting a schema.sql returned `[]` for every statement, yet only the first
   table existed afterward). **Always re-query `information_schema.tables` to confirm a table landed.**
3. **`CREATE EXTENSION IF NOT EXISTS postgis` etc. return `[]` even when already present** — that's fine.
4. **Test DDL with extension-dependent types (vector, geometry) BEFORE trusting a loop.** A direct
   `CREATE TABLE t (col vector(1536))` returning `[]` and then appearing in `information_schema` proves
   the extension is live. If the table does NOT appear, the extension wasn't active at DDL time.
5. **Extensions available on Neon:** `postgis`, `postgis_topology`, `vector` (pgvector), `pg_graphql`.
   Enable them explicitly even though they're "available" — `pg_extension` must list them.

See `references/neon-mcp-quirks.md` for the exact confirmation recipes (extensions, tables, columns, one-statement loop).

## 2. Apply a schema.sql reliably
Split the file into individual statements (split on `;`), skip comments/blank lines, and call `neon run_sql`
once per statement. Then verify with:

```
SELECT table_name FROM information_schema.tables
WHERE table_schema='public' AND table_type='BASE TABLE'
AND table_name NOT IN ('spatial_ref_sys') ORDER BY table_name;
```

If a table is missing, re-run JUST that statement (it was likely dropped by a later failing statement
or never persisted). Idempotent `CREATE TABLE IF NOT EXISTS` is your friend.

## 3. Connect TypeORM (NestJS) to Neon
Set `DATABASE_URL` to the Neon connection string (user provides it; treat as a secret, never echo it back).
In `database.config.ts`:

```ts
import 'dotenv/config';            // MUST be first — loads .env BEFORE TypeOrmModule.forRoot runs
import { TypeOrmModuleOptions } from '@nestjs/typeorm';

export function databaseConfig(): TypeOrmModuleOptions {
  const url = process.env.DATABASE_URL;
  if (!url) throw new Error('DATABASE_URL is required (Neon Postgres connection string)');
  return {
    type: 'postgres',
    url,
    entities: [__dirname + '/../modules/**/*.entity{.ts,.js}'], // scope to YOUR entities only
    synchronize: false,   // schema is provisioned externally via MCP — never auto-sync
    logging: process.env.DB_LOGGING === 'true',
    ssl: { rejectUnauthorized: false },
    extra: { max: 5 },
    namingStrategy: new SnakeNamingStrategy(), // see pitfall #3
  };
}
```

### Pitfalls that break `nest start` (all observed this session)
**Pitfall 1 — `DATABASE_URL is required` at boot.** `ConfigModule.forRoot()` initializes env vars too
late; `TypeOrmModule.forRoot(databaseConfig())` runs at module-load time. Fix: `import 'dotenv/config'`
at the very top of `database.config.ts` so `process.env.DATABASE_URL` is set before the config function runs.

**Pitfall 2 — `Data type "vector"/"geometry" not supported by "postgres" database`.** This TypeORM
version's metadata validator rejects `vector` and `geometry` column types (the `@Column('vector')`
overload doesn't exist; `geometry` with `spatial:{srid}` also fails). Fixes that WORK:
  - Do NOT map `embedding vector(1536)` as a TypeORM column. The DB column stays `vector(1536)`
    (enables the `<=>` cosine operator + index); manage embeddings via **raw SQL** in a RagService
    (insert as a `[..]` literal, query with `embedding::vector <=> $1::vector`).
  - For geometry (PostGIS), you CAN map it but use `@Column({ type: 'geometry' as any })` WITHOUT the
    `spatial` option (the `spatial` property is rejected by the decorator overload). SRID is set at the
    DB level (your schema created it as `geometry(Point,4326)`).

**Pitfall 3 — camelCase entity props vs snake_case DB columns.** TypeORM defaults column name = property
name, so `authorId` -> queries `authorId` which doesn't exist (`errorMissingColumn`, hint "Perhaps you
meant a.author_id"). Fix: a custom snake-case `NamingStrategy` (extends `DefaultNamingStrategy`, overrides
`columnName` to `propertyName.replace(/([A-Z])/g,'_$1').toLowerCase()`). NOTE: this TypeORM build has NO
`SnakeNamingStrategy` export and NO `typeorm/naming-strategy/SnakeNamingStrategy` module — define it inline.

**Pitfall 4 — broken skeleton entities in the glob.** If the glob picks up pre-existing `*.entity.ts`
files with bad column defs (e.g. `@Column() articleId` with no type -> `Data type "Object" not supported`),
scope the entities glob to only the modules you built (`modules/**/*.entity`), NOT `**/*.entity`. The
legacy `database/entities/*` skeletons in this repo have `simple-array`/`Object`/relation mismatches and
are not wired into active modules.

**Pitfall 5 — `simple-array` vs `TEXT[]`.** Declaring `@Column('simple-array')` expects a comma-separated
`text` column; the DB has `tags TEXT[]`. Mismatch -> missing-column errors. Use `@Column('text',{array:true})`
to match `TEXT[]`.

**Pitfall 6 — ALTER must be individual too.** Adding columns (`ALTER TABLE ... ADD COLUMN`) also rejects
multiple commands. Send each ADD COLUMN separately. `IF NOT EXISTS` is safe/idempotent.

**Pitfall 7 — EADDRINUSE when restarting.** `nest start` (ts-node) is slow to boot; if you restart, the
old `dist/main.js` may still hold :3000. Run the compiled output instead: `node dist/main.js` (fast,
deterministic) with `DATABASE_URL=... NODE_ENV=development`. Kill stale node processes before restarting.

**Pitfall 8 — stale inline LSP/linter errors after edits.** The harness's inline TS linter occasionally
shows phantom diagnostics referencing PRE-EDIT file state (e.g. an old class name, a just-re-added import)
even after the file is correct. These are NOT real compile errors. The authoritative check is
`npx tsc --noEmit -p tsconfig.json` (or `npx nest build`) — if that returns exit 0, the code is fine and
the inline overlay is stale. Don't burn turns "fixing" phantom LSP errors; re-run the real type-check.

## 4. Seed data into Neon (plain `pg`, not TypeORM)
A `scripts/seed.mjs` using `pg`'s `Client` is the most reliable way to insert real rows (it handles
`vector` literals and `ST_MakePoint`/`ST_GeomFromGeoJSON` natively). Match EXACT column names — query
`information_schema.columns` first if unsure. Use `ON CONFLICT DO NOTHING` for idempotency.
See `references/seed-pattern.md` for the template.

## 5. Seamless agent UX: Mastra + AG-UI + CopilotKit (verified pattern)
Research via Context7 (`/mastra-ai/mastra`) produced the canonical integration. Condensed in
`references/mastra-agui-copilotkit.md`. Summary: Mastra runs agents server-side; the
`@ag-ui/mastra/copilotkit` adapter exposes them at a `/copilotkit` AG-UI endpoint; the frontend connects
via CopilotKit's `<CopilotKit runtimeUrl agent>` + `<CopilotChat>` (React) OR Angular's `@ag-ui/client`
RuntimeClient (streaming events, generative UI, human-in-the-loop). One protocol, streaming agent UX,
no custom websocket — that's the "seamless" part. For an Angular (not React) frontend, consume the AG-UI
HTTP/SSE endpoint directly with `@ag-ui/client` rather than mounting CopilotKit's React components.

## 6. Verification checklist (run before claiming success)
- [ ] `information_schema.tables` lists every expected table (re-query, don't trust `[]`).
- [ ] `pg_extension` lists postgis, vector, pg_graphql.
- [ ] **pgvector `<=>` actually works**: `SELECT '[1,2,3]'::vector <=> '[1,2,3]'::vector` returns `0`
      via the MCP. If it errors/returns empty, RAG is NOT functional — do not claim it works. (See the
      OPEN PITFALL in `references/mastra-agui-copilotkit.md`.)
- [ ] `curl http://localhost:3000/api/<entity>` returns HTTP 200 with REAL rows (not `[]` from mocks).
- [ ] No `DataTypeNotSupportedError` / `errorMissingColumn` in the API boot log.
- [ ] Frontend services call the API (HttpClient), not `of(mock).pipe(delay())`.
- [ ] Inline LSP linter shows phantom errors after edits -> trust `npx tsc --noEmit` (exit 0 = clean).

## 5b. Reuse Hermes provider keys for real LLM calls (Mastra etc.)
Don't ask the user for a new API key — reuse the ones Hermes already holds (see key-reuse + Mastra
import-path specifics, including the OpenRouter `OPENAI_BASE_URL` trick and `openai/gpt-4o-mini` model
id, in `references/mastra-agui-copilotkit.md`). Pull values into the target `.env` WITHOUT echoing
secrets; keep `.env` gitignored; verify with a real model call.

## 7. Honesty rule (user mandate)
The user explicitly requires real, verified output — NOT status claims. Every slice must be curl-tested
against the live DB before being called "done". If a layer is stubbed (e.g. auth controller returns a
mock JWT), say so plainly; do not present it as working.
