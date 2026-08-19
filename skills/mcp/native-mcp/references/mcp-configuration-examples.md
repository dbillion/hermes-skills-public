# MCP Configuration Examples from Hermes Session

This file contains practical examples of MCP server configurations based on the current session where we successfully configured Maltego and OpenCTI MCP servers, and attempted to set up Burp Suite MCP.

## Maltego MCP Server Configuration

The Maltego MCP server was successfully added and tested:

```yaml
mcp_servers:
  maltego:
    command: "/home/deeone/.nvm/versions/node/v25.6.1/bin/maltego-mcp"
    # No additional args or environment variables needed
```

This configuration provides access to 12 Maltego tools including:
- Graph creation and manipulation (`maltego_create_graph`, `maltego_add_entity`, etc.)
- OSINT lookups (`maltego_whois`, `maltego_dns`, `maltego_asn`, `maltego_crtsh`)
- Graph expansion utilities (`maltego_expand_ip`, `maltego_expand_domain`, etc.)

## OpenCTI MCP Server Configuration

The OpenCTI MCP server was configured but requires a running at localhost:8081:

```yaml
mcp_servers:
  opencti:
    command: "/home/deeone/mcp-servers/mcp-opencti/.venv/bin/python"
    args: ["/home/deeone/mcp-servers/mcp-opencti/opencti_mcp_server_v7.py"]
    env:
      OPENCTI_URL: "http://localhost:8081"
      OPENCTI_TOKEN: "b0de265c-0912-49d3-b781-7d4c4793a8be"
```

**Troubleshooting Notes:**
- The server returns `{"status":"unauthorized"}` when the token is incorrect or missing
- The server process exits immediately if environment variables aren't properly set
- Test connection manually: `curl -H "Authorization: Bearer $OPENCTI_TOKEN" http://localhost:8081/graphql`

## Burp Suite MCP Configuration (Planned)

Following the burp-mcp-agents pattern, the Burp Suite MCP should be configured via HTTP transport with a Caddy proxy:

```yaml
mcp_servers:
  burp:
    url: "http://localhost:19876/sse"
    headers:
      Authorization: "Bearer your-burp-token-here"
```

**Setup Requirements:**
1. Install Burp Suite Community/Professional
2. Install Burp AI Agent extension from: https://github.com/six2dez/burp-ai-agent/releases
3. Enable MCP Server in Burp AI Agent settings
4. Set up Caddy proxy as per burp-mcp-agents/common/Caddyfile:
   ```
   :19876 {
       reverse_proxy 127.0.0.1:9876
       header_up Host {upstream_hostport}
       header_up X-Forwarded-Host {host}
   }
   ```
5. Start Caddy: `caddy run --config /path/to/Caddyfile`

## General MCP Configuration Tips

### Environment Variables
Always use the `--env` flag for each variable when adding via CLI:
```bash
hermes mcp add opencti \
  --command /path/to/python \
  --args /path/to/server.py \
  --env OPENCTI_URL=http://localhost:8081 \
  --env OPENCTI_TOKEN=your_token
```

### Testing Connections
Use `hermes mcp test <server_name>` to verify configurations work before relying on them.

### Process Management
Some MCP servers may exit after initial handshake. Ensure the server process stays alive for the duration of your Hermes session.

### Troubleshooting Timeouts
If you see "MCP call timed out" errors:
1. Check if the server process is still running
2. Verify the command/args are correct
3. Look at server logs/output when running manually
4. Consider increasing timeout values in configuration