---
name: python-dependency-management
category: software-development
description: |
  Best practices for managing Python dependencies, including virtual environments,
  package installers (pip, uv, poetry), and locking reproductions.
  Emphasizes using uv for fast installations when available.
version: "0.1.0"
author: Hermes Agent
tags: [python, pip, uv, poetry, virtualenv, dependencies]
---

# Python Dependency Management Skill

## Why
Consistent, reproducible Python environments reduce friction across sessions and agents.
Using uv can dramatically speed up package installs while maintaining compatibility
with pip workflows.

## Prerequisites
- Python 3.8+ installed.
- Optionally install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or via package manager).
- Ensure `~/.local/bin` is in your `$PATH`.

## Recommended Workflow

1. **Create a dedicated virtual environment** for each project or toolset.
   ```bash
   python -m venv /path/to/venv
   source /path/to/venv/bin/activate
   ```

2. **Prefer uv for installations** when speed matters.
   ```bash
   uv pip install <package>          # same syntax as pip
   uv pip install -r requirements.txt
   ```
   uv respects the active virtual environment and uses the same resolver as pip,
   but is typically 2-10× faster.

3. **Lock dependencies** for reproducibility.
   ```bash
   uv pip compile requirements.in -o requirements.txt
   # or with pip-tools if preferred
   ```

4. **Upgrade safely**.
   ```bash
   uv pip list --outdated
   uv pip install -U <package>
   ```

5. **Cache and reuse**.
   uv automatically caches downloads in `~/.cache/uv`. To share caches across
   containers, mount that directory.

## Pitfalls
- Do **not** mix `pip` and `uv` in the same environment without awareness;
  they can interfere with each other's lock files. Pick one installer per
  environment and stick to it.
- Some packages rely on pip-specific features (e.g., `--no-binary` with complex
  markers); test after switching.
- Remember to activate the venv before running any tool that expects the
  installed packages (e.g., `theHarvester`, `sherlock`).

## Verification
After installing, check that the package is importable:
```bash
python -c "import theHarvester; print(theHarvester.__version__)"
```

## References
- uv documentation: https://docs.astral.sh/uv/
- Python packaging guide: https://packaging.python.org/
- See `references/uv-vs-pip.md` for a quick comparison table.