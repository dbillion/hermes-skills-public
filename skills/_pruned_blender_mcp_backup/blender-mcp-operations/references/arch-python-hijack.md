# Arch Python Hijack — Error Transcripts & Reproduction

This file captures the real failure signatures from a Blender 5.2 (distro, pacman)
session where a uv-managed Python shadowed the system Python. Use it to confirm
the diagnosis fast instead of re-deriving it.

## Environment that exhibited it
- Distro: EndeavourOS (Arch-based), user `deeone`, home `/home/deeone`.
- System Python: `/usr/bin/python3.14` = 3.14.7 (correct, complete).
- uv store: `/home/deeone/.local/share/uv/python/cpython-3.14.2-linux-x86_64-gnu/`.
- Shadows: `~/.local/bin/python3.14` -> uv 3.14.2, and `~/.local/bin` was FIRST on PATH.

## Signature #1 — `python3` resolves to uv, missing stdlib
```
$ PATH="$HOME/.local/bin:$PATH" python3.14 --version
Python 3.14.2          # <- wrong one; blender picks this up

$ /usr/bin/python3.14 --version
Python 3.14.7          # <- the real system one
```

## Signature #2 — Blender launches but addons die on enable
Blender GUI opens (C++ core runs), but enabling ANY addon fails. Traceback tail:
```
File ".../uv/python/cpython-3.14.2-linux-x86_64-gnu/lib/python3.14/subprocess.py", line 106, in <module>
    from _posixsubprocess import fork_exec as _fork_exec
ModuleNotFoundError: No module named '_posixsubprocess'
...
ModuleNotFoundError: No module named 'math'
...
ModuleNotFoundError: No module named '_struct'
```
The `.../uv/python/cpython-3.14.2...` path in the traceback is the smoking gun:
Blender loaded uv's Python, not the system one.

## Signature #3 — even Cycles (bundled) crashes
```
File "/usr/share/blender/5.2/scripts/addons_core/cycles/__init__.py", line 142, in register
    from . import properties
File ".../cycles/properties.py", line 23, in <module>
    from math import pi
ModuleNotFoundError: No module named 'math'
```
Confirms it's environmental, not the addon's fault.

## Signature #4 — the "Poly Haven annotation error"
A DIFFERENT, stale addon (`polyhavenassets`, NOT blender_mcp) throws:
```
File ".../polyhavenassets/addon_updater_ops.py", line 93, in make_annotations
    annotations = cls.__dict__["__annotations__"]
KeyError: '__annotations__'
```
Caused by `addon_updater_ops.make_annotations` on Python 3.10+ when a class has
no explicit annotations. This is the "annotation error" users report — it is the
old Poly Haven Asset Browser addon, not blender_mcp.

## Signature #5 — core dep missing (after fixing the shim)
With the shim fixed, Blender still needed a system package:
```
File "/usr/share/blender/5.2/scripts/modules/_bpy_internal/http/downloader.py", line 51, in <module>
ModuleNotFoundError: No module named 'cattrs'
```
Fix on Arch: `sudo pacman -S python-cattrs` (NOT `pip install --user`, which
PEP 668 blocks on the system interpreter).

## Exact reproduction recipe
1. Put a `python3.14` symlink in `~/.local/bin` -> uv's 3.14.2 bin.
2. Ensure `~/.local/bin` precedes `/usr/bin` on PATH (typical in Arch shell rc).
3. Run distro Blender: `blender` -> GUI shows, addons fail with #2/#3.

## Exact fix (no sudo, reversible)
```
mv ~/.local/bin/python3.14 ~/.local/bin/python3.14-uv
# then RESTART Blender (running instances keep the old Python)
```

## Verification after fix
```
$ blender --background --python-expr "import bpy; bpy.ops.preferences.addon_enable(module='blender_mcp'); print('REGISTERED', 'blender_mcp' in bpy.context.preferences.addons)"
... BlenderMCP addon registered
REGISTERED True
```
