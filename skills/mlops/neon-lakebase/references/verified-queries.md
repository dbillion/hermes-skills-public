# Verified Lakebase SQL (returned real rows on Neon PG17)

## BM25 (full-text) — lakebase_text
```sql
-- Assumes a tsvector column `search_vector` and a lakebase_bm25 index named 'articles_bm25'
SELECT id, title,
       search_vector <@> to_bm25query(to_tsvector('english', 'rag pgvector'), 'articles_bm25') AS bm25_score
FROM articles
ORDER BY bm25_score ASC          -- lower is better (negative magnitudes)
LIMIT 5;
-- Real result example: bm25_score = -5.0591 for the RAG article
```

## ANN (vector) — lakebase_vector
```sql
-- embedding is vector(1536). Inlining the literal vector returns 0 rows; wrap in a subquery.
SELECT a.id, a.title, a.embedding <=> q.vec AS dist
FROM articles a,
     (SELECT '[' || repeat('0.001,', 1535) || '0.001]'::vector(1536) AS vec) q
ORDER BY dist ASC
LIMIT 5;
-- The subquery trick fixes the "ORDER BY <=> '<inline>' returns 0 rows" pgvector bug.
```

## Hybrid RRF fusion (NestJS / TypeScript pattern)
```ts
// rank arrays bm25Rows[] and annRows[], each with .id
const k = 60;
const rrf = new Map<string, number>();
for (const [i, r] of bm25Rows.entries()) rrf.set(r.id, (rrf.get(r.id) ?? 0) + 0.5 / (k + i + 1));
for (const [i, r] of annRows.entries())  rrf.set(r.id, (rrf.get(r.id) ?? 0) + 0.5 / (k + i + 1));
const fused = [...rrf.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit);
```

## Reranker fallback
- `rag_jina_reranker_v1_tiny_en.rerank_distance(query, passage)` -> real, but the model worker
  daemon often does NOT start on Vercel-managed / free Neon compute.
  Error: `Couldn't connect worker stream /tmp/.s.pgrag.rag_jina_reranker_v1_tiny_en... No such file or directory`.
- Do NOT treat this as a code bug. Use RRF (above) as the rerank. If a true reranker is required,
  run it in app code (Cohere/CCP or a local cross-encoder) on the hybrid candidates.
