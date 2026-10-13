# Skill + CLI Sync: host (deeone) → champion node

Keep the node's Hermes/OpenClaw environment in sync with the host: same skills, plus the
three CLIs `scrapling`, `agent-reach`, `opencli`.

## Skill store locations (verified this session)
- **HOST** real skills: `~/.agents/skills` (465 dirs). Host's `~/.hermes/skills` is a mix of
  real dirs + symlinks pointing into `~/.agents/skills`.
- **NODE** real skills: `~/.hermes/skills` (~642 entries; ~594 real dirs + symlinks). The node's
  `~/.agents/skills` had only **60** — DO NOT diff against it or you'll badly undercount the gap.
- **Therefore:** to find skills the node is MISSING, diff `host ~/.agents/skills` names vs
  `node ~/.hermes/skills` names.

## Skill sync procedure (additive — never delete)
1. Compute the missing set (Python, not `comm`, to avoid locale-sort pitfalls):
   ```python
   import subprocess
   host = set(subprocess.run(["ls","-1","/home/deeone/.agents/skills"],capture_output=True,text=True).stdout.split())
   node = set(subprocess.run(["ssh","champion","ls -1 ~/.hermes/skills"],capture_output=True,text=True).stdout.split())
   missing = sorted(host - node)
   ```
2. rsync each missing real dir as a REAL DIR into the node (its `~/.hermes/skills` convention is
   real dirs, not links):
   `rsync -a ~/.agents/skills/<name>/ champion:~/.hermes/skills/<name>/`
3. Preserve node-only skills (177 of them) — never delete.
4. Verify zero missing:
   `comm -23 <(ls -1 ~/.agents/skills|sort) <(ssh champion 'ls -1 ~/.hermes/skills'|sort)` → expect 0.

## CLI install on the node (Arch Linux — PEP 668 externally-managed)
`python3 -m pip` AND `ensurepip` fail with `externally-managed-environment`. Use a venv:

```sh
ssh champion 'mkdir -p ~/.local/bin ~/.venvs
python3 -m venv ~/.venvs/tools
~/.venvs/tools/bin/pip install --quiet --upgrade pip
~/.venvs/tools/bin/pip install "scrapling[shell]" agent-reach
~/.venvs/tools/bin/scrapling --version   # needs [shell] extra for click
ln -sf ~/.venvs/tools/bin/scrapling  ~/.local/bin/scrapling
ln -sf ~/.venvs/tools/bin/agent-reach ~/.local/bin/agent-reach'
```

- `scrapling` installed WITHOUT an extra → `ModuleNotFoundError: No module named 'click'` at
  `--version`. Fix: install `scrapling[shell]`. The `[cli]` extra does **not** exist in 0.4.x
  (warning: "does not provide the extra 'cli'").
- `agent-reach` installs and runs fine from pip.

### opencli (Node)
- `npm i -g opencli` → **404 Not Found** (bare `opencli` is not a public name). The real package
  is scoped: **`@jackwener/opencli`**.
  ```sh
  ssh champion 'npm config set prefix ~/.npm-global
  npm install -g @jackwener/opencli
  ln -sf ~/.npm-global/bin/opencli ~/.local/bin/opencli'
  ```
### Why symlink into ~/.local/bin (not edit ~/.bashrc)
The node's `~/.bashrc` already puts `~/.local/bin` on PATH. Symlinking the npm/venv binaries
there makes them resolve in a **fresh login shell** (`bash -lc "which opencli"`). Avoids editing
`~/.bashrc` — an append/redirect there (`>> ~/.bashrc`) and `bash -lc` can trip a safety guard and
get the command blocked.

## Verification (fresh login shell)
```sh
ssh champion 'bash -lc "scrapling --version; agent-reach --version; opencli --version"'
# expect: Scrapling, version 0.4.15 / agent-reach usage line / 1.8.7
```
