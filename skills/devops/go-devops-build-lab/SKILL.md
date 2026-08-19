---
name: go-devops-build-lab
description: "Go DevOps on GCP with cobra, goreleaser, safe teardown."
---

# Go DevOps Build Lab

Rebuild DevOps curriculum projects (e.g. roadmap.sh 26-project list) in **Go** on **Google Cloud**, journaling each. Cost-safe: every cloud resource is created AND torn down.

## Project structure (per project)
```
devops-go/
  journal/00-PLAN.md            # backlog mapping each official project -> Go/GCP build
  journal/00-ROADMAP-PROJECTS.md  # official requirements (extracted from roadmap.sh)
  journal/B1-<slug>.md         # per-project journal (goal, impl, teardown, gains)
  projects/B1-<slug>/
    requirements.md            # official spec verbatim (for git commit traceability)
    main.go  go.mod
```
git commit per project; `requirements.md` documents the spec before code.

## CLI construction (cobra, not clapper)
- **There is NO `github.com/leaanthony/clapper`** — it 404s. Use **cobra** (`github.com/spf13/cobra`, ~44k★) or **urfave/cli**. User may say "clapper" meaning a CLI lib; correct them to cobra.
- Flags pattern: `-s/--stat all|load|mem|disk|uptime`, `-f/--format text|json`, `-w/--watch N`.
- Install: `go install .` -> binary in `$HOME/go/bin` (on PATH). Build: `go build -o b1 .`

## Make CLIs run on ANY PC (cross-platform)
1. **OS-aware collectors**: wrap `/proc` reads in `if runtime.GOOS == "linux" {…} else { return "n/a on "+runtime.GOOS }`. `df -h` exists on linux/darwin but NOT windows — guard windows with a message. Without this, cross-platform `go test` fails at runtime on mac/windows.
2. **Cross-compile** (pure Go, no cgo): `GOOS=windows GOARCH=amd64 go build -o dist/b1.exe .` etc. for darwin/linux × amd64/arm64.
3. **goreleaser** (`.goreleaser.yaml`, version: 2) builds all targets, runs `go test ./...` first, checksum, drafts GitHub Release. Install via `go install github.com/goreleaser/goreleaser@latest`.
4. **GH Actions**: `test.yml` matrix (ubuntu/macos/windows × amd64/arm64) runs `go test ./...` on every PR; `release.yml` on `v*` tag runs `goreleaser release --clean` (needs `GITHUB_TOKEN`).
   - Copy-paste scaffolding: `templates/goreleaser-and-actions.yaml` (all three files in one).

## GCP deploy (cost-safe) — Cloud Run
- Build container remotely: `gcloud run deploy svc --source=. --allow-unauthenticated --port=8080`. No local Docker needed (Cloud Build builds it).
- **Dockerfile gotchas**: `golang:1.26-alpine` does NOT exist on Docker Hub (latest is 1.27rc2). Use `golang:1.23-alpine`. The build context MUST contain `go.mod` or `COPY go.mod` fails ("file not found in build context").
- **Teardown is mandatory**: after verify, run `gcloud run services delete svc --quiet` AND `gcloud artifacts repositories delete cloud-run-source-deploy --location=… --quiet` (Cloud Run auto-creates an Artifact Registry repo on first deploy — delete it or it lingers/bills).
- Confirm zero leftovers: `gcloud run services list` + `gcloud artifacts repositories list` show nothing of yours.

## qmd BM25 (search the journal)
- `qmd search "term"` is pure lexical BM25 — **needs NO model**. For BM25, the "smallest model" = none. Embedding/rerank models (embeddinggemma-300M, Qwen3-Reranker-0.6B) are only for `qmd query`/vector, and are CPU-slow on this box. Index via `qmd update`.

## Mermaid diagrams
- Render via `mmdc` (mermaid CLI). Needs chromium: set `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium` (or puppeteer config `executablePath`), else it fails looking for its own Chrome. `mmdc -i x.mmd -o x.png -b transparent`.

## chrome-devtools MCP
- `chrome-devtools-mcp@latest` is reachable via `mcp-cli` (tools: navigate_page, click, evaluate_script, upload_file, list_network_requests). BUT it **spawns its own headless Chrome** each call (npx noise breaks JSON parsing) rather than attaching to a running instance. For reliable scraping use the built-in `browser_*` tools. The Hermes Chrome Connector extension can bind it to a real Chrome.
