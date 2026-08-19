---
name: gws-google-docs
description: >
  Use before creating, editing, reading, or managing Google Docs through the
  local gws CLI. Trigger on document, doc, Google Doc, or writing/editing
  document content.
---

# Google Docs via `gws`

Use `gws docs ...` and `gws drive ...` for document work.

## Finding Documents

Search with a Docs MIME type filter:

```bash
gws drive files list --params '{"q":"mimeType='\''application/vnd.google-apps.document'\'' and name contains '\''Report'\'' and trashed=false","fields":"files(id,name,webViewLink,modifiedTime)","pageSize":10}'
```

## Reading Documents

Inspect the schema and read the document:

```bash
gws schema docs.documents.get --resolve-refs
gws docs documents get --params '{"documentId":"<id>"}'
```

## Creating And Formatting

For richly formatted documents, use a two-step workflow:

1. Insert content as plain text.
2. Apply formatting with `batchUpdate`.

Calculate indices carefully. Google Docs uses 1-based body indices; count
newlines.

Use heading styles for major sections and bold for labels. Preview content and
formatting before applying writes.

Inspect schemas before writes:

```bash
gws schema docs.documents.create --resolve-refs
gws schema docs.documents.batchUpdate --resolve-refs
```

## Organization

If a document must live in a specific folder, create the document first, then
move it with Drive. Verify folder existence before moving.
