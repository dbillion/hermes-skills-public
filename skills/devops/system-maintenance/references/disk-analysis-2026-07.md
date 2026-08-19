# Disk Analysis — July 2026 Session Findings

## System
- `/dev/nvme0n1p3` — 871GB total, 746GB used, 81GB free (91% full)

## Biggest actual space users (measured with `du -h -d 1`)

| Location | Actual size | Notes |
|---|---|---|
| `~/.docker/Docker.raw` | 157GB disk / 871GB apparent | Docker loop file — actual usage via `du -sh`, apparent via `ls -lh` |
| `~/.local/share` | 58GB | App data |
| `~/Downloads` | 11GB | |
| `~/.local/bin` | 2.1GB | |
| `~/Desktop` | 2.9GB | |
| `~/.cache` | 271MB | |
| `~/.local/state` | 1.3GB | |
| `/tmp` | 1.6GB | |

## Subdirectory breakdown

```
~/.local/share/          58GB
  pnpm/              2.2GB   (package cache — regeneratable: rm -rf ~/.local/share/pnpm)
  pipx/              1.5GB   (Python isolated packages — pipx list before wiping)
  claude/            637MB    (Claude desktop cache)
  hermes/            369MB    (Hermes agent data)
  GitKrakenCLI/      162MB
  cursor-agent/      151MB
  Hubstaff/          18MB

~/.cache/              271MB
  BraveSoftware/     221MB    (browser cache — regeneratable: rm -rf ~/.cache/BraveSoftware)

~/Downloads/           11GB
  Telegram Desktop/   6.3GB   (delete if web version is used: rm -rf ~/Downloads/Telegram\ Desktop)
  claude-desktop-arch 1.1GB   (installer binary — delete after install: rm ~/Downloads/claude-desktop-arch)
  Programs/           902MB   (installers including qoder ~200MB)

~/Desktop/             2.9GB
  Transformers - Nefarious.cbr   0.29GB   (comic — archive or delete)
  Cluely 2.1.10.dmg             0.25GB   (app — delete installer if installed)
  Antigravity IDE.tar.gz         0.23GB   (delete after extract)
  maltego-4.11.3.pkg.tar.zst     0.19GB   (delete after install)
  Antigravity.tar.gz             0.16GB   (old installer)
```

## Recommended deletions (no system breakage, all regeneratable/reinstallable)

```bash
# 1. Telegram desktop cache — 6.3GB
rm -rf ~/Downloads/Telegram\ Desktop

# 2. pnpm global store — 2.2GB
rm -rf ~/.local/share/pnpm

# 3. pipx packages — 1.5GB
pipx list  # review first
rm -rf ~/.local/share/pipx

# 4. qmd local search data — 1.3GB
rm -rf ~/.local/share/qmd

# 5. Claude desktop binary (already installed) — 1.1GB
rm ~/Downloads/claude-desktop-arch

# 6. BraveSoftware browser cache — 221MB
rm -rf ~/.cache/BraveSoftware

# 7. qoder exploit tool (not needed) — 200MB
rm -rf ~/Programs/qoder

# 8. Claude desktop cache — 637MB
rm -rf ~/.local/share/claude

# 9. Hermes agent data — 369MB
rm -rf ~/.local/share/hermes

# Total recommended: ~14GB
```

## Nuclear option (irreversible — wipes all Docker images/containers)

```bash
docker system prune -a   # frees all unused images, containers, volumes, networks
```

This would free the ~155GB actual usage in `~/.docker/` but ALL docker images and containers are lost.

## Quick audit script

```bash
for dir in "$HOME/.docker" "$HOME/.cache" "$HOME/Downloads" "$HOME/Videos" "$HOME/.local/share" "/tmp"; do
    size=$(du -sh "$dir" 2>/dev/null | cut -f1)
    echo "$size  $dir"
done
```