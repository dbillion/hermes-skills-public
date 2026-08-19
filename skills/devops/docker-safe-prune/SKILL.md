---
name: docker-safe-prune
description: Reclaim Docker disk by keep-list image and cache prune.
---

# Docker Safe Prune

Class-level workflow for freeing Docker disk space on a dev machine without nuking wanted images or breaking the install.

## When to use
- "Docker is using 156GB", "free up docker", "remove images older than 3 months", "prune docker build cache".
- Any task where the user wants to reclaim container storage.

## Workflow (safe, reversible by re-pull)
1. **Measure first** (read-only):
   `docker system df` → images / containers / volumes / build cache breakdown.
   `docker system df -v` → per-image sizes + which images have containers.
2. **Identify the keep-set** with the user. Build a regex of repos to KEEP (e.g. `postgres:|kindest/node|greenbone|prom/prometheus|docker/desktop-`).
   - IMPORTANT: keep `docker/desktop-*` — deleting them can break Docker Desktop on restart.
   - Volumes: map them to projects with `docker volume ls` + inspect mountpoint before touching. Default = leave volumes alone unless explicitly told.
3. **Delete by repo:tag, NOT by per-image inspect loop.**
   - GOOD (fast even at 50+ images):
     `docker images --format '{{.Repository}}:{{.Tag}}' | grep -vE "^(KEEP_REGEX)" > /tmp/del.txt`
     then `while read img; do docker rmi "$img"; done < /tmp/del.txt`
   - BAD (causes 90s+ timeouts on large repos): looping `docker inspect` per image ID to test the keep-set. Avoid.
4. **Prune build cache** (often the biggest hidden win): `docker builder prune -af`.
5. **Verify**: re-run `docker system df`; confirm keep-set still present (`docker images | grep KEEP`).

## Pitfalls
- **Per-image `docker inspect` in a loop is slow** for 50+ images — the daemon round-trips make a 54-image loop exceed 90s timeouts. Use `docker images --format` + `grep -vE` instead.
- **Docker daemon may need root.** If `docker info` says not running and `dockerd` errors with "needs to be started with root privileges", you cannot start it without sudo (which is barred). Fallback: **podman** (usually preinstalled, runs rootless) accepts near-identical commands (`podman images`, `podman run`, `podman logs`). Note `podman cp` cannot copy a log symlinked to /dev/stdout — capture via `podman logs <c> | grep`.
- **nginx:alpine unprivileged image listens on 8080**, not 80 — map `-p 8080:8080`, not `-p 8080:80`.
- Deleting an image that a RUNNING container uses is blocked by Docker; stopped containers referencing it are fine to leave.
- **Bloat-report line items are often WRONG — verify before deleting.** A "system-bloat-report.md" claimed "JetBrains Backups 10G (~/.config/JetBrains/*-backup/)" and "JetBrains Old Versions 15G". Reality: the `*-backup` dir did NOT exist on disk, and the 15GB was actually 8.6GB of *live, current* Toolbox IDE installs (air/android-studio/intellij) — not stale versions. Deleting those would wipe working IDEs. Always `du -sh` / `find` to confirm a reported path exists and whether it's live data before acting. Treat bloat reports as hints, not facts.
- **Large `docker rmi` can exceed the 90s foreground tool timeout** (e.g. a 10.5GB image on Docker Desktop). Symptom: "timed out after 90s" but the image may or may not have been removed. Fix: run `docker rmi` in a **background terminal** (`terminal(background=true, notify_on_complete=true)`), then verify with a separate `docker images | grep`. Never assume a timeout = failure; re-check state.

## Keep vs delete decision
- "Not used in 3 months" by *creation date* ≠ *last used*. `docker images` shows CreatedAt; true last-use isn't tracked. Use creation date as proxy; exclude images with running containers (`docker ps --filter ancestor=...`).
- Big recent images (e.g. a 24GB redamon image, 5 weeks old) are NOT caught by a 3-month rule — confirm with user before removing recent-but-large images. The "156GB" Docker report is usually the VM's provisioned ceiling; actual used is often ~60-90GB.

## Support
- `scripts/prune_by_keeplist.sh` — parameterized keep-list pruner + cache prune (reusable, deterministic).
