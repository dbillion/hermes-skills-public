---
name: blender-mcp-operations
description: Operate and troubleshoot Blender and the blender-mcp addon.
---

# Blender MCP Operations

Use when: setting up or fixing the `blender-mcp` addon, the `uvx blender-mcp` mcp-cli bridge, copying addons between Blender versions, diagnosing a distro Blender that crashes on launch or fails to enable addons with `No module named 'math'` / `_posixsubprocess` / `_struct` / `cattrs`, or making a specific Blender version the system default.

## Mental model: two ways Blender is installed on this box

- **Manual `/opt/blender`** (e.g. 5.0 alpha): self-contained — bundles its own Python (e.g. `python3.11`) and does NOT consult system PATH for Python. Robust; ignores uv/pyenv/conda shims.
- **Distro package `blender` (pacman, e.g. 5.2 LTS in `extra`)**: at `/usr/bin/blender`, built against the **system Python** (Arch's current default, e.g. 3.14). Needs system python packages and is vulnerable to PATH/python hijacks.

`which -a blender` + the symlink chain shows which wins. `/usr/local/bin` and `~/.local/bin` are usually ahead of `/usr/bin` on PATH, so a symlink there overrides the distro binary.

## Pitfall #1 — uv/pyenv Python shadows the system Python (THE big one)

**Symptom:** distro Blender launches the GUI but EVERY addon fails to enable with `ModuleNotFoundError: No module named 'math'`, `'_posixsubprocess'`, `'_struct'`, or `import catts` fails inside Blender even though the package is installed. The traceback names a path like `/some/uv/python/cpython-3.14.2.../lib/python3.14/...`.

**Root cause:** a `python3.X` symlink in `~/.local/bin` (or `/usr/local/bin`) points at a uv/pyenv-managed Python that sits **ahead of `/usr/bin` on PATH**. Blender resolves `python3` → that shim → an incomplete/broken Python build missing stdlib modules. The manual `/opt` Blender is immune; the distro one dies.

**Diagnosis:**
```
ls -la ~/.local/bin/python3.* /usr/local/bin/python3.*
readlink -f ~/.local/bin/python3.14
PATH="$HOME/.local/bin:$PATH" python3.14 --version   # what blender sees
/usr/bin/python3.14 --version                          # the correct one
```
If the first `python3.14` is a symlink into `~/.local/share/uv/...` and Blender's traceback names that uv path → confirmed.

**Fix (no sudo, reversible):** rename the shadowing shim so the system python wins, keeping uv available under a different name:
```
mv ~/.local/bin/python3.14 ~/.local/bin/python3.14-uv
```
Then RESTART Blender (running instances keep the old Python). This pattern applies to ANY tool that suddenly can't find stdlib modules — check for a `pythonX.Y` shim ahead of `/usr/bin` on PATH first.

## Pitfall #2 — missing system Python deps for distro Blender

Distro Blender's *core* modules (e.g. the remote asset-library downloader `_bpy_internal/http/downloader.py`) import packages like `cattrs`. On Arch these come from `python-cattrs` (pacman), NOT pip. If `pacman -Q python-cattrs` is empty, Blender throws `No module named 'cattrs'` during addon enable.
- Correct fix: `sudo pacman -S python-cattrs` (distro-approved; avoids PEP 668 `--break-system-packages`).
- Plain `pip install --user` is blocked by PEP 668 on Arch's system python.

## blender-mcp addon: lifecycle

- The addon is **ahujasid/blender-mcp**, NOT pacman-managed. It lives in `~/.config/blender/<version>/scripts/addons/blender_mcp.py`.
- **Update it with:** `uvx blender-mcp install-addon` — fetches the current protocol version and writes it into the DEFAULT Blender's config dir. After: Preferences → Add-ons → disable "Blender MCP" → re-enable → Start MCP Server.
- **Copy between versions:** `cp ~/.config/blender/5.0/scripts/addons/blender_mcp.py ~/.config/blender/5.2/scripts/addons/` makes it *present and register*, but leaves the old `ADDON_PROTOCOL_VERSION = 4`, so the `uvx blender-mcp` bridge warns "addon on disk is outdated" and Poly Haven/Sketchfab tools may not respond. Prefer `uvx blender-mcp install-addon` for a real update.
- **Verify registration headless:** `blender --background --python-expr "import bpy; bpy.ops.preferences.addon_enable(module='blender_mcp'); print('REGISTERED', 'blender_mcp' in bpy.context.preferences.addons)"`
- The addon's `bl_info` `blender` field is `(3, 0, 0)` with no upper cap → forward-compatible across versions; only the file must be re-added per major version dir.

## Stale third-party addons breaking on newer Python

Old addons like `polyhavenassets` (Poly Haven Asset Browser) and `sketchfab-plugin-1-6-1` use `addon_updater_ops.make_annotations` which throws `KeyError: '__annotations__'` on Python 3.10+. They are NOT pacman-owned (manually dropped into addons/) so `pacman -Syu` never updates them. A "Poly Haven annotation error" is this stale addon, NOT blender_mcp. Move it aside:
```
mkdir -p ~/.config/blender/<ver>/scripts/addons.disabled
mv ~/.config/blender/<ver>/scripts/addons/polyhavenassets ~/.config/blender/<ver>/scripts/addons.disabled/
```
`blender_mcp` has its OWN Poly Haven/Sketchfab integration — no separate browser addon needed.

## Making a version the default (no sudo for the shim)

`/usr/local/bin/blender` is root-owned (can't edit without sudo). `~/.local/bin` is yours and is first on PATH. To default `blender` → distro 5.2:
```
ln -sf /usr/bin/blender ~/.local/bin/blender
```
Per-version config dirs (`~/.config/blender/5.x/`) are created fresh on first launch of that version; the MCP addon must be re-added per major version. Before removing an old install, confirm every addon file from the old version exists in the new one (active or safely stashed in `addons.disabled/`).

## Diagnostic checklist (run in order)
1. `blender --version` (which binary, which version)
2. `which -a blender` + `readlink` the winning one
3. `ls -la ~/.config/blender/` (which version dirs exist)
4. `ss -ltnp | grep 9876` (is the MCP addon server listening? which pid?)
5. `pacman -Q python-cattrs` (distro python dep present?)
6. Check `~/.local/bin/python3.*` shims vs `/usr/bin/python3.*` (hijack check)

See `references/arch-python-hijack.md` for full error transcripts and the exact reproduction recipe.
