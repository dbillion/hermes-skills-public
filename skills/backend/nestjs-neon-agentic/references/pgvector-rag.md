# pgvector RAG on Neon — working query + the ORDER BY trap

## The trap (cost ~1 hour of debugging)
On Neon Postgres 17 + pgvector, this query returns **0 rows** with no error:

```sql
SELECT id, title, 1 - (embedding <=> '<vec>'::vector) AS score
FROM articles
WHERE embedding IS NOT NULL
ORDER BY embedding <=> '<vec>'::vector
LIMIT 4;
```

Yet `SELECT (embedding <=> '<vec>'::vector) FROM articles LIMIT 1` returns a
finite distance (e.g. 0.897), and `SELECT title FROM articles WHERE embedding IS
NOT NULL` returns 6 rows. The distance computes fine; putting `<=>` directly in
`ORDER BY` (with an inline literal) makes the planner return nothing.

Also: a **parameterized** `$1::vector` with a JS string param returns 0 rows in
the `pg` Node pool here. Inline the literal instead.

## The fix (verified, returns 4 ranked rows)
```sql
SELECT id, title, excerpt, category, score FROM (
  SELECT id, title, excerpt, category,
         1 - (embedding <=> '<vec>'::vector) AS score
  FROM articles
  WHERE embedding IS NOT NULL
) sub
ORDER BY score DESC
LIMIT $1;
```
Compute the distance in an inner SELECT, then ORDER BY the materialized numeric
`score` column in the outer query. Works.

## Deterministic pseudo-embedder (no API key needed)
Seed and query MUST use the same function so vectors share token dims. FNV-1a hash
to dim index, +1 per token, L2-normalize, format `toFixed(6)`:

```js
function embed(text, dims = 1536) {
  const vec = new Array(dims).fill(0);
  const tokens = text.toLowerCase().match(/[a-z0-9]+/g) || [];
  for (const tok of tokens) {
    let h = 2166136261;
    for (let i = 0; i < tok.length; i++) {
      h ^= tok.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    vec[Math.abs(h) % dims] += 1;
  }
  const norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0)) || 1;
  return `[${vec.map((v) => (v / norm).toFixed(6)).join(',')}]`;
}
```
- Seed stores `embed(title + ' ' + excerpt)`. Query the agent with the user's text
  (shares title tokens -> high cosine, e.g. 0.744 for an exact-title query).
- Inline the returned string directly into the SQL (don't bind it).

## Reproduction recipe
1. Seed: `DATABASE_URL=... node scripts/seed.mjs` (idempotent; re-embeds existing rows).
2. Verify distance: `SELECT title, 1-(embedding <=> '<embedded-vec>'::vector) AS s
   FROM articles WHERE embedding IS NOT NULL ORDER BY s DESC LIMIT 3;`
3. Agent endpoint: `curl -N -X POST localhost:3000/api/agents/researcher/run -H
   'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"RAG
   with pgvector in Postgres"}],"threadId":"t1"}'` -> should stream the matching
   article at the top with a real score.
