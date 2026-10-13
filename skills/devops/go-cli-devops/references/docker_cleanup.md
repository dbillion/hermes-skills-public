# Docker / Podman cleanup — durable technique

From a real session: user had a "156GB Docker" and asked to remove images unused >3 months.

## Key facts
- "Docker uses 156GB" is usually the VM's **provisioned** disk size. `docker system df` shows
  ACTUAL used (often ~94GB). Trust `docker system df`, not a bloat report.
- The 3-month rule barely dents storage: the largest images are usually RECENT (e.g. a 24.6GB
  security tool built 5 weeks ago). Deleting only >3-month-old images frees little; the real
  reclaimable space is build cache + genuinely-abandoned project volumes.

## Fast, safe image deletion (avoid per-image inspect — it's SLOW on 50+ images)
```
KEEP="supoclip|kindest/node|greenbone|postgres:|prom/prometheus|grafana|otel|docker/desktop-"
docker images --format '{{.Repository}}:{{.Tag}}' | grep -vE "^($KEEP)" > /tmp/del.txt
while read img; do docker rmi "$img" || docker rmi -f "$img"; done < /tmp/del.txt
```
Do NOT loop `docker inspect` per image — it round-trips the daemon and timed out at 90s.

## Build cache
`docker builder prune -af` → reclaims all build cache (often ~21GB). Safe (regenerates on build).

## Volumes
`docker volume ls` + inspect size; volumes belong to projects. Deleting a project's volume loses
its data. Only remove volumes for ABANDONED projects after confirming with the user. Keep
`docker/desktop-*` volumes (Docker Desktop internals).

## Daemon needs root but sudo not passwordless?
Use **podman** (rootless, drop-in): `podman run`, `podman logs`, `podman cp`.
Gotcha: nginx:alpine images symlink `/var/log/nginx/access.log -> /dev/stdout`, so capture the
access log via `podman logs <c>` — `podman cp` of the log file fails (special file).

## Permission note
Image/volume deletion is destructive/shared-state. Present a delete-list first; get batch approval
before `docker rmi`/`prune` on a user's machine.
