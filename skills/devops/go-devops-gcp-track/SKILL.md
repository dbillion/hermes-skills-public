---
name: go-devops-gcp-track
description: Rebuild DevOps projects as Go CLIs on GCP with teardown.
---

# Go DevOps → GCP Track

Class of work: rebuild a backlog of DevOps learning projects (e.g. the 26 official
roadmap.sh DevOps projects) as real Go CLI tools, each deployed to GCP, verified,
torn down (cost $0), journaled, and pushed to its own git repo.

## HARD RULES (from user corrections — do not violate)

1. **FINISH THE WHOLE BACKLOG.** "Stopped at 4 is not a pass mark." Once the
   permission envelope is approved, run B1 → A4 (or however projects are numbered)
   WITHOUT pausing for re-approval. Only stop when genuinely blocked (real GCP error
   needing retry, or a step requiring a user-supplied domain/endpoint). Do not ask
   "should I keep going?" mid-run.

2. **NAME BY FUNCTION, NOT ROADMAP CODE.** Binary, repo, and every GCP resource get
   the *problem-solved* name, never the roadmap id. Existing examples: `sysstats`,
   `logarc`, `nginxlog`, `pagedeploy`, `sshsetup`, `staticsite`, `dnssetup`,
   `monwatch`, `svcunit`. Codes like `b1`, `p2`, `i3` are forbidden as tool/repo
   names. User verbatim: "I dont like the tools name, it should be the project it is
   solving, not b1".

3. **gcloud REQUIRES EXPLICIT NAMES.** It does not auto-name. Reuse the functional
   name everywhere: binary `svcunit`, Cloud Run service `svcunit`, GCS bucket
   `devops-svcunit-<ts>`, GCE instance `svcunit-vm`. One name, no decisions for user.

4. **COST-SAFE: CREATE + TEARDOWN IN THE SAME RUN.** Every GCP resource must be
   deleted before the command exits. Verify it's gone (404 / empty instance list /
   empty bucket list). No orphaned VMs, firewalls, buckets, DNS zones, or metric
   descriptors. If `terraform apply` fails, still run `terraform destroy` (see
   references/gcp-teardown-patterns.md).

5. **ONE REPO PER PROJECT.** `gh repo create devops-<function> --private`, commit,
   push. Repo name uses the functional name from rule 2.

## PER-PROJECT PROCESS

1. Scaffold `projects/<id>-<slug>/main.go` — cobra root, functional command name.
2. `go.mod`: `module devops-go/<id>`, `require github.com/spf13/cobra`.
3. Build + `go test ./...` LOCALLY first. Fix until green (vet clean).
4. Cloud step (if project maps to GCP): shell out to `gcloud` via the `sh()` helper
   (see templates/cobra-gcp-cli.go). Deploy → verify live → **tear down** → verify gone.
5. `go build -o $HOME/go/bin/<function> .` (install on PATH).
6. Journal under `journal/<id>-<slug>.md` (mermaid diagram optional).
7. `gh repo create devops-<function> --private` + commit + push.

## THE sh() HELPER (mandatory)

Spawned `/bin/sh -c` does NOT inherit the login PATH, so `gcloud` is "command not
found". Every cloud command must run through a helper that exports the SDK:

```go
func sh(c string) (string, error) {
    cmd := exec.Command("/bin/sh", "-c",
        "export PATH=$PATH:/home/deeone/google-cloud-sdk/bin && "+c)
    b, err := cmd.CombinedOutput()
    return string(b), err
}
```

## WHEN TO SHELL OUT VS USE Go CLIENT LIBS

Prefer **shelling out to the `gcloud` CLI via `sh()`** over `cloud.google.com/go/*`
client libraries for control-plane ops (create/delete resources, push metrics).
Reasons: (a) no heavy module-cache network fetches that get blocked in this
environment, (b) one consistent pattern across all projects, (c) gcloud handles
auth/regions transparently. Use REST via `curl` + `gcloud auth print-access-token`
only when a `gcloud` subcommand is missing (e.g. Cloud Monitoring — see references).

## Pitfalls / references

All GCP-specific gotchas (capacity zones, DNS delete-order, sshd readiness wait,
Monitoring REST workaround, terraform CWD, variable declaration) are in
`references/gcp-teardown-patterns.md`. Copy the skeleton from
`templates/cobra-gcp-cli.go`. A reusable orphan-check probe is in
`scripts/check-orphans.sh`.
