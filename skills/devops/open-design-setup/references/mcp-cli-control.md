# mcp-cli programmatic control for Open Design

Reusable pattern proven this session. OD must already be in `~/.mcp_servers.json`.

## Reusable driver: od-control.sh
```bash
#!/usr/bin/env bash
# Usage: od-control.sh {list|count|run "<prompt>" [skill] [plugin]|status <runId>}
set -euo pipefail
export PATH="/home/deeone/.nvm/versions/node/v24.19.0/bin:$PATH"
SRV=open-design
case "${1:-list}" in
  list)
    mcp-cli call "$SRV" list_plugins '{}' > /tmp/od_plugins.raw 2>/dev/null
    mcp-cli call "$SRV" list_skills  '{}' > /tmp/od_skills.raw 2>/dev/null
    echo "=== PLUGINS ==="; node /home/deeone/open-design/parse-od-list.js 8 title < /tmp/od_plugins.raw
    echo "=== SKILLS ===";  node /home/deeone/open-design/parse-od-list.js 8 name  < /tmp/od_skills.raw
    ;;
  count)
    mcp-cli call "$SRV" list_plugins '{}' > /tmp/od_plugins.raw 2>/dev/null
    mcp-cli call "$SRV" list_skills  '{}' > /tmp/od_skills.raw 2>/dev/null
    echo -n "plugins: "; node /home/deeone/open-design/parse-od-list.js 100000 title < /tmp/od_plugins.raw | head -1
    echo -n "skills:  "; node /home/deeone/open-design/parse-od-list.js 100000 name  < /tmp/od_skills.raw  | head -1
    ;;
  run)
    PROMPT="${2:?prompt required}"; SKILL="${3:-}"; PLUGIN="${4:-}"
    ARGS=$(node -e 'const a={prompt:process.argv[1]};if(process.argv[2])a.skill=process.argv[2];if(process.argv[3])a.plugin=process.argv[3];console.log(JSON.stringify(a))' "$PROMPT" "$SKILL" "$PLUGIN")
    echo "commissioning: $ARGS"
    mcp-cli call "$SRV" start_run "$ARGS" > /tmp/od_run.raw 2>/dev/null
    node /home/deeone/open-design/parse-od-list.js 1 id < /tmp/od_run.raw
    ;;
  status) mcp-cli call "$SRV" get_run "{\"runId\":\"${2:?runId required}\"}" 2>/dev/null | node -e 'const d=JSON.parse(require("fs").readFileSync(0,"utf8"));const t=JSON.parse(d.content[0].text);console.log("status:",t.status)' ;;
  *) echo "usage: $0 {list|count|run <prompt> [skill] [plugin]|status <runId>}"; exit 1 ;;
esac
```

## Robust parser: parse-od-list.js
Inline `node -e` chokes on the large list_* payloads (malformed-string / truncated
JSON). Use a file-based parser instead:
```js
const n = parseInt(process.argv[2]||"8",10);
const key = process.argv[3]||"title";
let raw=""; process.stdin.on("data",d=>raw+=d);
process.stdin.on("end",()=>{
  const outer=JSON.parse(raw); const inner=JSON.parse(outer.content[0].text);
  const list=inner.plugins||inner.skills||[];
  console.log("total:",list.length);
  list.slice(0,n).forEach(x=>console.log(" -",x.id,"|",x[key]||x.name||""));
});
```

## Pipe-truncation gotcha (important)
`mcp-cli call open-design list_plugins '{}' | node -e '...'` silently drops bytes
on responses >~60KB (the daemon returns ~275KB). The inline parser then fails with
`Unterminated string in JSON`. **Always redirect to a file first** (`> /tmp/x.raw
2>/dev/null`) then parse the file. This is why od-control.sh saves to
`/tmp/od_plugins.raw` before parsing.

## Notes
- `mcp-cli` subcommands are `info` / `grep` / `call` (not `list`). `mcp-cli list`
  errors with UNKNOWN_SUBCOMMAND.
- `start_run` returns a runId immediately; poll `get_run(runId)` until terminal.
  Project is optional and defaults to the OD project open in the GUI.
- Skills are driven via `start_run(skill=...)`, not invoked directly.
