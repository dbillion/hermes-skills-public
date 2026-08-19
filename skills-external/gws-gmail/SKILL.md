---
name: gws-gmail
description: >
  Use before composing, sending, drafting, searching, or managing email through
  the local gws CLI. Trigger on email, Gmail, inbox, draft, label, or sending a
  message.
---

# Gmail via `gws`

Use `gws gmail ...` for Gmail work.

## Search

Use Gmail search syntax in the `q` parameter:

```bash
gws gmail users messages list --params '{"userId":"me","q":"from:alice@example.com newer_than:7d","maxResults":10}'
```

Fetch message details only for selected results:

```bash
gws gmail users messages get --params '{"userId":"me","id":"<message-id>","format":"full"}'
```

## Sending And Drafting

Never send or draft email without an explicit user confirmation after previewing
recipients, subject, and body.

For rich email bodies, use HTML unless the user asks for plain text. Gmail strips
style blocks, so use inline CSS. Prefer semantic HTML:

```html
<p style="font-family:Arial,sans-serif;font-size:14px;color:#333;">Hello,</p>
<p style="font-family:Arial,sans-serif;font-size:14px;color:#333;">Message body.</p>
```

Before sending, inspect the exact method schema:

```bash
gws schema gmail.users.messages.send --resolve-refs
gws schema gmail.users.drafts.create --resolve-refs
```

## Message Handling

- Use `userId: "me"` unless the user specifies another mailbox.
- Preserve thread context when replying.
- Validate attachments exist locally before referencing them.
- For destructive changes, such as delete or trash, preview and confirm first.
