# YouTube Data API v3 Endpoints Reference

Use these URLs with `mcp_zapier_youtube_youtube_make_api_get_request`.

## Search

### Search for videos
```
https://www.googleapis.com/youtube/v3/search?part=snippet&q=romans+theology&type=video&order=date&maxResults=10
```

### Search by channel
```
https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=UCxxxxx&type=video&order=date&maxResults=25
```

## Video Details

### Get video info
```
https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id=VIDEO_ID
```

### Get video with all parts
```
https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails,topicDetails,recordingDetails,liveStreamingDetails&id=VIDEO_ID
```

Parts available: `snippet`, `contentDetails`, `statistics`, `status`, `topicDetails`, `recordingDetails`, `liveStreamingDetails`, `player`, `id`

## Channel

### Get channel info
```
https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id=CHANNEL_ID
```

### Get your own channel
```
https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true
```

## Captions / Transcripts

### List available captions
```
https://www.googleapis.com/youtube/v3/captions?part=snippet&id=VIDEO_ID
```

### Get specific caption track
```
https://www.googleapis.com/youtube/v3/captions/CAPTION_TRACK_ID
```

Note: Downloading captions directly requires the Google OAuth token. For easier transcript extraction, use the `youtube-content` skill's `fetch_transcript.py` script instead.

## Playlists

### Get playlist items
```
https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=PLAYLIST_ID&maxResults=50
```

### List your playlists
```
https://www.googleapis.com/youtube/v3/playlists?part=snippet&mine=true&maxResults=25
```

## Comments

### Get top-level comments
```
https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=VIDEO_ID&order=relevance&maxResults=100
```

### Get replies to a comment
```
https://www.googleapis.com/youtube/v3/comments?part=snippet&parentId=PARENT_COMMENT_ID
```

## Analytics (OAuth, your channel only)

Note: These require the `yt-analytics.readonly` scope which the Zapier MCP has.

For analytics, use `mcp_zapier_youtube_youtube_get_report` instead of raw API calls.

## Useful Queries

### Search theology lectures
```
https://www.googleapis.com/youtube/v3/search?part=snippet&q=seminary+lectures+on+grace&type=video&videoDuration=long&order=viewCount&maxResults=20
```

### Find recent sermons
```
https://www.googleapis.com/youtube/v3/search?part=keyword&q=sermon+on+faith&type=video&order=date&publishedAfter=2026-01-01T00:00:00Z&maxResults=15
```

### Get video duration
```
https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=VIDEO_ID
```
Returns `contentDetails.duration` in ISO 8601 format (e.g., `PT1H23M45S`)

### Check if video has captions
```
https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=VIDEO_ID
```
Look for `contentDetails.caption: "true"`
