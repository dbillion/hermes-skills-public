# Installing community Hermes plugins & skills from cloned repos

Pattern proven during the hermesatlas use-case bulk-install (2026-08-14). Use
this when you have a git repo on disk that is a Hermes plugin (`plugin.yaml`)
or skill (`SKILL.md`) and want to wire it into a running Hermes WITHOUT
`hermes skills install` (which only fetches from hubs/URLs).

## The local-install trap (learned the hard way)
`hermes plugins install <local-path>` treats the path as a repo URL to CLONE.
Passing a local directory makes it resolve to `https://github.com/<cwd-owner>.git`
and fail with "Repository not found". Do NOT use it for local dirs.

## Plugins: symlink into ~/.hermes/plugins/
```bash
ln -sfn /path/to/repo ~/.hermes/plugins/<name>
hermes plugins enable <name>
hermes plugins doctor <name>      # validates manifest + runtime contracts
```
- The symlink basename MUST match the plugin's internal `name:` in `plugin.yaml`,
  or `hermes plugins enable` reports "not installed or bundled".
  (e.g. repo dir `hermes-memlock` had `name: memlock` -> symlink must be `memlock`.)
- NEVER grant `--allow-tool-override` unless you explicitly want the plugin to
  intercept built-in tools (shell/file). Safe plugins need no override.
- `doctor` WARNs about hook/manifest mismatches are common in community plugins
  and non-fatal -- only ERRORs block.

## Skills: symlink each Hermes-shaped skill dir into ~/.hermes/skills/
```bash
ln -sfn /path/to/skill-dir ~/.hermes/skills/<uc-prefix>-<name>
```
- Namespace with a prefix (e.g. `uc01-`, `ts-`) so staged repos don't collide
  with bundled skill names.
- Bundled skill repos (youtube-skills, drawio-skill, super-hermes, the 817-entry
  Anthropic-Cybersecurity-Skills) keep their real SKILL.md files in a `skills/`
  SUBDIRECTORY, not the repo root. Hermes does NOT reliably recurse a bundled
  dir -- symlink EACH sub-skill individually:
  ```bash
  for d in /path/repo/skills/*/; do
    ln -sfn "$(realpath "$d")" ~/.hermes/skills/ts-$(basename "$d")
  done
  ```
- Lowercase `skill.md` is NOT auto-detected. If a repo uses `skill.md`, add an
  alias inside the repo (don't rewrite upstream): `ln -sfn skill.md SKILL.md`.
- Curated SUBSET over bulk: a 817-skill cybersecurity repo should NOT be linked
  in full (bloats the index you already have ~547 of). Link ~10-15 high-value
  skills, leave the rest staged on disk.

## Activation requirement (easy to forget)
New symlinks do NOT appear in `hermes skills list` / `hermes plugins list`
until the SKILL INDEX is rescanned. That happens at session/gateway START.
From a gateway-connected session you often CANNOT restart the gateway (the
gateway is the parent process); the user must run `hermes gateway restart`
from a separate real terminal. Tell them explicitly -- don't claim a skill is
"live" until after that restart.

## Safe-route bulk pattern (for "implement all the things")
1. Clone all target repos first (shallow `--depth 1`) into one staging dir.
2. Classify each: SKILL (has SKILL.md) / PLUGIN (has plugin.yaml) /
   APP (package.json/pyproject/go.mod) / other.
3. Register only SKILLs + PLUGINs (symlink + enable + doctor).
4. Stage APPs/others as reference (need builds / external services / mobile /
   GPU) -- do NOT auto-install those; flag per-repo what they need.
5. Report live-vs-staged honestly; never claim an app "done" when only cloned.
