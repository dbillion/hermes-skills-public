# Open Design (`od`) CLI — setup notes

Open Design (nexu-io/open-design) is a local-first design studio + agent runtime.
Its CLI binary is named `od`, which collides with GNU coreutils `od`.

## Install location on this machine
- Repo clone: `/home/deeone/open-design/open-design`
- Real CLI entry: `apps/daemon/bin/od.mjs` (shebang `#!/usr/bin/env node`)
- Repo-root bin maps `"od": "./apps/daemon/bin/od.mjs"`
- Runtime: Node 24 (nvm: `/home/deeone/.nvm/versions/node/v24.19.0`). Default `node` on PATH is v25.6.1 — must NOT be used.
- Alias wrapper (collision-free): `/home/deeone/.local/bin/opendesign`

## Connect to agents (MCP adapters)
```
opendesign mcp install hermes      # wires OD MCP into Hermes
opendesign mcp install --help      # list all adapters (claude, codex, cursor, opencode, ...)
opendesign mcp install <agent> --print   # dry-run preview
opendesign mcp install <agent> --uninstall
```

## Gotcha: `write_file` follows symlinks
Writing a wrapper to a path that was a symlink chain clobbered the real
`apps/daemon/bin/od.mjs`. If `od`/`opendesign` ever hangs, restore the source:
```
cd /home/deeone/open-design/open-design
git checkout -- apps/daemon/bin/od.mjs
rm -f node_modules/.bin/od
ln -s "$PWD/apps/daemon/bin/od.mjs" node_modules/.bin/od
```

## Sanity checks
- `opendesign --help` prints usage from any cwd.
- `od --version` still reports `od (GNU coreutils) 9.11` (untouched).
