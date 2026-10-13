# Social Media API Research — 2026

## Unified Social Media Posting APIs

### Provider Comparison

| Provider | Platforms | Free Tier | Pricing Model | MCP | Best For |
|---|---|---|---|---|---|
| **Zernio** | 15 (IG, TikTok, FB, LI, X, YT, WA, TG, Pinterest, Bluesky, Reddit, Snapchat, Threads, Google Business) | 2 free accounts | Per account: $6/$3/$1 at scale | Yes, 280+ tools | AI agents, best overall |
| **Postproxy** | 10 (IG, TikTok, FB, LI, X, YT, TG, Pinterest, Bluesky, Threads) | 10 posts/mo | Flat: $17/$49/$399/mo | Yes | Flat pricing, n8n/MCP native |
| **Ayrshare** | 13 (IG, TikTok, FB, LI, X, YT, TG, Pinterest, Bluesky, Reddit, Snapchat, Threads, Google Business) | None | Per profile: $149/$299/$599/mo | No | Enterprise, established |

### Recommendation

**Use Zernio** for new projects: free tier (2 accounts, no credit card), broadest platform coverage including WhatsApp, MCP server with 280+ tools, CLI with JSON output. Sign up at https://zernio.com

## Zernio API — Technical Details

### Base URL
```
https://zernio.com/api/v1
```
**NOT** `https://api.zernio.com/v1` — the docs say `zernio.com/api/v1`.

### Authentication
```
Authorization: Bearer sk_...
```
API key format: `sk_` prefix + 64 hex characters (67 total).

### Node.js HTTP Gotcha — Gzip Encoding
When using Node.js `https.request`, **do NOT set `Accept-Encoding: gzip`** unless you handle decompression. Zernio (and many other APIs) return gzip-encoded responses by default, and the raw binary will fail `JSON.parse()` silently.

**Fix:** Set `Accept-Encoding: identity` in request headers.

### Get Connected Accounts
```
GET /api/v1/accounts
```
Returns `{ accounts: [{ _id, platform, enabled, displayName, ... }] }`

Match accounts by `platform` field (e.g., `"linkedin"`, `"tiktok"`). Must check `enabled === true`.

### Create Post
```
POST /api/v1/posts
{
  "content": "Post text here",
  "platforms": [
    { "platform": "linkedin", "accountId": "6a0abf..." }
  ],
  "scheduledFor": "2026-05-18T14:00:00",
  "timezone": "America/Toronto"
}
```

**Key differences from Ayrshare/Postproxy:**
- Uses `content` (not `post` or `caption`)
- `platforms` is array of `{platform, accountId}` objects (not array of strings)
- `scheduledFor` + `timezone` (not `scheduledAt`)
- Account ID required per platform (no auto-select)

### Upload Media
```
POST /api/v1/media
{
  "fileName": "video.mp4",
  "fileType": "video",
  "file": "<base64-encoded file>"
}
```
Returns `{ url: "..." }` — use this URL in post's `mediaUrls`.

### SDK
```bash
npm install @zernio/node
```

## Platform-Specific Notes

- **Instagram**: Business/Creator account required
- **TikTok**: Business account required. Videos < 10 min.
- **Facebook**: Page admin required. Posts to Page, not personal profile.
- **LinkedIn**: Videos up to 15 min.
- **WhatsApp**: Supported by Zernio only (not Ayrshare, not Postproxy)
- **X/Twitter**: BYO OAuth 1.0a credentials required after March 2026.

## Common Pitfalls

1. Instagram personal accounts cannot use API — must be Business/Creator
2. TikTok personal accounts cannot use Content Posting API
3. Facebook API posts to Pages, not personal profiles
4. X/Twitter requires own OAuth keys after March 2026
5. Video format: MP4 (H.264) universally supported
6. Zernio base URL: `zernio.com/api/v1` NOT `api.zernio.com/v1`
7. Node.js gzip: Always use `Accept-Encoding: identity` when using raw `https.request`
8. Zernio posting requires per-platform `accountId` — GET `/accounts` first, match by `platform` field
9. User prefers free/cheaper alternatives — Zernio free tier (2 accounts) over Ayrshare ($149/mo min)
