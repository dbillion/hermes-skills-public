---
name: zapier-youtube-mcp
description: "YouTube MCP server via Zapier. Search videos, get analytics, upload, manage playlists, YouTube API access. Use for YouTube search, channel management, and API operations — NOT for transcript extraction (use NLM's --youtube source instead)."
---

# Zapier YouTube MCP

Connects to YouTube via Zapier's MCP server. Provides 8 tools for YouTube operations: search, analytics, uploads, playlist management, and full API access.

**IMPORTANT**: This MCP does NOT extract transcripts. For transcript extraction, use NLM's `--youtube` source feature instead (see `youtube-content` skill).

## Setup

Add to `~/.hermes/config.yaml` under `mcp_servers`:

```yaml
mcp_servers:
  zapier_youtube:
    url: "https://mcp.zapier.com/api/v1/connect?token=***    timeout: 60
    connect_timeout: 30
```

Then restart Hermes Agent. Tools will be available as `mcp_zapier_youtube_*`.

## Important: What This MCP Does NOT Do

- **Does NOT extract transcripts** — Use NLM `--youtube` source for that (see `youtube-content` skill or `nlm-advanced`)
- **Does NOT read video content** — It's for management only
- Use this MCP for: searching, analytics, uploading, thumbnails, playlists, raw API calls
- Use NLM for: transcripts, summaries, content analysis

## Available Tools

### 1. youtube_find_video
Search for YouTube videos by keywords, channel, date range, etc.

```
mcp_zapier_youtube_youtube_find_video(
  instructions: "Search query or detailed instructions",
  output_hint: "just the title, videoId, and published date"
)
```

### 2. youtube_get_report
Get analytics reports for your YouTube channel.

```
mcp_zapier_youtube_youtube_get_report(
  instructions: "Report parameters",
  output_hint: "views, watch time, subscribers for last 30 days",
  metrics: ["views", "watchTime", "subscribersGained"]
)
```

### 3. youtube_make_api_get_request
Make any YouTube API GET request without handling auth.

```
mcp_zapier_youtube_youtube_make_api_get_request(
  instructions: "What you want to fetch",
  url: "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=VIDEO_ID"
)
```

### 4. youtube_make_api_mutating_request
Make POST/PUT/PATCH/DELETE requests to YouTube API.

```
mcp_zapier_youtube_youtube_make_api_mutating_request(
  instructions: "What you want to change",
  url: "https://www.googleapis.com/youtube/v3/videos?part=snippet",
  # plus body parameters
)
```

### 5. youtube_upload_video
Upload a video to your channel.

```
mcp_zapier_youtube_youtube_upload_video(
  instructions: "Upload video file",
  tags: ["tag1", "tag2"]
)
```

### 6. youtube_update_video_thumbnail
Update a video's thumbnail image.

```
mcp_zapier_youtube_youtube_update_video_thumbnail(
  video_id: "VIDEO_ID",
  # thumbnail file
)
```

### 7. youtube_add_video_to_playlist
Add a video to one of your playlists.

```
mcp_zapier_youtube_youtube_add_video_to_playlist(
  instructions: "Add to playlist",
  # video and playlist params
)
```

### 8. get_configuration_url
Get the URL where users can configure this MCP server.

```
mcp_zapier_youtube_get_configuration_url()
```

## Workflows

### Search for Videos

```
mcp_zapier_youtube_youtube_find_video(
  instructions: "Find recent theology lectures on the book of Romans",
  output_hint: "just the title, videoId, channel name, and published date",
  order: "date"
)
```

### Fetch Video Transcript (via youtube-transcript-api)

The Zapier MCP doesn't have a direct transcript tool, but you can use it alongside the `youtube-content` skill's script:

```bash
# Get video ID from MCP search, then:
python3 ~/.hermes/skills/media/youtube-content/scripts/fetch_transcript.py "VIDEO_ID"
```

Or make an API request to the YouTube Data API for caption info:
```
mcp_zapier_youtube_youtube_make_api_get_request(
  instructions: "Get caption tracks available for this video",
  url: "https://www.googleapis.com/youtube/v3/captions?part=snippet&id=VIDEO_ID"
)
```

### Extract Transcript and Analyze

**Do NOT use this MCP for transcripts.** Use NLM instead:

```bash
# Preferred: NLM handles everything
nlm notebook create "YouTube Transcript"
nlm source add <notebook-id> --youtube "https://youtu.be/VIDEO_ID" --wait
nlm notebook query <notebook-id> "Extract the full transcript with timestamps."
```

The Zapier MCP has no transcript tool. The `youtube_make_api_get_request` can check for caption track metadata but cannot download caption content. Always route transcript requests through NLM's `--youtube` source feature.

### Upload a Video

```
mcp_zapier_youtube_youtube_upload_video(
  instructions: "Upload my presentation video about Pauline theology",
  tags: ["theology", "bible", "paul", "romans", "seminary"]
)
```

## Tips

- Always use `output_hint` to limit response data — keeps results focused
- The `instructions` field accepts natural language — be descriptive
- For search, include specific terms: channel name, date range, topic
- You can combine with the `youtube-content` skill for transcript extraction
- The MCP handles OAuth — no need to manage API keys for YouTube
- Use `youtube_make_api_get_request` for any YouTube Data API v3 endpoint
- For analytics on channels you don't own, you'll need proper OAuth scopes

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tools not appearing | Add `mcp_servers` to config.yaml, restart agent |
| "Not Acceptable" error | Server needs MCP protocol — use `mcp_` tool prefix, not web_fetch |
| Auth errors | Configure Zapier token at mcp.zapier.com |
| Rate limits | Wait between requests, batch operations |
| Missing transcript | Some videos have disabled captions — use youtube-content skill as fallback |

## Transcript Extraction: The Right Way

**The Zapier YouTube MCP CANNOT extract transcripts.** Despite having `youtube_make_api_get_request`, the YouTube Data API captions download endpoint requires OAuth scopes that Zapier does not support. The `captions.list` works (lists available captions), but `captions.download` returns 401.

### Correct Tool: NLM (`--youtube` source)

```bash
# Create notebook, add YouTube as source, extract transcript — all in 3 commands
nlm notebook create "YouTube: [Topic]"
nlm source add <notebook-id> --youtube "https://youtu.be/VIDEO_ID" --wait
nlm notebook query <notebook-id> "Extract the full transcript with timestamps. Include speaker labels if identifiable."
```

This is the **only reliable way** in this environment to get YouTube transcripts. No pip packages needed.

### Fallback if NLM unavailable
The `youtube-content` skill's `fetch_transcript.py` script works but requires `youtube-transcript-api` pip package.

### What the Zapier MCP IS good for
- **Search** — finding videos by keywords, channels, dates
- **Analytics** — views, watch time, subscriber stats for YOUR channel (requires proper OAuth scopes)
- **Upload** — video file upload to your channel
- **API exploration** — any YouTube Data API v3 GET request that doesn't need caption download scope

### Token/Connection Issues
The Zapier MCP uses HTTP/SSE transport. Tokens expire. If you see `401 Unauthorized` or repeated "connection lost" errors:
1. Go to mcp.zapier.com → regenerate/revoke token
2. Update `~/.hermes/config.yaml` → `mcp_servers.zapier_youtube.url` with new token
3. Restart gateway: `/restart`

## See Also

- `youtube-content` skill — fallback transcript extraction script (requires `youtube-transcript-api` pip package)
- `nlm-productivity` skill — **preferred** YouTube transcript extraction via `nlm source add --youtube`
- `references/mcp-tool-matrix.md` — which MCP tools work vs their marketing claims, env var gotchas, cron model overrides
- `references/youtube-api-endpoints.md` — YouTube Data API v3 endpoint reference
- Zapier MCP docs: https://mcp.zapier.com