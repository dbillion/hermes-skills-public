---
name: go-cli-devops
description: Build roadmap.sh DevOps CLIs in Go with cobra.
---

# Go CLI for DevOps Projects

Pattern established while rebuilding roadmap.sh DevOps projects in Go on GCP.

## When to use
- Implementing any roadmap.sh DevOps project as a Go CLI (B1 stats, B2 log archive, B3 nginx log analyser, ...).
- Scaffolding a new Go command-line tool the user will `go install` and call from PATH.

## NAMING: functional, not internal codes (USER PREFERENCE — high value)
The user explicitly said: **"I dont like the tools name, it should be the project it is solving, not b1."**
- Bad binary names: `b1`, `b2`, `project03` (internal roadmap codes).
- Good: `sysstats` (server perf), `logarc` (log archive), `nginxlog` (nginx analyser),
  `dnssetup`, `bastion`, `dbbak`, `pagedeploy`, `svcdeploy`, `dockersvc`, `bluegreen`, `metricsrv`.
- Keep the roadmap code (B1..A4) ONLY as a folder key / journal filename for traceability — never as
  the user-facing binary or `cobra.Use`. Apply to every generated tool for this user.

## Canonical structure (per project)
```
projects/<id>-<name>/
  main.go          # cobra root cmd
  main_test.go     # table/unit tests
  go.mod           # module devops-go/<id>, go 1.23, cobra dep
  requirements.md  # official roadmap requirement (verbatim)
journal/<id>-<name>.md  # goal, impl, sample run, teardown, gains
```

## Pattern
1. **cobra** for flag parsing (`github.com/spf13/cobra`). Flags: `--stat/--source/--format/--watch` etc.
2. **OS-aware**: guard Linux-specific code (`/proc`, `df`) with `if runtime.GOOS != "linux" { return "n/a on "+runtime.GOOS }`. Use `filepath` for cross-platform paths. This lets the same binary run (degrading gracefully) on macOS/Windows — required so `goreleaser` cross-compile tests pass.
3. **Install / binary name (CRITICAL pitfall):** `go install .` names the binary after the **module
   directory**, NOT the `cobra.Command.Use` string. So `go install .` in `projects/B1-cli-...` produces
   `~/go/bin/B1-cli-...` — ignoring your `Use:"sysstats"`. **Fix:** install with an explicit output path:
   `go build -o $HOME/go/bin/<funcname> .` (e.g. `go build -o $HOME/go/bin/sysstats .`).
   NOTE: `go install -o` is INVALID — `go install` rejects `-o`; use `go build -o`.
   Ensure `~/.zshrc` has `export PATH="$HOME/go/bin:$PATH"` (a grep for "go/bin" can false-match
   ".cargo/bin", so verify with `which <name>` in a FRESH shell).
4. **Cross-platform release**: `.goreleaser.yaml` (builds windows/darwin/linux × amd64/arm64, runs `go test`, checksums, draft release) + `.github/workflows/test.yml` (matrix ubuntu/macos/windows × amd64/arm64 running `go test ./...`) + `.github/workflows/release.yml` (on `v*` tag → goreleaser). goreleaser need NOT be installed locally; the CI action fetches it.
5. **No cloud for local CLIs** — cost $0; note optional GCP extension (Cloud Run / GCS) in journal but defer.

## Pitfalls
- **Don't assume a library name exists.** User referenced `clapper` (Go CLI lib) — `github.com/leaanthony/clapper` returns 404 (does not exist); `github.com/leaanthony/cli` also 404s. Real Go CLI libs: **cobra** (`github.com/spf13/cobra`) and **urfave/cli**. Always `go get` or web-search to verify a package path before substituting your own guess.
- **go.mod must live in the project dir**, not a parent — a container build step `COPY go.mod ./` fails with "file not found" if go.mod is missing from the build context. `go mod init` lands in CWD; double-check.
- **Regex group indices** in log parsers: `FindStringSubmatch` returns [whole, g1, g2, ...]. Off-by-one (using m[5] when the group is m[4]) causes panics / silent mis-mapping. Write a unit test with a sample log line to catch this.
- **nginx combined log regex** groups: m[1]=ip, m[2]=time, m[3]=request, m[4]=status, m[5]=bytes. Request line (method/url) is m[3], NOT m[4].

## Autonomous multi-project runs: permission envelope (USER WORKFLOW PREF)
When the user says "run all of them till you finish," do NOT just start blasting. Produce a
**permission-required matrix** grouped by action type and get batch approval FIRST:
- GitHub: create N repos + push (remote/shared-state).
- Cloud: create+teardown per project (billable/shared — even with teardown, creation touches the account).
- Needs user INPUT: domain for DNS/VPN, external IPs (can't invent).
- Avoid sudo (design around it: high ports, Cloud Run). If a step needs root, STOP and ask.
Then run sequentially: build → `go test` → capture errors/logs → fix until green → deploy (if mapped)
→ verify → teardown → journal → create repo + push. Pause only on unexpected cost or a decision point.

## Support
- `templates/cobra_cli_main.go` — starter main.go with cobra + OS guards (functional Use name).
- `references/roadmap_projects.md` — the 26 official roadmap.sh DevOps projects (Beginner 11 / Intermediate 11 / Advanced 4) for requirements mapping.
- `references/docker_cleanup.md` — fast/safe Docker image+volume cleanup, build-cache prune, podman fallback.
