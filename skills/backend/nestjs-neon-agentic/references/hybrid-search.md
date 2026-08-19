# Hybrid search (BM25 FTS + pgvector + RRF reranking) on Neon

`pg_search`/`pg_bm25` (ParadeDB) are deprecated/blocked on Neon
(`NeonDbError: extension "pg_search" is deprecated and no longer allowed`).
Use native Postgres FTS instead — it is always available and gives BM25-style
ranking via `ts_rank`.

## 1. DDL (apply ONE statement per MCP `run_sql` call)

```sql
ALTER TABLE articles ADD COLUMN IF NOT EXISTS search_vector tsvector;

UPDATE articles SET search_vector =
  setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
  setweight(to_tsvector('english', coalesce(excerpt,'')), 'B') ||
  setweight(to_tsvector('english', coalesce(content,'')), 'C') ||
  setweight(to_tsvector('english', coalesce(array_to_string(tags,' '),'')), 'B');

CREATE INDEX IF NOT EXISTS articles_search_idx ON articles USING GIN (search_vector);

-- function (write to a .sql file; the $$ delimiter survives JSON-in-MCP better
-- than shell-escaped $ in a -c string):
CREATE OR REPLACE FUNCTION articles_search_vec() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title,'')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.excerpt,'')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.content,'')), 'C') ||
    setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags,' '),'')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS articles_search_vec_trigger ON articles;
CREATE TRIGGER articles_search_vec_trigger BEFORE INSERT OR UPDATE ON articles
  FOR EACH ROW EXECUTE FUNCTION articles_search_vec();
```

## 2. Hybrid query (RRF, k=60)

```sql
WITH fts AS (
  SELECT id, 1 - (1 / (1 + exp(-ts_rank(search_vector,
    websearch_to_tsquery('english', '<Q>'))))) AS fts_score
  FROM articles
  WHERE search_vector @@ websearch_to_tsquery('english', '<Q>')
),
vec AS (
  SELECT id, 1 - (embedding <=> '<VEC>'::vector) AS vec_score
  FROM articles WHERE embedding IS NOT NULL
),
ranked_fts AS (SELECT id, row_number() OVER (ORDER BY fts_score DESC) AS r FROM fts),
ranked_vec AS (SELECT id, row_number() OVER (ORDER BY vec_score DESC) AS r FROM vec)
SELECT a.id, a.title, a.excerpt, a.category,
       round(coalesce(fts.fts_score,0)::numeric,3) AS fts_score,
       round(coalesce(v.vec_score,0)::numeric,3) AS vec_score,
       round((coalesce(1.0/(60+rf.r),0) + coalesce(1.0/(60+rv.r),0))::numeric,4) AS score
FROM articles a
LEFT JOIN fts fts ON fts.id=a.id
LEFT JOIN vec v ON v.id=a.id
LEFT JOIN ranked_fts rf ON rf.id=a.id
LEFT JOIN ranked_vec rv ON rv.id=a.id
WHERE fts.id IS NOT NULL OR v.id IS NOT NULL
ORDER BY score DESC
LIMIT <LIMIT>;
```

Notes:
- `<VEC>` is the pseudo-embedding literal (see `references/pgvector-rag.md`); inline
  it — a parameterized `$1::vector` returned 0 rows in the `pg` pool here.
- `<=>` must NOT sit in `ORDER BY` directly (returns 0 rows); the vec CTE +
  materialized `vec_score` avoids that.
- `websearch_to_tsquery` tolerates bare words and quotes; escape single quotes in
  `<Q>` as `''`.

## 3. `hybridSearch()` (TS, in `db.util.ts`)

```ts
export async function hybridSearch(query: string, limit = 6) {
  const vec = pseudoEmbed(query);            // matches seed embed() exactly
  const ts = query.replace(/'/g, "''");
  const r = await pool.query(
    `WITH fts AS (
       SELECT id, 1 - (1 / (1 + exp(-ts_rank(search_vector,
         websearch_to_tsquery('english', '${ts}'))))) AS fts_score
       FROM articles WHERE search_vector @@ websearch_to_tsquery('english', '${ts}')
     ),
     vec AS (SELECT id, 1 - (embedding <=> '${vec}'::vector) AS vec_score
             FROM articles WHERE embedding IS NOT NULL),
     ranked_fts AS (SELECT id, row_number() OVER (ORDER BY fts_score DESC) AS r FROM fts),
     ranked_vec AS (SELECT id, row_number() OVER (ORDER BY vec_score DESC) AS r FROM vec)
     SELECT a.id, a.title, a.excerpt, a.category,
            round(coalesce(fts.fts_score,0)::numeric,3) AS fts_score,
            round(coalesce(v.vec_score,0)::numeric,3) AS vec_score,
            round((coalesce(1.0/(60+rf.r),0) + coalesce(1.0/(60+rv.r),0))::numeric,4) AS score
     FROM articles a
     LEFT JOIN fts fts ON fts.id=a.id LEFT JOIN vec v ON v.id=a.id
     LEFT JOIN ranked_fts rf ON rf.id=a.id LEFT JOIN ranked_vec rv ON rv.id=a.id
     WHERE fts.id IS NOT NULL OR v.id IS NOT NULL
     ORDER BY score DESC LIMIT $1`,
    [limit],
  );
  return r.rows;
}
```

Expose via `GET /api/search?q=&limit=` (public controller in `modules/search`).
Verified: `?q=postgres` returns Postgres-related articles with both `fts_score` and
`vec_score` fused; `?q=vector similarity search` ranks "RAG with pgvector in
Postgres" first by semantic weight.
