---
name: colab-operator
description: Operate Google Colab environments via the `colab` CLI from googlecolab/google-colab-cli — provision GPU/TPU sessions, run Python/shell on a remote VM, sync files, automate setup, export history as Jupyter notebook. Use when the user wants to create/manage Colab notebooks or run code on Colab VMs.
---

# Colab Session Operator

**Source:** `google-colab-cli` skill (`colab-operator`)
**CLI:** `colab` (install via `uv tool install google-colab-cli` or `pip install google-colab-cli`)

## Mental Model (Critical)
- **A session == a live Jupyter kernel on a rented VM.** `colab new` allocates a billable VM; `colab stop` releases it. 24h keep-alive cap — unstopped sessions burn compute.
- **Kernel state PERSISTS** across `colab exec`/`repl` in same session (kernel ID cached locally; websocket closes but kernel stays up). Imports/vars/functions survive. Reset only via `colab stop` or `colab restart-kernel`.
- **Default working dir is `/content`.** All `exec`/`repl`/`run` cd there first; use absolute `/content/...` paths. `ls`/`rm`/`upload`/`download` default to VM root `content`.
- **`colab` is fire-and-forget.** Each command auths, does one thing, exits. Detached daemon (from `colab new`) handles keep-alive.

## Authentication
- Global flag: `--auth={adc,oauth2}`, **default `adc`**, must precede subcommand: `colab --auth=adc new -s x`
- **ADC setup** (best for headless/agents) — re-mint with all four scopes:
  ```bash
  gcloud auth application-default login \
    --scopes=openid,\
  https://www.googleapis.com/auth/cloud-platform,\
  https://www.googleapis.com/auth/userinfo.email,\
  https://www.googleapis.com/auth/colaboratory
  ```
  - `userinfo.email` → backend `colab.research.google.com` (else 401)
  - `colaboratory` → RuntimeService keep-alive (else 403)
  - `openid`+`cloud-platform` → mandated by gcloud
- **oauth2:** browser flow on first use; token at `~/.config/colab-cli/token.json`; needs client config `~/.colab-cli-oauth-config.json` (or `-c PATH`). Prefer ADC for agents.
- **Verify:** `colab sessions` (read-only) or `colab whoami` (prints email/scopes/audience/expiry). 403 on `colab.pa.googleapis.com` = missing scope.
- `colab new` pre-flights keep-alive RPC; lacks `colaboratory` scope → unassigns VM + prints fix.
- `colab auth` ≠ CLI auth. It injects VM-side GCP creds for in-kernel GCS/BigQuery. Never use it to fix CLI 401/403.

## Workflow

### Provision
- `colab new -s <name>` (CPU). Accelerators: `--gpu A100`, `--tpu v6e1`. **Always pass `-s`** (omit → random 6-hex, ambiguous).
- GPUs: `T4`, `L4`, `G4`, `H100`, `A100`. TPUs: `v5e1`, `v6e1`.
- Gotcha: bad `--gpu` silently falls back to **A100** (then fails). `400` = no quota → use `T4` or CPU. Most accounts CPU-only.

### Execute
- Preferred: `colab exec -s <name> -f script.py` (sent to kernel, no upload).
- Piped: `echo "print(1)" | colab exec -s <name>`
- Notebooks: `colab exec -s <name> -f nb.ipynb` → writes `_output.ipynb`. `# @title Foo` labels cell.
- Plots: PNG/JPEG intercepted; use `--output-image <path>`. Inline escapes suppressed when non-TTY.
- Shell: `echo "cmd" | colab console -s <name>` (tmux-wrapped, has control bytes; use `grep -a`). `exec` faster if no real shell.
- **Never run interactively from agent:** `repl`, `console`, `auth`, `drivemount` (TTY hang). `repl`/`console` accept piped stdin + EOF exit.

### Ephemeral Jobs (`colab run`)
- `colab run [--gpu T4] [--tpu v6e1] [--keep] [-s NAME] script.py [args...]` = new+exec+stop.
- Sets `sys.argv`, `__name__ == "__main__"`. `--keep` prevents teardown.
- Exit codes propagate (CPython: `sys.exit(N)` → N).
- Streams: `[colab]` chatter → stderr; script stdout → stdout. `colab run job.py > out.txt` captures only script stdout.
- Shebang: `#!/usr/bin/env -S colab run --gpu T4` (reinstall CLI after edits).
- Nonexistent script → non-zero exit before VM alloc.

### Automate
- `colab auth -s <name>` — VM-side GCP creds (interactive)
- `colab drivemount -s <name> [PATH]` — mounts Drive at `/content/drive` (interactive)
- `colab install -s <name> pkg1 pkg2` — `uv pip install --system` → `pip` fallback. Also `-r requirements.txt`

### Inspect & Report
- `colab help` / `colab help <cmd>`
- `colab sessions` — lists assignments, prunes stale; orphans show `[?]`
- `colab status [-s <name>]` — hardware, IDLE/BUSY, last exec
- `colab log -s <name> [-n 20] [-t TYPE]` — events; keep-alive errors show raw `response_body`
- `colab log -s <name> -o summary.ipynb` — export (also `.md`, `.txt`, `.jsonl`)
- `colab url -s <name>` — web UI URL for existing session (`--open` launches)
- `colab skill` / `colab readme` — print skill/README

## Safety
- **Always `colab stop -s <name>` when done.** `colab run` (no `--keep`) self-cleans.
- Local state: `~/.config/colab-cli/sessions.json` (settings `settings.json`, history `history/*.jsonl`). Don't hand-edit; delete sessions.json entry to forget a session.

## Generating notebooks FROM source files (this session's pattern)
To turn local `.md`/`.py` files into Colab notebooks in the account:
1. **Build valid `.ipynb` JSON locally** (nbformat 4). Don't rely on `colab log -o` — that exports *kernel history*, not arbitrary files.
   - `.md` → split on fenced ```python blocks into CODE cells (prose → markdown); `.py` → split on top-level `def `/`class ` into code cells.
   - **Append a runnable demo to every bare-definition code cell** (call with sample args + print, wrapped in try/except) so the implementation is visibly exercised — user requirement. (Reuse `scripts/md_to_colab_notebook.py`.)
   - Write `{"cells":[...], "metadata":{...}, "nbformat":4, "nbformat_minor":0}`.
2. `colab upload LOCAL.ipynb /content/NAME.ipynb` → lands in the session (verify with `os.path.exists` via `colab exec`).
3. **Downloaded copies are NOT valid JSON.** `colab download` returns Colab's wire format, not nbformat — re-downloading overwrites your good local original with an unparseable file. Keep the locally-built originals as the canonical artifact; treat `download` output as throwaway.
4. The uploaded notebooks live in the session only — they vanish when you `colab stop`. For durable storage you need Drive.

### MANDATORY: nbformat trailing-newline rule (cost a full debug cycle)
**Every `source` line EXCEPT the last must end with `\n`.** If you write `source: text.split("\n")`, the lines have NO trailing newline and **Jupyter/Colab merges adjacent lines into one** — e.g. `from contextlib import contextmanagerimport time@contextmanagerdef timer...` → `SyntaxError`. 
- This is INVISIBLE to a local test that does `"\n".join(lines)` then `compile()` — that test PASSES while the real notebook is broken.
- **Verify notebooks by ACTUALLY RUNNING them on the Colab VM**, not by local compile: `colab exec -s <name> -f notebook.ipynb` executes each cell in a real per-cell kernel and surfaces SyntaxErrors the local test hides. This is the only reliable check.
- Always build `source` through a `to_source(text)` helper (see `scripts/md_to_colab_notebook.py`) that appends `\n` to all-but-last lines.

## Drive persistence is HEADLESS-BLOCKED
- `drive.mount('/content/drive')` (in-kernel, piped via `colab exec`) **times out** — it requires an interactive browser auth click that can't happen headlessly. `colab drivemount` is likewise interactive/TTY-hang per the base skill.
- **Workaround:** start the session, then the USER must open the session URL and do the one Drive-auth click interactively, OR mount Drive themselves and copy the `.ipynb` files in. Until then, deliver the local valid `.ipynb` files as the artifact.
- Don't burn 120s+ waiting on `drive.mount` in a piped exec — it will time out. Surface the limitation and hand off the auth step.

## Pitfalls
- `colab exec` does not auto-upload local files; use `-f script.py` (sent inline) or `colab upload`.
- Notebook export via `colab log -o` captures kernel history, NOT arbitrary source files.
- `colab new` with no `-s` → random name, confusing.
- Mind the 24h keep-alive; stop sessions you're done with.
- **Upload filename typos are silent** — `colab upload ds_a_practice.ipynb` (typo) succeeds but the file on the VM won't match what you later check. Verify existence via `colab exec` `os.path.exists`, not by trusting the upload echo.
- **`cd` does NOT persist into the `colab` call in a multi-line shell command.** `cd /home/.../notebooks && colab upload foo.ipynb /content/foo.ipynb` re-created a session and reported "Local file 'foo.ipynb' not found" — the `cd` ran but `colab` started a fresh shell/subsession from the repo root. **Always pass ABSOLUTE local paths to `colab upload`** (e.g. `colab upload "$D/foo.ipynb" /content/foo.ipynb` where `D=/abs/path`). This fails-fast correctly instead of silently creating a new session with a missing file.
- **Loop-typo class of bug:** when iterating `for f in A B C; do colab upload "$f..."; done`, a single mistyped name (e.g. `ds_a_...` vs real `dsa_...`) uploads nothing and the verify step shows MISSING — but the upload echo is easy to miss in a 5-line loop. Verify ALL names post-loop with one `colab exec` existence check before `colab stop`.
- ADC is cleaner than oauth2 for agents but needs the 4 scopes above or you get 401/403.
- **nbformat trailing-newline bug (silent, breaks real Colab runs):** `source` lines built via `text.split("\n")` have NO trailing `\n`, so Jupyter/Colab MERGE adjacent lines → `SyntaxError`. A local `"\n".join()+compile()` test hides it (passes), but `colab exec -f nb.ipynb` on the VM catches it. Build `source` via `to_source()` (appends `\n` to all-but-last lines) and VERIFY by running on the VM, never by local compile alone.
- **Local `exec(compile(whole_notebook_as_one_string))` gives FALSE confidence.** It re-adds newlines and runs everything in one namespace, masking both the newline-merge bug AND cells that fail under per-cell execution. Use `colab exec -f` for real verification.
## Reproducible notebook builder
- `scripts/md_to_colab_notebook.py` — turn local `.md`/`.py` into Colab `.ipynb` with
  fenced-code→runnable code cells + auto-appended try/except **demo** calls (so the
  implementation is visibly exercised). Reusable for any "make me notebooks from these files" task.
