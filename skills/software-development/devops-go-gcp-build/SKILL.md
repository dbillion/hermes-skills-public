---
name: devops-go-gcp-build
description: Build DevOps projects in Go on GCP, cost-safe, journaled.
---

# DevOps Projects in Go on GCP (Build Track)

User builds the **26 official roadmap.sh DevOps projects** (Beginner/Intermediate/Advanced) in Go, targeting **Google Cloud** as primary cloud, journaling each, and tearing down every cloud resource after use (cost-safe). This skill encodes the working pattern established in the first sessions so future runs start correct.

## Hard rules (from user corrections)
- **Trash-first is the REQUIRED default, not optional.** Move files to `~/.local/share/Trash/files/` before any `rm`. A prior session hard-deleted npm/pnpm/bun caches with `rm -rf` (a bloat report listed them as safe) and the user CORRECTED it sharply: "why are you trying to delete bun, npm and pnpm? isnt that very bad... why didnt you move them to trash first." Lesson: caches are still user data — even when a report says "safe to clean", MOVE TO TRASH, never `rm -rf`, unless the user gives explicit per-item approval to hard-delete. Keep this as a standing preference in memory too.
- **Consult before destructive/shared-state actions**: kill procs, stop services, remove pkgs, `rm -rf`, cloud resource create/delete, git push. Use `clarify`.
- **Cost-safe cloud**: every `gcloud`/`terraform` resource is paired with delete/destroy. Verify with `gcloud run services list` + `gcloud artifacts repositories list` = empty.
- **Study-first**: do NOT execute cloud CLIs unless the user says go. AWS CLI is currently unavailable — don't assume it.
- **No GPU**: Intel HD 620 iGPU, no CUDA. BM25/qmd search needs NO model — `qmd search` is instant on CPU.

## Go CLI pattern (Beginner projects B1/B2 built this way)
- Library: **cobra** (`github.com/spf13/cobra`). User believed **`clapper`** exists — it does NOT (404). Use cobra (or urfave/cli).
- Each project = `projects/<code>-<slug>/` with `main.go`, `go.mod` (`module devops-go/<x>`, `go 1.23`), `requirements.md` (official spec), `main_test.go`.
- **OS-aware**: guard `/proc` + `df` reads with `if runtime.GOOS == "linux"`; return "n/a on <os>" elsewhere so cross-platform tests pass.
- Install: `go install .` → `~/go/bin`. Ensure `export PATH="$HOME/go/bin:$PATH"` in `~/.zshrc` (user's zsh; `.zshrc` only had `.cargo/bin` — false-matched "go/bin" substring).
- Flags: `--stat`, `--format text|json`, `--watch`, `--source/--dest/--gzip`.

## Cross-platform release (goreleaser + GH Actions)
- **goreleaser NOT needed locally** — CI action `goreleaser/goreleaser-action@v6` installs it in-pipeline. Don't `go install` it locally (user blocked that; CI handles it).
- Repo-root files:
  - `.goreleaser.yaml` (version: 2): `builds` for `linux/darwin/windows × amd64/arm64`, `CGO_ENABLED=0`, `archives` + `checksum` + `changelog`, `release.draft: true`.
  - `.github/workflows/test.yml`: matrix `os:[ubuntu,macos,windows-latest] × arch:[amd64,arm64]`, `go test ./...`.
  - `.github/workflows/release.yml`: on `tags: v*`, goreleaser `release --clean` with `GITHUB_TOKEN`.
- Activate: `git init` + remote + `git tag v0.1.0 && git push --tags` → CI tests all platforms, drafts release. (Push/release = shared-state; confirm with user first.)

## GCP deploy pattern (P01 template)
- `gcloud run deploy <svc> --source=. --region=us-central1 --allow-unauthenticated --port=8080` builds the container REMOTELY via Cloud Build (no local Docker needed).
- Dockerfile: multi-stage `golang:1.23-alpine` → `gcr.io/distroless/static-debian12:nonroot`, non-root, EXPOSE 8080. **`golang:1.26-alpine` does NOT exist** (latest 1.27rc2) — use 1.23.
- Build context MUST contain `go.mod` or COPY fails ("file not found in build context").
- After verify: `gcloud run services delete <svc> --quiet` AND `gcloud artifacts repositories delete cloud-run-source-deploy --location=us-central1 --quiet` (Cloud Run auto-creates this repo).
- Pre-existing `go-web-collab` (by dayozoe, not ours) — leave untouched unless user says.

## Journal structure (`/home/deeone/devops-go/`)
- `journal/00-PLAN.md` — maps all 26 roadmap projects → Go/GCP builds.
- `journal/00-ROADMAP-PROJECTS.md` — authoritative 26-project list (browser-extracted; JS page, no public API).
- `journal/PXX-<name>.md` — per-project build journal.
- `projects/<code>-<slug>/` — code + `requirements.md` + tests.

## Verification per project
- [ ] `go build` + `go test ./...` + `go vet` clean
- [ ] `go install .` → binary on PATH, `--help` shows flags
- [ ] (cloud) deployed, verified, FULLY torn down ($0)
- [ ] journal + requirements.md updated

## Gotchas
- `mcp-cli chrome-devtools` spawns own headless Chrome w/ npm stdout noise → flaky. Built-in `browser_*` more reliable for JS pages.
- **Containers without root**: Docker daemon needs root (barred); use **podman** (rootless). See `references/podman-rootless-testing.md` for the nginx:alpine access-log capture recipe.
- qmd BM25: `qmd update` builds index (no model); `qmd search` instant lexical.
- User prefers MCP by default when present (drive integrations via real MCP, not hand-rolled curl).
