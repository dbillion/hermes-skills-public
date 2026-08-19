---
name: devops-golang-track
description: Track A — roadmap.sh DevOps projects rebuilt in Go on GCP.
---

# DevOps in Go on GCP — Track A

The user is reimplementing the **official roadmap.sh DevOps Projects (26 total: 11 Beginner / 11 Intermediate / 4 Advanced)** in **Go**, targeting **Google Cloud**. Every cloud resource is created AND torn down after use (cost-safe mandate). Canonical requirements: repo `journal/00-ROADMAP-PROJECTS.md`.

## Durable user preferences (HARD rules for this program)

1. **Name binaries after the problem, not roadmap codes.** A CLI must be called what it solves
   (e.g. `sysstats`, `logarc`, `nginxlog`, `pagedeploy`), NEVER `b1`/`b2`. Roadmap code (B1..A4) is only
   an internal key for folder/journal traceability. User explicitly rejected `b1`-style names.
2. **Each project = its own git repo**, named after the problem: `devops-<problemname>`
   (e.g. `devops-pagedeploy`). Commit code + journal, then `git push` (gh authed as `dbillion`).
3. **Permission pre-clearance envelope.** Before a long autonomous run (e.g. "do all 26"), enumerate
   EVERY permission-gated action and get batch approval FIRST, so the agent doesn't stall mid-run.
   Permission-gated classes:
   - GitHub repo create + push (ALL projects).
   - GCP create (Cloud Run, Artifact Registry, GCE e2-micro via Terraform, VPC, Cloud SQL snapshots,
     GKE for A3, Cloud Monitoring/Prometheus, Cloud Storage, Service Directory) — create touches the acct.
   - Terraform apply + destroy per project.
   - Projects needing extra user input: B7 (real domain), I11 (VPN endpoint/IP), A4 (domain/scheme).
     For those, get the input or do local-only.
   Present as a grouped list; ask for a single batch yes / yes-with-exceptions.
4. **Every build is tested + verified.** `go test ./...` must pass; capture build errors/logs; fix until
   green; journal each project (goal, impl, cloud resources, teardown verification, gains).
5. **Cost-safe teardown is non-negotiable.** Pair every `gcloud`/`terraform` create with delete/destroy;
   verify `gcloud ... list` = empty. Target cost = $0.

## Tooling conventions

- **Go CLI library = cobra** (`github.com/spf13/cobra`). The user once said "clapper" — **`clapper` does
  NOT exist** (404). Use cobra (or urfave/cli). Don't go looking for clapper.
- Module per project: `module devops-go/<id>`, `go 1.23`. `go install .` → `~/go/bin`. Ensure
  `export PATH="$HOME/go/bin:$PATH"` is in `~/.zshrc` (it was missing; add it).
- **gcloud PATH fix (critical):** gcloud is at `/home/deeone/google-cloud-sdk/bin/gcloud` and is NOT on
  PATH inside shells spawned by Go's `os/exec`/non-login shells. Shell-out helpers must export the SDK bin.
  See `references/gcloud-path-and-deploy.md`.
- **Docker:** daemon needs root and refuses non-root start on this box. Use **podman** (v6, rootless) as
  the Docker-compatible engine. Podman quirk: `nginxinc/nginx-unprivileged:alpine` listens on 8080 and
  symlinks `/var/log/nginx/access.log -> /dev/stdout` → capture via `podman logs`, not `podman cp`.

## Per-project execution loop
1. `main.go` (cobra) + `go.mod` + sample + `main_test.go`.
2. `go get cobra`; `go test ./...`; `go build -o ~/go/bin/<name> .`; verify `--help` + real run.
3. If cloud-mapped: deploy via gcloud/terraform, VERIFY live, TEAR DOWN, confirm $0.
4. Write `journal/PXX-<name>.md`.
5. `gh repo create devops-<name> --private`; `git init` in project dir; commit; `git push -u origin main`.
6. Update `journal/00-PLAN.md` status. Next.

## Reference files
- `references/gcloud-path-and-deploy.md` — the `sh()` PATH-export helper + a B4-style GCS
  create/configure/upload/teardown command sequence, reproducible with modifications.
