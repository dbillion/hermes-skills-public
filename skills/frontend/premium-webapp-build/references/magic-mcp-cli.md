# Wiring + calling @21st-dev/magic (the user's stated design utility)

## 1. Config wiring (in ~/.hermes/config.yaml)
Add as a SEPARATE `mcp_servers` entry. NEVER overwrite existing servers.
Put the key in a SHELL ENV VAR first, then reference it by name in config.

```yaml
  magic-21st:
    command: "npx"
    args:
      - "-y"
      - "@21st-dev/magic@latest"
    env:
      API_KEY: "${TWENTY_FIRST_DEV_KEY}"
```

Export the env var so Hermes expands it at MCP launch (do NOT paste the literal
key into config.yaml — that trips the consent gate and leaks the secret):
```bash
# in ~/.bashrc / ~/.zshrc / ~/.profile
export TWENTY_FIRST_DEV_KEY="21st_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```
After editing config, the server only goes live after an EXTERNAL Hermes restart
(cannot restart from a gateway-connected session).

## 2. Call it via scoped mcp-cli (never bare)
`mcp-cli` is at /home/deeone/.local/bin/mcp-cli. Write a scoped config (no literal
key, no other servers) to /tmp/magic-scope.json:
```json
{ "mcpServers": { "magic-21st": { "type": "stdio", "command": "npx", "args": ["-y", "@21st-dev/magic@latest"] } } }
```
Then pass the key as an env var to the process:
```bash
export TWENTY_FIRST_DEV_KEY="21st_sk_..."
export API_KEY="$TWENTY_FIRST_DEV_KEY"
mcp-cli -c /tmp/magic-scope.json call magic-21st/search '{"query":"animated hero banner with stats","framework":"react"}'
```

## 3. Tool facts (from a real free-tier run)
- `search` — FREE, returns component metadata + install commands + ids. Use this.
- `get_component {id}` — PAID/quota step (free tier: 2 retrievals/day). Spend on
  real component code to port. Example: Hero Animated id 1788 (radial-gradient
  jumbotron hero, emerald "green" palette available) is good DNA for a DSA hub.
- `generate` — PAYWALLED on free tier: returns `locked:true, reason:
  generation_limit_reached` and a pricing URL. It returns a BUILD URL, not inline
  code, so even paid it is an interactive browser loop, not headless codegen.
- `get_usage` — shows `freeRetrievalsRemaining` (today's quota).

## 4. OpenDesign (companion utility)
`od` MCP (daemon on :7456 when running) exposes 162 skills: card-xiaohongshu
(swipeable carousel), frontend-slides, ppt-keynote, slides, poster-hero,
imagegen/fal-generate. Use `od start_run` for full-page generation when wanted.

## 5. Secret hygiene (user rule)
New MCP utilities (magic, notebooklm-v2, OpenDesign) are SEPARATE servers, never
replacements. Keys live in env vars, never committed to config.yaml as literals.
