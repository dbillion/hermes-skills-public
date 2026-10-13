#!/usr/bin/env node
// Minimal Stitch MCP JSON-RPC client over HTTP.
// Usage: node stitch_client.js <method> '<json-args>'   (method = create_project | generate_screen_from_text | get_screen | list_screens)
// Example:
//   node stitch_client.js create_project '{"title":"My Project"}'
//   node stitch_client.js generate_screen_from_text '{"projectId":"12281104722419857681","prompt":"Landing hero, indigo accent","deviceType":"DESKTOP"}'
//
// Proven gotchas (see references/stitch-mcp-direct-http.md):
//  - projectId MUST be a string, never a number.
//  - generate_screen_from_text is synchronous: outputComponents[].text holds screens/<id> + downloadUrl.
//  - Transient "Request contains an invalid argument" -> retry.

const https = require('https');
const fs = require('fs');
const KEY = process.env.STITCH_API_KEY ||
  (() => { try { return JSON.parse(fs.readFileSync(process.env.HOME + '/.gemini/extensions/Stitch/gemini-extension.json', 'utf8')).apiKey; } catch { return ''; } })();
const EP = 'https://stitch.googleapis.com/mcp';

function rpc(method, params, id = 1) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: '2.0', id, method, params });
    const u = new URL(EP);
    const r = https.request({ hostname: u.hostname, path: u.pathname, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
        'X-Goog-Api-Key': KEY, 'Content-Length': Buffer.byteLength(body) } },
      (x) => { let d = ''; x.on('data', c => d += c); x.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { resolve({ raw: d.slice(0, 800) }); } }); });
    r.on('error', reject); r.write(body); r.end();
  });
}
const call = (name, args, id = 2) => rpc('tools/call', { name, arguments: args }, id);

async function withRetry(fn, n = 4) {
  for (let i = 0; i < n; i++) {
    try { const r = await fn(); const t = r?.result?.content?.[0]?.text || '';
      if (t.includes('invalid argument') || t.includes('Request contains')) { console.error(`attempt ${i+1}: retry`); await new Promise(s=>setTimeout(s,2500)); continue; }
      return r; } catch (e) { console.error(`attempt ${i+1} threw`, e.message); await new Promise(s=>setTimeout(s,2500)); }
  }
  return null;
}

(async () => {
  if (!KEY) { console.error('No STITCH_API_KEY and could not read gemini extension key.'); process.exit(1); }
  const [method, argsJson] = [process.argv[2], process.argv[3] || '{}'];
  if (method === 'initialize') { console.log(JSON.stringify(await rpc('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'hermes', version: '1.0' } }))); return; }
  if (method === 'tools/list') { console.log(JSON.stringify(await rpc('tools/list'))); return; }
  const res = await withRetry(() => call(method, JSON.parse(argsJson)));
  console.log(JSON.stringify(res, null, 2));
})().catch(e => { console.error(e); process.exit(1); });
