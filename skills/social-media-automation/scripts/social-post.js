#!/usr/bin/env node
// ============================================================================
// Social Media Poster — Posts video/image to all platforms via Ayrshare API
// ============================================================================
// Usage:
//   node social-post.js <media_path> <caption> [--platforms p1,p2] [--schedule ISO] [--dry-run]
//
// Environment:
//   AYRSHARE_API_KEY  — Required. Get at https://app.ayrshare.com/
//   AYRSHARE_PROFILE_KEY — Optional. For business accounts.
// ============================================================================

const fs = require('fs');
const path = require('path');
const https = require('https');

const API_KEY = process.env.AYRSHARE_API_KEY || '';
const PROFILE_KEY = process.env.AYRSHARE_PROFILE_KEY || '';
const BASE_URL = 'https://api.ayrshare.com/api';

const args = process.argv.slice(2);
const mediaPath = args[0];
let caption = '';
const options = { platforms: [], schedule: null, dryRun: false };

for (let i = 1; i < args.length; i++) {
  if (args[i] === '--platforms' && args[i + 1]) options.platforms = args[++i].split(',').map(p => p.trim().toLowerCase());
  else if (args[i] === '--schedule' && args[i + 1]) options.schedule = args[++i];
  else if (args[i] === '--dry-run') options.dryRun = true;
  else if (!args[i].startsWith('--')) caption = args[i];
}

function tweakCaption(platform, text) {
  const tweaks = {
    twitter: text.length > 280 ? text.substring(0, 277) + '...' : text,
    instagram: text + '\n\n#ai #business #entrepreneur #smallbusiness #aitools #tech #innovation #growth #marketing #automation',
    tiktok: text + '\n\n#ai #business #aitools #smallbusiness #entrepreneur #fyp #viral',
    linkedin: text + '\n\nWhat AI tools are you using in your business? Share in the comments 👇\n\n#AI #Business #Entrepreneurship #SmallBusiness #Innovation',
    facebook: text + '\n\n#AI #Business #Entrepreneurship #SmallBusiness',
  };
  return tweaks[platform] || text;
}

function request(method, endpoint, body) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${BASE_URL}${endpoint}`);
    const data = body ? JSON.stringify(body) : null;
    const reqOptions = {
      hostname: url.hostname, path: url.pathname, method,
      headers: {
        'Content-Type': 'application/json', 'Accept-Encoding': 'gzip, deflate, br',
        'Authorization': `Bearer ${API_KEY}`,
        ...(PROFILE_KEY ? { 'Profile-Key': PROFILE_KEY } : {}),
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}),
      },
    };
    const req = https.request(reqOptions, (res) => {
      let chunks = '';
      res.on('data', d => chunks += d);
      res.on('end', () => { try { resolve({ status: res.statusCode, data: JSON.parse(chunks) }); } catch { resolve({ status: res.statusCode, data: chunks }); } });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function uploadMedia(filePath) {
  const fileName = path.basename(filePath);
  const fileExt = path.extname(filePath).toLowerCase();
  console.log(`  📤 Uploading ${fileName}...`);
  const fileBuffer = fs.readFileSync(filePath);
  const response = await request('POST', '/media/upload', {
    fileName, fileType: ['.mp4', '.mov', '.avi'].includes(fileExt) ? 'video' : 'image',
    file: fileBuffer.toString('base64'),
  });
  if (response.status === 200 && response.data.url) {
    console.log(`  ✓ Media uploaded`);
    return response.data.url;
  }
  throw new Error(`Upload failed: ${JSON.stringify(response.data)}`);
}

async function postToSocial(mediaUrl, platforms) {
  const results = [];
  for (const platform of platforms) {
    const body = { post: tweakCaption(platform, caption), platforms: [platform], media_urls: [mediaUrl], ...(options.schedule ? { scheduleDate: options.schedule } : {}) };
    if (options.dryRun) { console.log(`  [DRY RUN] ${platform}: ${body.post.substring(0, 60)}...`); results.push({ platform, status: 'dry-run' }); continue; }
    try {
      const response = await request('POST', '/post', body);
      if (response.status === 200) { console.log(`  ✅ ${platform}: Posted!`); results.push({ platform, status: 'success' }); }
      else { console.log(`  ❌ ${platform}: ${JSON.stringify(response.data)}`); results.push({ platform, status: 'error', error: response.data }); }
    } catch (err) { console.log(`  ❌ ${platform}: ${err.message}`); results.push({ platform, status: 'error', error: err.message }); }
    await new Promise(r => setTimeout(r, 1000));
  }
  return results;
}

async function main() {
  console.log('📱 Social Media Poster\n======================\n');
  if (!mediaPath || !fs.existsSync(mediaPath)) { console.error('Usage: node social-post.js <media_path> <caption>'); process.exit(1); }
  if (!API_KEY) { console.error('❌ AYRSHARE_API_KEY not set!'); process.exit(1); }
  const platforms = options.platforms.length > 0 ? options.platforms : ['instagram', 'tiktok', 'facebook', 'linkedin'];
  console.log(`Media: ${mediaPath}\nCaption: ${caption}\nPlatforms: ${platforms.join(', ')}\n`);
  const mediaUrl = await uploadMedia(mediaPath);
  console.log('\nPosting...');
  const results = await postToSocial(mediaUrl, platforms);
  const success = results.filter(r => r.status === 'success' || r.status === 'dry-run').length;
  console.log(`\n📊 ${success}/${results.length} posted successfully`);
}

main().catch(err => { console.error('Fatal:', err); process.exit(1); });
