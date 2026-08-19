---
name: cli-tool-wrapping
description: Alias colliding CLI; dodge the symlink-clobber write.
version: 1
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [cli, symlink, alias, node, packaging, devops]
    related_skills: [hermes-agent, devops-golang-track]
---

# CLI Tool Wrapping & Symlink Safety

## When to use
- A tool you're setting up installs a binary whose name collides with an existing system command. Most common real case: **Open Design's `od` CLI vs GNU coreutils `od` at `/usr/bin/od`**.
- You need a callable name for a tool without shadowing the system binary.
- You are creating a wrapper script or symlink that points at (or through) a symlink.
- You must force a specific runtime (e.g. Node 24) regardless of the default `node` on PATH.

## User-endorsed pattern: alias + symlink to a non-colliding name
Do NOT overwrite or shadow the system binary. Give the tool its own name:
1. Pick a collision-free name (e.g. `opendesign` for Open Design's `od`).
2. Put a wrapper or symlink at `~/.local/bin/<name>` (confirm `~/.local/bin` is on PATH: `case ":$PATH:" in *":/home/deeone/.local/bin:"*) echo YES;; esac`).
3. Leave the system binary (`/usr/bin/od`) untouched.

This is the user's explicit instruction: *"alias and symlink it to connect it to avoid name collision."* It works — the tool becomes callable as `opendesign`, coreutils `od` stays intact.

## CRITICAL PITFALL — the file writer follows symlinks and clobbers the real target
The agent's `write_file` (and similar write actions) **resolve symlinks to their final target and overwrite THAT file**. It does NOT create/replace the symlink itself.

### Verified incident (this session)
While creating `~/.local/bin/opendesign` as a wrapper, that path was already a symlink I had just made:
`~/.local/bin/opendesign` → `node_modules/.bin/od` (symlink) → `apps/daemon/bin/od.mjs` (the REAL source).
Writing the wrapper text to `~/.local/bin/opendesign` followed the whole chain and **corrupted `od.mjs`** with wrapper content, so every `od`/`opendesign` invocation hung (`exec` of a shell script as if it were an `.mjs`). The write result even reported `resolved_path: .../apps/daemon/bin/od.mjs`, confirming the clobber.

### How to avoid
- NEVER `write_file` to a path that is (or resolves through) a symlink to a file you must not overwrite.
- Before writing a wrapper: if a symlink already occupies the target, `rm` the symlink FIRST, then `write_file` the real wrapper file as a plain file, then re-create any symlinks you need elsewhere.
- If you corrupted a tracked source this way, restore it from VCS: `git checkout -- <file>` (it's tracked), then re-link `node_modules/.bin/<bin>` → the real entry.
- Diagnose with `sh -x <wrapper>` — it shows exactly what gets exec'd and surfaces a clobbered entrypoint fast.

### Verifying a wrapper is safe & correct
- `sh -x /path/to/wrapper --help` — trace what it execs.
- Test from an arbitrary cwd with a stripped PATH to prove it forces the right runtime regardless of defaults: `PATH="/usr/bin:/bin:/home/deeone/.local/bin" wrapper --help`.
- Confirm the system binary is untouched: `command -v od` → still `/usr/bin/od`; `od --version` → coreutils, not the tool.

## Wrapper template (forces a specific runtime, avoids collision)
```sh
#!/bin/sh
# Forces the runtime the tool requires; does NOT collide with system `od`.
NODE24=/home/deeone/.nvm/versions/node/v24.19.0/bin
export PATH="$NODE24:$PATH"
exec /abs/path/to/REAL/entrypoint "$@"
```
- Point `exec` at the **real, restored entrypoint** (e.g. `apps/daemon/bin/od.mjs` or the package's `bin` field target), NOT a `node_modules/.bin` symlink you might also be editing.
- Find the real entry: `grep -E '"bin"' package.json` (repo root) or `apps/<app>/package.json`; for Open Design it is `apps/daemon/bin/od.mjs` and the repo-root bin maps `"od": "./apps/daemon/bin/od.mjs"`.

## Keep system binaries intact — final check
Always confirm: `od --version` → `od (GNU coreutils) 9.11`, and the tool is reachable only via its alias (`opendesign --help`).
