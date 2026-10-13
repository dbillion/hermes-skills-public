# LinkedIn Posting Workflow (Session Reference)

## User Context
- **Location**: Tallinn, Estonia
- **LinkedIn**: `linkedin_feere-oxhorn` connection
- **Person ID**: `VOlIoQKyIK`
- **Content**: Rust Master Class series (26 chapters)
- **PDFs**: Google Drive links for lead magnets
- **Images**: First-page PNG covers converted from PDFs

## Workflow Used

### 1. Convert PDFs to PNG Covers
```bash
pdftoppm -png -r 100 -f 1 -l 1 input.pdf /tmp/covers/output_prefix
```

### 2. Create Payload File per Article
```json
{
  "author": "urn:li:person:VOlIoQKyIK",
  "commentary": "Story-driven post text...",
  "visibility": "PUBLIC",
  "images": ["/tmp/covers/Ch02_Basic_Programming-01.png"]
}
```

### 3. Post via Composio CLI
```bash
composio execute "LINKEDIN_CREATE_LINKED_IN_POST" \
  --account linkedin_feere-oxhorn \
  -d @/tmp/payload.json
```

### 4. Delete Posts (if needed)
```bash
composio execute "LINKEDIN_DELETE_LINKED_IN_POST" \
  --account linkedin_feere-oxhorn \
  -d '{"share_id": "urn:li:share:XXXX"}'
```

## Key Learnings

1. **Use `images` array, NOT `--file` flag**: Using both causes validation error.
2. **Write payload to file first**: Avoids shell escaping issues with JSON.
3. **Add delays between posts**: 2-3 seconds to avoid rate limiting.
4. **Confirm before posting**: Never publish without explicit user approval.
5. **Delete test posts immediately**: Clean up after testing.

## File Locations
- **v3 Articles**: `/home/deeone/Documents/deskprojects/rust_master_class_anime_final/cleansed/story_ready_articles_v3/`
- **PNG Covers**: `/tmp/covers/`
- **Payload Files**: `/tmp/payload_ch*.json`
- **Posting Script**: `/home/deeone/Documents/deskprojects/rust_master_class_anime_final/post_all_v2.py`
