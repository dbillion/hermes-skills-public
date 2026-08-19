# hatchling + `uv build` produces an EMPTY wheel

## Symptom
`uv build --wheel` succeeds ("Successfully built ...") but the `.whl` contains
only `bin/<script>` and `*.dist-info` — NONE of your package's `.py` files.
Installing it yields `ModuleNotFoundError: No module named '<pkg>'`.

## Root cause
hatchling's `packages = ["<pkg>"]` looks for `./<pkg>/` at the project root.
If your modules (`client.py`, `cache.py`, `cli.py`, ...) sit at the **project
root** instead of inside `<pkg>/`, hatchling finds nothing and builds an empty
wheel. This is silent — no error, just an empty artifact.

A tell-tale sign: a failed `mv <pkg> src/<pkg>` earlier left modules at root
while you assumed they'd been nested.

## Fix
Put the modules INSIDE the package directory:
```bash
mkdir -p tgforwarder
mv cache.py client.py cli.py forward.py score.py tgforwarder/
# (and ensure tgforwarder/__init__.py exists)
```
Then rebuild:
```bash
rm -rf dist
uv build --wheel
python -c "import zipfile,glob; w=sorted(glob.glob('dist/*.whl'))[-1]; \
  print([n for n in zipfile.ZipFile(w).namelist() if n.endswith('.py')])"
# must list your modules, not just __init__.py / dist-info
```

## Editable install gotcha
`uv pip install -e .` may still report the package but not write the console
script to `.venv/bin/`. Verify with `python -c "import <pkg>"`. If missing,
reinstall with `--no-build-isolation` after `uv pip install hatchling`. The real
`tgf` binary appears when installed from the (correct) wheel via `uv tool install .`
or `uv pip install --target /tmp/x dist/*.whl` (check `ls /tmp/x/bin`).
