---
name: notion-mcp-utils
description: "Parse Notion MCP responses: extract JSON from text field."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [NOTION_TOKEN]
metadata:
  hermes:
    tags: [Notion, MCP, Integration, Productivity]
    homepage: https://developers.notion.com
---

# Notion MCP Utilities

This skill provides tips and tricks for using the Notion MCP server effectively, especially for parsing its responses.

## Parsing MCP Responses

The Notion MCP server returns a JSON object with a `content` array. The actual result is in the `text` field of the first element, which is a stringified JSON. You must parse this string to get the actual data.

### Example: Parsing a search response

```bash
# Call the MCP server
RESULT=$(mcp-cli call notion API-post-search '{"query":"tasks"}')

# Extract the inner JSON string (the value of the "text" field)
INNER_JSON=$(echo "$RESULT" | sed -n 's/.*"text": "\(.*\)".*/\1/p' | head -1)

# Unescape the string: convert \\ to \, \" to ", and \n to newline
UNESCAPED=$(echo "$INNER_JSON" | sed 's/\\\\/\\/g' | sed 's/\\"/"/g' | sed 's/\\n/\n/g')

# Now $UNESCAPED is the actual JSON you can parse with jq or similar
echo "$UNESCAPED" | jq .
```

### Example: Extracting titles from a data source query

Assuming you have a data source ID and want to get the titles of items:

```bash
DATA_SOURCE_ID="fff21259-8cc5-8112-9f23-ec2d76a3e223"
FILTER='{"property":"Status","select":{"equals":"Done"}}'

RESULT=$(mcp-cli call notion API-query-data-source "{\"data_source_id\":\"$DATA_SOURCE_ID\"}" 2>/dev/null <<< "$FILTER")
INNER_JSON=$(echo "$RESULT" | sed -n 's/.*"text": "\(.*\)".*/\1/p' | head -1)
UNESCAPED=$(echo "$INNER_JSON" | sed 's/\\\\/\\/g' | sed 's/\\"/"/g' | sed 's/\\n/\n/g')

# Extract titles (assuming a title property)
echo "$UNESCAPED" | jq -r '.results[].properties.title.title[0].text.content'
```

## When to Use MCP vs. Raw HTTP

See the `notion` skill for a detailed comparison. This utility focuses on the MCP-specific Got: parsing.

## Troubleshooting

- **Empty response from MCP**: If you get an empty response, the server might be failing silently. Try calling the Notion API directly with curl using the token from `~/.mcp_servers.json`.
- **Parsing errors**: Ensure you are correctly unescaping the string. The `sed` commands above handle common escapes.

## Reference

This skill complements the existing `notion` skill. For general Notion API usage (HTTP/curl, ntn CLI), refer to the `notion` skill.