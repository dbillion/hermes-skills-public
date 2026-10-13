# Local plugin / skill / MCP install recipes (verified)

Concrete commands that worked during the atlas use-case rollout. These are the
"how" behind the pitfalls in SKILL.md.

## 1. Install a locally-cloned repo as a Hermes PLUGIN
`hermes plugins install <local-path>` FAILS (it git-clones the path as a URL):
  Error: Git clone failed: ... github.com/<user>.git/ ... Repository not found
Correct path — symlink into ~/.hermes/plugins using the plugin's INTERNAL name:
  # find the internal name from plugin.yaml:  name: memlock
  ln -sfn /path/to/cloned/repo /home/deeone/.hermes/plugins/memlock
  hermes plugins enable memlock
  hermes plugins doctor memlock      # WARNs about hook manifest mismatch = benign
Note: the symlink name MUST equal the manifest `name:` (e.g. `memlock`, not
`hermes-memlock`) or `hermes plugins enable` reports "not installed or bundled".

## 2. Register a cloned repo as a SKILL
Hermes does NOT recurse a symlinked bundle dir. Symlink EACH skill individually:
  # bad:  ln -sfn repo/skills  ~/.hermes/skills/uc10-youtube-skills   (stays undetected)
  # good: one symlink per sub-skill
  for d in repo/skills/*/; do
    n=$(basename "$d"); ln -sfn "$(pwd)/$d" "/home/deeone/.hermes/skills/uc10-yt-$n"
  done
Hermes only reads `SKILL.md` (uppercase). If the repo ships lowercase `skill.md`:
  ln -s skill.md SKILL.md          # inside the repo dir (alias, no content change)
Verify: hermes skills list | grep <name>

## 3. Add an MCP server via hermes config set (AVOID the stringify trap)
BAD — stores the whole object as a string; `hermes mcp list` crashes and server
never connects:
  hermes config set mcp_servers.meigen '{"command":"npx",...}'   # becomes a 'str'
GOOD — set sub-keys so a real dict is built:
  hermes config set mcp_servers.meigen.command "npx"
  hermes config set mcp_servers.meigen.args '["-y","meigen@1.4.0"]'
  hermes config set mcp_servers.meigen.env '{"MEIGEN_API_TOKEN":"meigen_sk_..."}'
  hermes config set mcp_servers.meigen.timeout "2700"
  hermes config set mcp_servers.meigen.connect_timeout "120"
Verify the entry is a dict (not str):
  python3 -c "import yaml;d=yaml.safe_load(open('/home/deeone/.hermes/config.yaml'));
  print(type(d['mcp_servers']['meigen']).__name__)"   # must print 'dict'

## 4. Activation timing
New skills (step 2), plugins (step 1), and MCP servers (step 3) are scanned ONLY
at gateway/session start. After registering all of them, ONE restart activates
everything:
  hermes gateway restart            # from a real terminal, NOT inside a connected session
  # fallback if blocked: systemctl --user restart hermes-gateway

## 5. Smoke-test an MCP server directly (before relying on Hermes)
  printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{
    "protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"p","version":"1"}}}' \
   | timeout 40 npx -y meigen@1.4.0 2>/dev/null | head -c 200
  # Expect: {"result":{"serverInfo":{"name":"meigen","version":"1.4.0"},...}}
  # A clean handshake with no auth error proves the token validates.
