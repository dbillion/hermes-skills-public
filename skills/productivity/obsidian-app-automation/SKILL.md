---
name: obsidian-app-automation
description: "Drive a running Obsidian app: CLI, REST, plugin state."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [obsidian, cli, plugins, excalidraw, automation]
---

# Obsidian App Automation

For driving a **running Obsidian instance** — querying plugin state, installing
libraries, executing commands. Complements the bundled `obsidian` skill, which
covers filesystem-first note reading/writing.

Use this one when the question is *"is Obsidian actually seeing this?"* rather
than *"what's in this file?"*

## Three access paths

| Path | Endpoint | Best for |
|---|---|---|
| Official CLI | `obsidian` binary (IPC) | Richest: vaults, files, tasks, plugins, `eval` |
| Local REST API plugin | `http://127.0.0.1:27123` | HTTP/scripted access; also speaks MCP |
| Filesystem | vault dir | Bulk writes; but app/plugins may not notice |

## Detecting the CLI — the trap

**Never conclude "there is no Obsidian CLI" without testing the bare `obsidian`
binary.** Real miss: a session checked `obs` and `obsidian-cli`, found `obs` was
**OBS Studio** (video streaming — unrelated software that merely shares a
prefix), and reported no CLI existed. `/usr/bin/obsidian` was installed the
whole time and worked on first try. The user had to correct it.

```bash
which obsidian     # the ONLY authoritative check
obsidian version   # e.g. 1.13.4 (installer 1.12.7)
obsidian vault     # name / path / files / folders / size
```

Generalised lesson: when probing for a CLI, test the **exact expected binary
name** before testing abbreviations, and confirm any hit is the right product
(`cat` the wrapper, or check `--help` output) before ruling it in *or* out.

## Operating rules

- Obsidian must be **running** — the CLI talks over IPC.
- `vault=<name>` must be the **FIRST** argument to target a specific vault.
- Linux stderr noise `vaInitialize failed: unknown libva error` is a harmless
  GPU warning, not a failure. Pipe stderr to `/dev/null` in scripts.
- `obsidian reload` can **terminate** the app rather than reloading it. Avoid it
  in scripts; if used, verify the app is still up (`pgrep`, or re-run
  `obsidian vault`) and relaunch via `terminal(background=True)` if not.

## Disk state ≠ app state (the core discipline)

A file existing in the vault does **not** mean Obsidian or a plugin loaded it.
When asked *"how many are active?"*, answer from **plugin state**, never from a
directory listing — they are different claims, and conflating them produces a
confidently wrong answer.

Two verification tools:

```bash
# 1. Obsidian's own file index.
#    GOTCHA: returns NOTHING for non-markdown files unless you pass ext=.
#    A silent empty result reads like "not installed" when files are present.
obsidian files folder="Excalidraw/Libraries" ext=excalidrawlib

# 2. Live plugin state — the authoritative answer.
obsidian eval code="(()=>{ /* inspect app.plugins.plugins[...] */ })()"
```

`eval` is the escape hatch whenever config files disagree with observed
behaviour. Discover the real API by walking the prototype chain rather than
guessing method names:

```bash
obsidian eval code="JSON.stringify(Object.getOwnPropertyNames(app.plugins.plugins['<id>'].someManager||{}))"
```

Guessed names fail silently or return empty output — enumerate first.

## Installing Excalidraw stencil libraries

Detailed, verified recipe: `references/excalidraw-libraries.md`.

Headline pitfall: dropping `.excalidrawlib` files into the library folder makes
them **visible but inactive**. The plugin reads exactly one file, named by
`libraryFileName` in its `data.json`. Files must be merged into it.

## Pitfalls

- Reporting "confirmed visible" after checking only the file index. That
  verifies file visibility, not feature activation. Say which one you checked.
- Editing a plugin's managed file without a backup — it may rewrite it.
- Assuming a config key like `library2` reflects reality; in some storage modes
  it is unused and reads `0` while the feature is fully loaded.
