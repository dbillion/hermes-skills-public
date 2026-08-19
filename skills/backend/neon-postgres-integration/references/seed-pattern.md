// scripts/seed.mjs — seed real data into Neon Postgres (run: node scripts/seed.mjs)
// Requires DATABASE_URL in env (Neon connection string).
import { Client } from 'pg';
import { randomUUID } from 'crypto';

const url = process.env.DATABASE_URL;
if (!url) { console.error('DATABASE_URL is required'); process.exit(1); }

const client = new Client({ connectionString: url });

// Deterministic pseudo-embedding (dims) — NOT a real model embedding, but produces
// stable, queryable pgvector data for demo RAG/cosine. Production: use a real embedder.
function embed(text, dims = 1536) {
  const vec = new Array(dims).fill(0);
  const tokens = text.toLowerCase().match(/[a-z0-9]+/g) || [];
  for (const tok of tokens) {
    let h = 2166136261;
    for (let i = 0; i < tok.length; i++) { h ^= tok.charCodeAt(i); h = Math.imul(h, 16777619); }
    vec[Math.abs(h) % dims] += 1;
  }
  const norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0)) || 1;
  return `[${vec.map((v) => (v / norm).toFixed(6)).join(',')}]`;
}

async function main() {
  await client.connect();
  console.log('Connected to Neon.');

  // Categories (match exact DB columns)
  for (const [name, slug] of [['Engineering','engineering'],['Research','research'],['Maps','maps']]) {
    await client.query(
      `INSERT INTO categories (name, slug, description, color)
       VALUES ($1,$2,$3,$4) ON CONFLICT (slug) DO UPDATE SET name=EXCLUDED.name RETURNING id`,
      [name, slug, `${name} articles`, '#5C6BC0']);
  }

  // Users (DB columns: email, username, first_name, last_name, password_hash, role, is_active)
  for (const u of [
    { first:'Ada', last:'Lovelace', username:'ada', email:'ada@ks.dev' },
    { first:'Alan', last:'Turing', username:'alan', email:'alan@ks.dev' },
  ]) {
    await client.query(
      `INSERT INTO users (email, username, first_name, last_name, password_hash, role, is_active)
       VALUES ($1,$2,$3,$4,$5,'author',true)
       ON CONFLICT (email) DO UPDATE SET username=EXCLUDED.username RETURNING id`,
      [u.email, u.username, u.first, u.last, 'seed-not-real']); // use bcrypt hash in real seed
  }

  // Articles (DB columns must match exactly; embedding is a [..] vector literal)
  const articles = [ /* {title, slug, excerpt, content, category, tags:[], geom:{lng,lat}} */ ];
  for (const a of articles) {
    await client.query(
      `INSERT INTO articles (title, slug, excerpt, content, status, category, tags, author_id,
         is_published, featured, image_url, geom, embedding, created_at, updated_at)
       VALUES ($1,$2,$3,$4,'published',$5,$6,$7,true,false,'',
         ST_SetSRID(ST_MakePoint($8,$9),4326),$10, now(), now())
       ON CONFLICT (slug) DO NOTHING`,
      [a.title, a.slug, a.excerpt, a.content, a.category, a.tags, a.authorId,
       a.geom.lng, a.geom.lat, embed(a.title + ' ' + a.content)]);
  }

  await client.end();
  console.log('Seed complete.');
}
main().catch(async (e) => { console.error('SEED ERROR:', e.message); await client.end().catch(()=>{}); process.exit(1); });
