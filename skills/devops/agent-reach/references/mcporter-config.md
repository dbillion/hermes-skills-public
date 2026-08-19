# mcporter config fragmentation — the gotcha that burned a setup

## Symptom
`agent-reach doctor` reports a channel ok (e.g. linkedin), but a direct
`mcporter call linkedin.xyz` fails with: `Unknown MCP server 'linkedin'.`

## Root cause
`mcporter config add <name> <url>` resolves config files in this order:
1. A **cwd-relative** project config: `<current_dir>/config/mcporter.json`
2. A system config: `~/.mcporter/mcporter.json` (often missing)

When you run `mcporter config add` from a directory like a venv
(`/home/deeone/.venv/lib/python3.12/site-packages`), it writes
`<that_dir>/config/mcporter.json`. Meanwhile `agent-reach doctor` and the
nvm-provided node `mcporter` read the **HOME** project config at
`/home/deeone/config/mcporter.json`. So the server existed in the stray
config (doctor saw it via its own resolution), but the node `mcporter`
binary's `call` command looked in the home config and didn't find it.

## The fix
1. ALWAYS `cd ~` (or cd to the home project dir) before `mcporter config add`.
2. After adding, verify from `$HOME`: `mcporter config list` should list the
   server under "Project config: /home/deeone/config/mcporter.json".
3. Hunt down and delete stray copies:
   `find /home/deeone -maxdepth 4 -name mcporter.json` and remove any that
   aren't the intended home one.

## Which mcporter is which
- Node `mcporter` (from nvm): `/home/deeone/.nvm/versions/node/<ver>/bin/mcporter`
  — this is what `agent-reach` and the skill use.
- A pip-installed or venv-installed `mcporter` is a different binary and may
  write to a different project config. Prefer the node one for Agent Reach work.
- Run `mcporter config list` to see the resolved Project/System config paths
  for whatever binary you invoked — trust that output, not assumptions.
