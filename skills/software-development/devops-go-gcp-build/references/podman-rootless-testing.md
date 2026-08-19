# Testing against a real container image without root (podman rootless)

On this user's machine the **Docker daemon refuses to start (`dockerd needs root privileges`)**
and sudo is barred. Use **podman** (v6.x, installed, runs rootless) as the Docker-compatible
engine. This is the reliable way to "launch an alpine/nginx image and test" here.

## Recipe: run nginx:alpine and capture its access log
```bash
# unprivileged nginx image listens on 8080 INSIDE the container (not 80)
podman run -d --name nginx-test -p 8080:8080 docker.io/nginxinc/nginx-unprivileged:alpine

# wait ~4s for readiness, then generate real traffic (sequential, with delays — rapid curls race and return 000)
for p in / /index.html /missing /favicon.ico; do
  curl -s -o /dev/null --max-time 5 http://localhost:8080$p
  sleep 1
done

# access.log is a SYMLINK to /dev/stdout in this image, so `podman cp` FAILS ("file not found").
# Capture it from `podman logs` instead:
podman logs nginx-test 2>&1 | grep -E '"[A-Z]+ ' > /tmp/real_access.log

# run the analyser on the REAL log
b3 --source /tmp/real_access.log --top 5

# cleanup (cost-safe: no lingering resources)
podman rm -f nginx-test
```

## Gotchas
- `--unprivileged` image -> internal port **8080**, not 80. Map `-p 8080:8080`.
- `podman cp container:/var/log/nginx/access.log .` errors because the file is a symlink to
  `/dev/stdout`. Use `podman logs` + grep for the combined-format lines.
- Mixed `000` responses mean nginx wasn't ready yet or curls fired too fast — add `sleep` between hits.
- `docker` client exists but daemon is down; don't waste time on `dockerd` (needs root). Go straight to `podman`.
