---
name: gws-google-slides
description: >
  Use when the user wants to find, read, extract content from, or update Google
  Slides presentations through the local gws CLI.
---

# Google Slides via `gws`

Use `gws slides ...` and `gws drive ...` for presentation work.

## Finding Presentations

Search with a Slides MIME type filter:

```bash
gws drive files list --params '{"q":"mimeType='\''application/vnd.google-apps.presentation'\'' and name contains '\''Quarterly Review'\'' and trashed=false","fields":"files(id,name,webViewLink,modifiedTime)","pageSize":10}'
```

For full-text search, use `fullText contains`.

## Reading Content

Get presentation metadata and slide object IDs:

```bash
gws slides presentations get --params '{"presentationId":"<id>"}'
```

When downloading thumbnails or binary outputs, always use absolute output paths.
Inspect the method schema first:

```bash
gws schema slides.presentations.pages.getThumbnail --resolve-refs
```

## Updates

Preview slide edits before applying them. For `batchUpdate`, inspect the schema
and keep requests focused:

```bash
gws schema slides.presentations.batchUpdate --resolve-refs
```
