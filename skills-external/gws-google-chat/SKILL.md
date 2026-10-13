---
name: gws-google-chat
description: >
  Use before sending, reading, or managing Google Chat messages through the
  local gws CLI. Trigger on Google Chat, chat space, DM, or sending chat
  messages.
---

# Google Chat via `gws`

Use `gws chat ...` for Google Chat work.

## Message Formatting

Google Chat supports a specific markdown subset. Convert unsupported markdown
before sending:

- `**bold**` -> `*bold*`
- `[text](url)` -> `<url|text>`
- `# Heading` -> `*Heading*`
- Nested lists -> single-level lists

Supported forms include `*bold*`, `_italic_`, `~strikethrough~`, inline code,
code blocks, bullet lists, `<url|text>` links, and `<users/{userId}>` mentions.

## Sending Messages

Never send a Chat message without previewing the target space or DM and the
exact message content, then receiving explicit confirmation.

Inspect schemas before writes:

```bash
gws schema chat.spaces.messages.create --resolve-refs
```

## Reading And Spaces

Use `gws schema` to verify list/get parameters before reading spaces, members,
or messages. Present multiple spaces or messages as numbered lists.
