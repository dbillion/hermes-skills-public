---
name: neon-lakebase
description: Provision and use Neon Postgres with Lakebase extensions (lakebase_text BM25 full-text search, lakebase_vector ANN vector search) and hybrid RRF fusion. Covers the non-obvious Neon API preload-library step required to enable Lakebase, the exact CREATE EXTENSION / CREATE INDEX syntax, query operators, and verified-working hybrid search patterns. Use when a task needs Postgres full-text + vector search on Neon, or when pg_search/pg_bm25 is unavailable/deprecated.
license: MIT
metadata:
  author: ks-knowledge-sharing project learnings
  version: '1.0'
---

# Neon + Lakebase (BM25 + Vector + Hybrid)

Neon's **Lakebase** extensions provide production full-text (BM25) and vector (ANN) search inside Postgres. They are NOT enabled by the usual `CREATE EXTENSION` alone on a default compute — the shared libraries must be registered via the **Neon API** (the `neon` CLI cannot set `preload_libraries` directly; the docs state CLI cannot do preloads).

## When to use
- You need FTS + vector similarity on Neon and `pg_search` / `pg_bm25` are deprecated/unavailable.
- Hybrid retrieval (keyword + semantic) fused via RRF for RAG / search.
- Native Postgres (no separate search service).

## Hard-won enablement sequence (verified)
1. **Authenticate** the `neon` CLI: `neon auth` (opens browser) OR use a Neon API key with `neon` commands via `--api-key`.
2. **Find project + org.** `neon projects list` may only show your personal org. If the project is missing, list orgs (`neon orgs list`) and re-list with `--org-id <orgId>`. Vercel-managed projects live under an org like `org-crimson-bush-48892848` ("Vercel: <user>'s projects"), not the personal org.
3. **Enable preload libraries via the Neon API** (CLI cannot). Patch the project settings:
   ```
   neon api POST /projects/<projectId> -X PATCH -d '{
     "project": { "settings": { "preload_libraries": {
       "enabled_libraries": [
         "timescaledb","pg_cron","pg_partman_bgw",
         "rag_bge_small_en_v15","rag_jina_reranker_v1_tiny_en",
         "lakebase_vector","lakebase_text"
       ]
     }}}}
   ```
   Note: `neon api` is a pass-through to the REST API; use `POST ... -X PATCH -d '{...}'`. Verify with `neon api GET /projects/<projectId>`.
4. **Restart the compute** so the new shared_preload_libraries take effect: `neon api POST /projects/<projectId>/endpoints/<endpointId>/actions/restart` (or scale to 0 and wake). Then confirm with:
   ```
   neon psql --project-id <projectId> --role-name neondb_owner -- -c "SHOW shared_preload_libraries;"
   ```
   You should see `lakebase_vector,lakebase_text` in the list.
5. **Create extensions + indexes** (now that preloads are live):
   ```
   CREATE EXTENSION IF NOT EXISTS lakebase_text;
   CREATE EXTENSION IF NOT EXISTS lakebase_vector;
   -- BM25 over a tsvector column:
   CREATE INDEX articles_bm25 ON articles USING lakebase_bm25 (search_vector);
   -- ANN over an embedding vector column:
   CREATE INDEX articles_embedding_ann ON articles USING lakebase_ann (embedding vector_cos_ops);
   ```
   `vector_cos_ops` is the operator class for cosine distance with `lakebase_ann`.

## Executing SQL (which subcommand works)
- `neon psql --project-id <id> --role-name neondb_owner -- -c "SQL"` — the working interactive/CLI SQL path.
- `neon sql` — NOT a subcommand in neon 2.x.
- `neon api` — pass-through for GET/POST/PATCH/DELETE to the REST API (used for preloads + restarts above).

## Query operators (verified)
- **BM25 score** (lower = better, negative magnitudes): `search_vector <@> to_bm25query(to_tsvector('english', :q), 'articles_bm25')`. Order `ASC` and take the top N.
- **ANN distance**: `embedding <=> :query_vec` (cosine). Wrap the literal vector in a subquery to avoid the empty-result bug when inlining a `vector` parameter (see references/verified-queries.md).
- **RRF fusion** of the two result sets in app code (k=60): `score = 0.5/(k+rank_bm25) + 0.5/(k+rank_ann)`. This is the rerank step when a dedicated reranker model is unavailable.

## Caveats (from real failures)
- `rag_jina_reranker_v1_tiny_en` extension *installs* but its model worker daemon may not spawn on free/Vercel-managed compute -> SQL throws `Couldn't connect worker stream /tmp/.s.pgrag... No such file or directory`. This is infrastructure, not your code. Fall back to RRF. Neon docs themselves call pgRAG experimental and recommend a dedicated project.
- BM25 shows a sequential scan on tiny tables (<100 rows) — harmless; it switches to index scan at scale.
- Always run DDL (CREATE EXTENSION / CREATE INDEX) as the `neondb_owner` role via `neon psql`.

See references/verified-queries.md for copy-paste SQL that returned real rows, and references/neon-cli-cookbook.md for the exact CLI/API commands.
