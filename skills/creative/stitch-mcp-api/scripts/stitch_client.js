#!/usr/bin/env node
/*
 * Stitch MCP JSON-RPC client (proven working, 2026-07).
 * Drives https://stitch.googleapis.com/mcp directly because `mcp-cli` is
 * unreliable (silent, no output) and Hermes may not load the Stitch server
 * as a tool this session.
 *
 * Usage:
 *   node stitch_client.js create_project '{"title":"My App"}'
 *   node stitch_client.js gen <projectId> <DEVICE:DESKTOP|MOBILE> "<prompt>"
 *   node stitch_client.js list <projectId>
 *
 * `gen` generates ONE screen and downloads its assets into ./stitch-designs/.
 * Repeat `gen` for more screens, or script a loop.
 *
 * GOTCHAS (verified):
 *  - projectId MUST be a string ("1228...", no "projects/" prefix).
 *  - generation takes 60-180s; call sequentially.
 *  - saved "screenshot" URLs may be HTML (Tailwind CDN), not binary PNG.
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

// API key: read from env or fall back to the Gemini Stitch extension config.
function loadKey() {
  if (process.env.STITCH_API_KEY) return process.env.STITCH_API_KEY;
  try {
    const p = os.homedir() + '/.gemini/extensions/Stitch/gemini-extension.json';
    const cfg = JSON.parse(fs.readFileSync(p, 'utf8'));
    return cfg.mcpServers.stitch.headers['X-Goog-Api-Key'];
  } catch (e) { throw new Error('STITCH_API_KEY not set and Gemini ext config not found'); }
}
const KEY = loadKey();
const EP = 'https://stitch.googleapis.com/mcp';
const OUT = path.join(process.cwd(), 'stitch-designs');

function rpc(method, params, id = 1) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: '2.0', id, method, params });
    const u = new URL(EP);
    const r = https.request({
      hostname: u.hostname, path: u.pathname, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
        'X-Goog-Api-Key': KEY, 'Content-Length': Buffer.byteLength(body) } },
      (x) => { let d = ''; x.on('data', c => d += c); x.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { resolve({ raw: d.slice(0, 800) }); } }); });
    r.on('error', reject); r.write(body); r.end();
  });
}
const call = (name, args, id = 2) => rpc('tools/call', { name, arguments: args }, id);

function download(url, dest) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location)
        return download(res.headers.location, dest).then(resolve).catch(reject);
      const f = fs.createWriteStream(dest);
      res.pipe(f); f.on('finish', () => { f.close(); resolve(dest); });
    }).on('error', reject);
  });
}

function extract(text) {
  const urls = new Set(); const ids = new Set();
  const uRe = /https:\/\/[^\s"\\]+/g; let m;
  while ((m = uRe.exec(text))) { if (m[0].includes('download') || m[0].includes('googleapis') || m[0].includes('lh3')) urls.add(m[0]); }
  const idRe = /screens\/([a-zA-Z0-9_-]{20,})/g; while ((m = idRe.exec(text))) ids.add(m[1]);
  return { urls: [...urls], screenId: [...ids][0] };
}

(async () => {
  const [,, cmd, a, b, c] = process.argv;
  if (cmd === 'create_project') {
    const res = await call('create_project', JSON.parse(a || '{}'));
    console.log(res.result?.structuredContent?.name || JSON.stringify(res).slice(0, 300));
  } else if (cmd === 'list') {
    const res = await call('list_screens', { projectId: String(a) });
    (res?.result?.structuredContent?.screens || []).forEach((s, i) => console.log(i, s.title, '|', s.name || s.id));
  } else if (cmd === 'gen') {
    const projectId = String(a); const device = (b || 'DESKTOP').toUpperCase(); const prompt = c;
    console.log(`Generating (${device})...`);
    const res = await call('generate_screen_from_text', { projectId, prompt, deviceType: device }, Math.floor(Math.random() * 1e6));
    const text = res?.result?.content?.[0]?.text;
    if (!text) { console.log('NO TEXT / ERROR:', JSON.stringify(res).slice(0, 400)); process.exit(1); }
    const { urls, screenId } = extract(text);
    fs.mkdirSync(OUT, { recursive: true });
    const safe = (prompt || 'screen').slice(0, 24).replace(/[^a-z0-9]+/gi, '_');
    fs.writeFileSync(path.join(OUT, `${safe}.json`), text);
    for (const u of urls) {
      const tag = u.includes('.html') || u.includes('htmlCode') ? 'html' : 'png';
      const dest = path.join(OUT, `${safe}.${tag}`);
      try { await download(u, dest); console.log('saved', dest); } catch (e) { console.log('dl fail', e.message); }
    }
    console.log('screenId=', screenId, '| urls=', urls.length, '| out=', OUT);
  } else {
    console.log('Usage:\n  node stitch_client.js create_project \'{"title":"X"}\'\n  node stitch_client.js gen <projectId> <DESKTOP|MOBILE> "<prompt>"\n  node stitch_client.js list <projectId>');
  }
})().catch(e => { console.error('ERR', e); process.exit(1); });
