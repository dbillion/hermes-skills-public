---
name: social-media-automation
description: Full social media automation — create videos with music from carousel slides, post to Instagram, TikTok, Facebook, LinkedIn via unified social media APIs. Use when the user wants to publish content to social media platforms.
metadata:
  tags: social-media, instagram, tiktok, facebook, linkedin, ayrshare, zernio, postproxy, video, automation
---

# Social Media Automation

End-to-end workflow: carousel slides → video with music → post to all platforms.

## Support Files

- **`references/api-research.md`** — Full API research: Zernio, Postproxy, Ayrshare comparison; native APIs (Instagram, TikTok, Facebook, LinkedIn, WhatsApp); platform-specific notes; common pitfalls
- **`scripts/social-workflow.sh`** — Combines carousel slides → video with optional music (FFmpeg)
- **`scripts/social-post.js`** — Posts video/image to all platforms via Zernio, Postproxy, or Ayrshare (multi-provider)

## Prerequisites

### Required Tools
| Tool | Install | Purpose |
|---|---|---|
| `clickup-cli` | `npm i -g @krodak/clickup-cli` | Task management |
| `social-media-api` | `npm i -g social-media-api` | Ayrshare SDK |
| `ffmpeg` | System package | Video/audio processing |
| `remotion` | `npx create-video` | Animated video creation |

### Required API Keys
| Service | Key | Get It From |
|---|---|---|
| **Zernio** (recommended) | `ZERNIO_API_KEY` | https://zernio.com (free, no credit card) |
| **Postproxy** | `POSTPROXY_API_KEY` | https://postproxy.dev (free tier: 10 posts/mo) |
| **Ayrshare** | `AYRSHARE_API_KEY` | https://app.ayrshare.com/ |
| **ClickUp** | API Token (`pk_...`) | https://app.clickup.com/settings/apps → Generate |
| **ClickUp** | Team ID | URL: `app.clickup.com/{TEAM_ID}/...` |

### Environment Setup
```bash
export ZERNIO_API_KEY="your-key-here"    # or POSTPROXY_API_KEY or AYRSHARE_API_KEY
export CU_API_TOKEN="pk-your-clickup-token"
export CU_TEAM_ID="your-team-id"
```

## Workflow

### Step 1: Create Video from Slides + Music

```bash
# Copy scripts from skill to workspace (one-time)
cp ~/.hermes/skills/social-media-automation/scripts/social-workflow.sh workspace/scripts/
cp ~/.hermes/skills/social-media-automation/scripts/social-post.js workspace/scripts/

# Basic (no music)
bash workspace/scripts/social-workflow.sh \
  workspace/instagram-carousel/slides/ \
  workspace/output-video.mp4

# With background music
bash workspace/scripts/social-workflow.sh \
  workspace/instagram-carousel/slides/ \
  workspace/output-video.mp4 \
  workspace/music.mp3
```

Output: MP4 video at `workspace/output-video.mp4`

### Step 2: Post to All Platforms

```bash
# Post via Zernio (recommended)
node workspace/scripts/social-post.js \
  workspace/output-video.mp4 \
  "Your caption here" \
  --provider zernio

# Post via Postproxy
node workspace/scripts/social-post.js \
  workspace/output-video.mp4 \
  "Your caption here" \
  --provider postproxy

# Post via Ayrshare
node workspace/scripts/social-post.js \
  workspace/output-video.mp4 \
  "Your caption here" \
  --provider ayrshare

# Dry run (see what would be posted without posting)
node workspace/scripts/social-post.js \
  workspace/output-video.mp4 \
  "Test caption" \
  --dry-run

# Schedule for later
node workspace/scripts/social-post.js \
  workspace/output-video.mp4 \
  "Scheduled post" \
  --schedule "2026-05-18T14:00:00Z"

# Specific platforms only
node workspace/scripts/social-post.js \
  workspace/output-video.mp4 \
  "Your caption" \
  --platforms "instagram,tiktok,facebook,linkedin"
```

### Step 3: Manage in ClickUp

```bash
# Initialize ClickUp CLI
cup init --token pk_YOUR_TOKEN --team YOUR_TEAM_ID

# Verify
cup auth

# List tasks
cup tasks

# Create a content task (NOTE: use -d for description, -l for list — NOT --desc or --list)
cup create -l "LIST_ID" -n "Post AI Tools carousel" -d "Post to Instagram + TikTok" --priority 2 --tags "instagram,tiktok"

# Update task status
cup update TASK_ID --status "Posted"
```

## Platform-Specific Notes

See `references/api-research.md` for full details including native API endpoints, rate limits, and video specs.

### Instagram
- Supports: Reels, Carousels, Stories, Images
- Auth: Connect Instagram account in provider dashboard
- Note: Instagram account must be a Business or Creator account

### TikTok
- Supports: Videos (< 10 min)
- Auth: Connect TikTok account in provider dashboard
- Note: TikTok Business account required

### Facebook
- Supports: Videos, Images, Reels
- Auth: Connect Facebook Page in provider dashboard
- Note: Posts to Page, not personal profile

### LinkedIn
- Supports: Videos (up to 15 min), Images, Text
- Auth: Connect LinkedIn account in provider dashboard

### WhatsApp
- Supported by: Zernio only (not Ayrshare, not Postproxy)
- Alternative: WhatsApp Cloud API directly (Meta Business account required)

## Provider Selection

**User preference**: Prefer free/cheaper alternatives. Zernio (free tier: 2 accounts, no credit card) is the default recommendation over Ayrshare ($149/mo minimum).

### Provider Selection Guide
- **Default**: Zernio — free tier, 15 platforms, MCP server, best for AI agents
- **If Zernio doesn't support needed platform**: Postproxy (10 platforms, free 10 posts/mo)
- **Enterprise/approval workflows**: Ayrshare (13 platforms, established, but paid from $149/mo)

```bash
# Run once to create Social Media space + Content Calendar list
node workspace/scripts/setup-content-calendar.js
```

This creates:
- "Social Media" Space
- "Content Calendar" List
- 5 sample tasks

## Troubleshooting

See `references/api-research.md` for common pitfalls and platform-specific notes.

**Zernio API errors**: Base URL is `https://zernio.com/api/v1` (NOT `api.zernio.com/v1`)
**Node.js JSON parse failures**: Set `Accept-Encoding: identity` — gzip responses break `https.request` JSON parsing
**Zernio "No connected account"**: GET `/accounts` first, match by `platform` field, check `enabled === true`
**Zernio posting format**: Use `content` + `platforms: [{platform, accountId}]` — NOT `post` + `platforms: [string]`
**Ayrshare auth error**: Verify `AYRSHARE_API_KEY` is set correctly
**ClickUp auth error**: Run `cup auth` to verify token
**Video too large**: Reduce resolution or duration in social-workflow.sh
**Instagram posting fails**: Ensure Instagram account is Business/Creator type
**TikTok posting fails**: Check video format (MP4, < 10 min)
