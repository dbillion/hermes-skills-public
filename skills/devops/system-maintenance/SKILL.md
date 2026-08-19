---
name: system-maintenance
description: Procedures for analyzing and cleaning up system resources (disk space, memory, caches) to maintain optimal performance.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
tags: [maintenance, cleanup, disk-space, memory, cache, performance, devops]
---

# System Maintenance

This skill provides procedures for analyzing system resource usage and performing safe cleanup operations to free disk space and manage memory pressure.

## When to Use This Skill

- System reports low disk space (e.g., >85% usage)
- High swap usage indicating memory pressure
- Noticeable system slowdowns
- Routine maintenance to prevent issues
- After large operations that generate temporary files (builds, downloads, etc.)

## Disk Space Analysis

### Check Overall Disk Usage
```bash
df -h
```

### Find Largest Directories
```bash
# Check home directory subdirectories
du -sh ~/* 2>/dev/null | sort -hr | head -20

# Check specific cache directories
du -sh ~/.cache/ ~/.npm/ ~/.local/share/ 2>/dev/null | sort -hr
```

### Identify Large Files
```bash
# Find files >100MB in home directory
find ~ -type f -size +100M 2>/dev/null | head -20

# Find files >1GB in home directory
find ~ -type f -size +1G 2>/dev/null
```

## Safe Cache Cleanup Procedures

### Node.js/npm Cache
```bash
# Check npm cache size
du -sh ~/.npm 2>/dev/null

# Clean npm cache (use with --force if needed)
npm cache clean --force

# Alternative: verify cache integrity (safer but doesn't free space)
npm cache verify
```

### UV/Python Package Cache
```bash
# Check UV cache size
du -sh ~/.cache/uv 2>/dev/null

# Clean UV cache
uv cache clean
```

### Pip Cache
```bash
# Check pip cache size
du -sh ~/.cache/pip 2>/dev/null

# Clean pip cache
pip cache purge
# or for older pip versions
pip cache dir && rm -rf $(pip cache dir)
```

### Browser Automation Caches (Safe to Clear)
```bash
# Puppeteer
rm -rf ~/.cache/puppeteer/*

# Codex runtimes
rm -rf ~/.cache/codex-runtimes/*

# Camoufox
rm -rf ~/.cache/camoufox/*
```

### Browser Caches (Will Rebuild as Needed)
```bash
# Google/Chrome-based browsers
rm -rf ~/.cache/google/* 2>/dev/null; echo "Google cache cleared"
rm -rf ~/.cache/BraveSoftware/* 2>/dev/null; echo "Brave cache cleared"
rm -rf ~/.cache/chromium/* 2>/dev/null; echo "Chromium cache cleared"

# Chrome DevTools MCP (if used)
rm -rf ~/.cache/chrome-devtools-mcp/* 2>/dev/null
rm -rf ~/.cache/chrome-devtools-mcp/Code\ Cache/* 2>/dev/null
rm -rf ~/.cache/chrome-devtools-mcp/GPUCache/* 2>/dev/null
```

### Electron/Framework Caches
```bash
rm -rf ~/.cache/electron/* 2>/dev/null
rm -rf ~/.cache/copilot/* 2>/dev/null
```

## Memory and Swap Monitoring

### Check Memory Usage
```bash
free -h
# or
cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree"
```

### Check Swap Usage
```bash
swapon --show
# or
free -h | grep Swap
```

### Identify Memory-Heavy Processes
```bash
# Top processes by memory usage
ps aux --sort=-%mem | head -10

# Or use top/htop and sort by memory
```

## Disk Space Analysis Workflow

## Disk Space Analysis Workflow
`du` hangs indefinitely (exit 124, no output) on large or fragmented filesystems
even with a timeout. Do NOT keep retrying `du -sh /home` on a ~800GB tree —
it will burn every call and return nothing. Two reliable paths:

### Path A — full scan (slow but complete): `ncdu -x`
```bash
ncdu -o /tmp/ncdu.txt -x /path 2>&1 && echo "SCAN_DONE"
# notify_on_complete=true; poll with `ls -lh /tmp/ncdu.txt`
```
Then parse the compact JSON (see below). For the full system root,
`/var/lib/docker` etc. need sudo; prefer scanning `/home/deeone/...`
per-directory instead (Path B).

### Path B — targeted per-directory (FAST, use this first)
`du -h -d 1 <dir>` with a timeout works fine on a SINGLE directory
(one level only) — the hang only happens on deep traversal of a huge tree.
```bash
for dir in /home/deeone/.docker /home/deeone/.local/share \
            /home/deeone/Downloads /home/deeone/Desktop /tmp; do
    printf "%s  " "$(du -sh "$dir" 2>/dev/null | cut -f1)"; echo "$dir"
done
# then drill into the biggest: du -h -d 1 /home/deeone/.local/share | sort -rh
```
This is the fastest way to find top-level hogs without a full scan.

### `du` timeout failure mode (learned this session)
- A bare `du -sh ~` on a large home hangs past any `--timeout` and returns
  exit 130/124 with NO output. Do not loop on it.
- `ncdu -x ~` was the user-suggested fix that actually worked — use it
  for full-tree analysis, not `du`.
- Cross-reference `df -h /` (instant) to separate APPARENT vs ACTUAL disk
  usage. Loop devices like `~/.docker/Docker.raw` report huge apparent size
  but small real on-disk footprint.

For the full system root (requires sudo for /var/lib/docker):
```bash
ncdu -o /tmp/ncdu-full.txt -x / 2>&1 && echo "SCAN_DONE"
```

**Note**: Scanning `/.docker/Docker.raw` and similar large loop devices can inflate apparent sizes. Cross-reference `df -h /` to see actual disk usage.

### Parse ncdu Output

ncdu saves in a compact JSON format: `[version, flags, info_dict, root_item]`

```python
import json, re

with open('/tmp/ncdu.txt', 'r') as f:
    data = json.load(f)

# root_item = data[3]
# Structure: [name_dict, excluded_list, children_dict]
# children_dict: keys are dir names, values are child info dicts or nested lists
root = data[3]
name_dict = root[0]    # {'name': '/path', 'asize': N, 'dsize': N, 'dev': ...}
excluded = root[1]     # list of excluded mount points
children = root[2]     # dict of top-level entries

# For direct ncdu files (e.g., ncdu -o /tmp/ncdu.txt ~/):
# Each top-level item is a list: [name_str, size_or_nested, ...]
# Direct file scan approach:
entries = re.findall(r'\{"name":"([^"]+)","asize":(\d+)', raw_content)
```

### Quick Per-Directory Scan (No Full Traversal)

For targeted checks on specific dirs, `du -h -d 1` with a timeout is faster than a full ncdu scan:

```bash
du -h -d 1 /path 2>/dev/null | sort -rh | head -20
```

### Key Directory Sizes on Linux Home

On this system, typical sizes for a fully-loaded dev machine:

| Directory | Expected size | Notes |
|---|---|---|
| `~/.cache/` | <500MB | Browser + tool caches |
| `~/.local/share/` | 20-60GB | App data, package caches |
| `~/.local/share/pnpm/` | 1-3GB | pnpm global store |
| `~/.local/share/pipx/` | 500MB-2GB | Python isolated packages |
| `~/Downloads/` | varies | Big installers, Telegram desktop cache |
| `~/Desktop/` | varies | Media, PDFs |
| `~/.docker/` | 50GB+ | Docker loop images/containers |

### Docker Loop Device (`~/.docker/Docker.raw`)

On systems using Docker with a loop device file instead of a block device:
- File shows massive apparent size (hundreds of GB) but actual disk usage is much smaller
- Actual usage: `du -sh ~/.docker/Docker.raw`
- Clean with: `docker system prune -a` (wipes ALL images/containers — irreversible)
- Do NOT delete the file itself — it's the Docker data store

### Parse ncdu JSON (Streaming for Large Files)

For 300MB+ scan files, Python's `json.load()` may OOM. Use regex extraction instead:

```python
import re
with open('/tmp/ncdu-full.txt', 'r') as f:
    content = f.read()
# Extract all name+size pairs
entries = re.findall(r'\{"name":"([^"]+)","asize":(\d+)', content)
seen = {}
for path, size in entries:
    if path not in seen:
        seen[path] = int(size)
# Now sort and display
all_items = sorted(seen.items(), key=lambda x: x[1], reverse=True)
```

## Lesson Learned: Cron Job Model Validation

During this session, we discovered that several cron jobs were failing due to an invalid model ID:
- **Problem**: Jobs were configured with `model: "nvidia/nemotron-3-ultra"` which is not a valid model identifier
- **Solution**: Updated to use `model: "nvidia/nemotron-3-super-120b-a12b"` with provider `openrouter` 
- **Free Alternative**: For zero-cost usage, use `model: "nvidia/nemotron-3-super-120b-a12b:free"` via OpenRouter

To fix cron jobs with invalid model IDs:
1. Check job configuration: `cat ~/.hermes/cron/jobs.json | grep -A2 -B2 '"model":'`
2. Update invalid models: Replace `nvidia/nemotron-3-ultra` with `nvidia/nemotron-3-super-120b-a12b`
3. Ensure provider is set correctly (usually `openrouter` for NVIDIA models via OpenRouter)
4. Clear error states: Set `"last_status": "idle"` and clear `"last_error"` fields
5. Validate changes: `hermes cron list` should show jobs in `idle` state rather than `error`

### Verification Commands
```bash
# List all cron jobs and their status
hermes cron list

# Run a specific job immediately (if not locked by scheduler)
hermes cron run <job-id>

# Check job configuration for model/provider issues
grep -r "nvidia/nemotron-3-ultra" ~/.hermes/cron/  # Should return no results after fix
```
```bash
# Show disk usage
docker system df

# Clean unused objects (containers, images, networks, build cache)
docker system prune -f
# For more aggressive cleanup including unused images:
docker system prune -a -f

# Remove specific unused images
docker image prune -a
```

### Snap Packages (Ubuntu/Linux)
```bash
# List all snaps and their versions
snap list --all

# Remove disabled snap versions (safe cleanup)
sudo snap list --all | awk '/disabled/{print $1, $3}' |
    while read snapname revision; do
        sudo snap remove "$snapname" --revision="$revision"
    done
```

### Journal Logs (Systemd)
```bash
# Check journal size
journalctl --disk-usage

# Vacuum logs to retain only recent entries
sudo journalctl --vacuum-time=3days   # Keep last 3 days
# or
sudo journalctl --vacuum-size=500M    # Limit to 500MB
```

## Safe Cleanup Script

Here's a consolidated script for common safe cleanup operations:

```bash
#!/bin/bash
# safe-cleanup.sh - Perform safe system cleanup operations

echo "Starting system cleanup..."

# Clean package managers
echo "Cleaning npm cache..."
npm cache clean --force 2>/dev/null || echo "npm cache clean skipped"

echo "Cleaning UV cache..."
uv cache clean 2>/dev/null || echo "UV cache clean skipped"

echo "Cleaning pip cache..."
pip cache purge 2>/dev/null || echo "pip cache purge skipped"

# Clean browser automation caches (safe to delete)
echo "Cleaning puppeteer cache..."
rm -rf ~/.cache/puppeteer/* 2>/dev/null; echo "Puppeteer cache cleared"

echo "Cleaning codex-runtimes cache..."
rm -rf ~/.cache/codex-runtimes/* 2>/dev/null; echo "Codex runtimes cache cleared"

echo "Cleaning camoufox cache..."
rm -rf ~/.cache/camoufox/* 2>/dev/null; echo "Camoufox cache cleared"

# Clean browser caches
echo "Cleaning Google/Chrome caches..."
rm -rf ~/.cache/google/* 2>/dev/null; echo "Google cache cleared"
rm -rf ~/.cache/BraveSoftware/* 2>/dev/null; echo "Brave cache cleared"
rm -rf ~/.cache/chromium/* 2>/dev/null; echo "Chromium cache cleared"

# Show results
echo -e "\nCleanup complete. Current disk usage:"
df -h /
echo -e "\nTop 5 largest directories in ~/.cache:"
du -sh ~/.cache/* 2>/dev/null | sort -hr | head -5

echo "Cleanup finished."
```

**Note**: This script only clears caches that are safe to delete (they will automatically rebuild as needed). It does not touch user data, documents, projects, or other important files.

## Preventive Maintenance Recommendations

### Regular Cleanup Schedule
- **Weekly**: Run basic cache cleanup (npm, uv, pip caches)
- **Monthly**: Run full cleanup including browser caches
- **Quarterly**: Review large files and archives, consider archiving old data

### Monitoring Setup
Consider setting up simple monitoring:
```bash
# Add to crontab for weekly disk usage report
0 2 * * 0 df -h / | mail -s "Weekly Disk Usage Report" user@example.com

# Or log to file for later review
0 2 * * 0 df -h / >> ~/logs/disk-usage.log
```

### Application-Specific Tips
- Configure applications to use smaller cache sizes when possible
- Regularly clean download folders (`~/Downloads`)
- Use temporary directories (`/tmp`) for transient files and clean them periodically
- For development work, consider periodic cleanup of `node_modules`, `venv`, `__pycache__` directories in projects

## Safety Guidelines

### ✅ SAFE to Clear
- Application caches (`~/.cache/*`)
- Package manager caches (`~/.npm`, `~/.cache/uv`, `~/.cache/pip`)
- Browser automation caches (puppeteer, codex-runtimes, etc.)
- Browser caches (will rebuild automatically)
- Temporary files in `/tmp` (not in use)
- Build artifacts (`node_modules`, `dist`, `build`, `__pycache__` in projects)

### ⚠️ USE CAUTION with
- Log files (check if actively used before clearing)
- Docker images/containers (ensure you don't need them)
- Virtual machine images
- Backup archives

### ❌ NEVER CLEAR (hard rule above all others)
- User documents (`~/Documents`, `~/Desktop`, etc.)
- Project source code
- Configuration files (`~/.config/*`, `~/.ssh/*`, etc.)
- Database files
- Any data you cannot afford to lose
- **`~/.hermes/`** — that is the agent itself; only `npm prune` / `git gc` inside it, never `rm -rf`.
- **Docker VM / active containers** unless the user confirmed they don't need them.
- **Pre-existing cloud resources not created this session** (e.g. a live Cloud Run service from a
  prior date) — flag, don't delete.

## USER PREFERENCE — trash-first, never hard `rm -rf` (HARD RULE)
This user explicitly corrected the agent after it hard-deleted npm/pnpm/bun caches during a
"safe cleanup" pass. The rule, now standing:

> **NEVER `rm -rf` / hard-delete files without moving them to trash first — this applies to
> caches too.** Only hard-delete per explicit, per-item user approval after a consult.

- Move-to-trash path: `~/.local/share/Trash/files/`.
- The "Safe Cleanup Script" later in this skill uses `rm -rf` directly — **do NOT use that
  pattern for this user.** Replace every `rm -rf <cache>` with
  `mv <cache> ~/.local/share/Trash/files/`. Caches are regenerable, but the user wants the trash
  safety net regardless.
- This overrides the generic "SAFE to Clear" lists in this skill for THIS user.
- **Session correction (2026-08):** agent was told "run the safe delete" (a SAFE list it had
  proposed) and hard-deleted npm/pnpm/bun caches with `rm -rf`. User pushed back hard:
  *"why didnt you move them to trash first"*. Two durable takeaways:
  (1) An approved "safe delete" authorizes ONLY the specific SAFE list proposed — never a
  blanket `rm -rf`. Keep Docker VM, `~/.hermes`, `~/Documents`, active venv, Android SDK,
  lmstudio, and pre-existing cloud resources untouched unless separately approved.
  (2) Even cache deletion = move to trash, not hard rm. Verify with `df -h /home/deeone`
  before/after. See `references/safe-delete-pattern.md` for the full execution recipe.

### Consult-before-destructive (standing user rule)
For ANY deletion, process kill, service stop, package removal, or `rm -rf`, this user requires a
**clarify-first** consult with beneficial suggestions + tradeoffs — never unilateral. Even an
approved "run the safe delete" only authorizes the specific SAFE list proposed, not a blanket
`rm -rf`. KEEP Docker VM, `~/.hermes`, `~/Documents`, active venv, Android SDK, lmstudio, and
pre-existing cloud resources untouched unless separately approved.

## Troubleshooting

### If Cleanup Doesn't Free Expected Space
1. Check for hidden large files: `sudo du -sh /* | sort -hr | head -10`
2. Look for deleted files still held by processes: `lsof | grep deleted`
3. Check filesystem reserved blocks (typically 5% on ext4): `sudo tune2fs -l /dev/sdXn | grep "Reserved block count"`
4. Consider filesystem fragmentation (less common on modern Linux filesystems)

### If System Still Feels Slow After Cleanup
1. Check for memory leaks: `top` or `htop` sorted by memory
2. Look for high CPU usage processes: `top` or `htop` sorted by CPU
3. Check disk I/O: `iotop` or `dstat -d`
4. Consider rebooting to clear stale state (particularly effective on Linux)

---
*This skill captures procedures for safe system maintenance and cleanup. Always verify you have backups of important data before performing cleanup operations.*

## Session References
- `references/disk-analysis-2026-07.md` — measured findings from this system (actual `du` output, not estimated)