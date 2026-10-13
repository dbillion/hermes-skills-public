# LinkedIn Posting with Media (PDFs/Images) via Composio CLI

## Overview

LinkedIn's API does not support direct PDF uploads. To share PDF content (e.g., whitepapers, book chapters, reports) on LinkedIn, you must:

1. Convert the PDF's first page to a PNG image (cover)
2. Upload the PNG as an image attachment to a LinkedIn post
3. Optionally include a URL to the full PDF in the post commentary

## PDF → PNG Conversion

Use `pdftoppm` (from Poppler) to convert PDF pages to PNG:

```bash
# Convert first page only (fast, for cover images)
pdftoppm -png -r 150 -f 1 -l 1 input.pdf output_prefix

# Convert all pages (slow, large files)
pdftoppm -png -r 300 input.pdf output_prefix
```

- `-r 150` = 150 DPI (good balance of quality/size)
- `-f 1 -l 1` = first page only
- Output: `output_prefix-01.png` (single page) or `output_prefix-01.png`, `output_prefix-02.png`, etc.

**Note:** High-resolution (300 DPI) multi-page conversions can be very slow (30s+ per PDF) and may time out. Use 150 DPI for covers.

## LinkedIn Post with Image

```bash
composio execute "LINKEDIN_CREATE_LINKED_IN_POST" \
  -d '{
    "author": "urn:li:person:YOUR_PERSON_ID",
    "commentary": "Your post text here...",
    "images": [
      "/path/to/cover-01.png"
    ]
  }'
```

**Schema requirements:**
- `author` (required): `urn:li:person:<ID>` or `urn:li:organization:<ID>`
- `commentary` (required): Post text, max 3000 chars
- `images` (optional): Array of image paths (1-20 images)
- `visibility` (optional): `PUBLIC` (default), `CONNECTIONS`, `LOGGED_IN`, `CONTAINER`
- `lifecycleState` (optional): `PUBLISHED` (default), `DRAFT`, `PUBLISH_REQUESTED`

## LinkedIn Article (URL Share)

```bash
composio execute "LINKEDIN_CREATE_ARTICLE_OR_URL_SHARE" \
  -d '{
    "author": "urn:li:person:YOUR_PERSON_ID",
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    "specificContent": {
      "com.linkedin.ugc.ShareContent": {
        "shareCommentary": {"text": "Your commentary..."},
        "shareMediaCategory": "ARTICLE",
        "media": [
          {
            "originalUrl": "https://yourdomain.com/article-url",
            "title": {"text": "Article Title"},
            "description": {"text": "Article description"}
          }
        ]
      }
    }
  }'
```

**Schema requirements:**
- `author` (required): Person or org URN
- `visibility` (required): Must include `com.linkedin.ugc.MemberNetworkVisibility`
- `specificContent.com.linkedin.ugc.ShareContent` (required):
  - `shareCommentary` (required): `{"text": "..."}`
  - `shareMediaCategory` (required): `"ARTICLE"` or `"NONE"`
  - `media` (required): Array with one `originalUrl` object

## Getting Your Person ID

```bash
composio execute "LINKEDIN_GET_MY_INFO" -d '{}'
```

Returns `id` field (e.g., `VOlIoQKyIK`) — use as `urn:li:person:<ID>`.

## Workflow: Batch Posting from a Folder

For scheduling multiple posts (e.g., 30-day content calendar):

1. **Map content to media**: Each post/article should reference a PDF or image
2. **Convert all PDFs first**: Batch convert with `pdftoppm` (parallelize if possible)
3. **Create a schedule**: Map dates to content pieces
4. **Execute sequentially**: Run `composio execute` for each post
5. **Track results**: Save log IDs for each post for debugging

### Example: Batch PDF Conversion Script

```bash
#!/bin/bash
PDF_DIR="/path/to/pdfs"
IMG_DIR="/path/to/images"
mkdir -p "$IMG_DIR"

for pdf in "$PDF_DIR"/*.pdf; do
  prefix=$(basename "$pdf" .pdf)
  echo "Converting: $prefix"
  pdftoppm -png -r 150 -f 1 -l 1 "$pdf" "$IMG_DIR/$prefix"
done
```

### Example: Posting Script

```bash
#!/bin/bash
# Post each article with its cover image
PERSON_ID="urn:li:person:VOlIoQKyIK"
BASE_DIR="/path/to/content"

for i in $(seq -w 1 30); do
  COVER="$BASE_DIR/images/ch${i}_cover-01.png"
  TEXT=$(cat "$BASE_DIR/posts/post_${i}.md")
  
  composio execute "LINKEDIN_CREATE_LINKED_IN_POST" \
    -d "{\"author\": \"$PERSON_ID\", \"commentary\": $(jq -Rs . <<< \"$TEXT\"), \"images\": [\"$COVER\"]}"
  
  sleep 2  # Rate limit buffer
done
```

## Common Pitfalls

1. **PDF upload fails**: LinkedIn doesn't accept PDFs directly. Always convert to PNG first.
2. **Image too large**: LinkedIn has size limits. Use 150 DPI, not 300.
3. **Author URN wrong**: Must be `urn:li:person:<ID>`, not just the ID.
4. **Visibility missing**: Article shares require the nested visibility object.
5. **Rate limiting**: LinkedIn throttles rapid posting. Add 2-5 second delays between posts.
6. **Composio CLI auth**: Ensure `composio whoami` shows the correct account before posting.

## Composio LinkedIn Toolkit Capabilities

The Composio LinkedIn toolkit (v20260826_00) supports 24 tools including:
- Post creation (text, URL shares, video)
- Post deletion and editing
- Profile reading (own + others)
- Comment creation
- Media upload (images, video)
- Organization analytics
- Ad targeting search

**Not supported**: Direct PDF upload, job search, connection requests, messaging.
