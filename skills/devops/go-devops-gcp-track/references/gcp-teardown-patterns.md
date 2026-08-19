# GCP Teardown Patterns & Gotchas (from the 26-project Go/GCP track)

Condensed, session-proven. Each was hit and fixed during the B1–B9 builds.

## 1. gcloud not on PATH inside spawned shell
Symptom: `gcloud: command not found` when running via `exec.Command("/bin/sh", "-c", c)`.
Cause: Go-spawned shells don't inherit the login PATH where the SDK lives at
`/home/deeone/google-cloud-sdk/bin`.
Fix: every cloud command runs through `sh()` which prepends the SDK to PATH.
Never call bare `gcloud` from a spawned shell.

## 2. GCE e2-micro capacity exhaustion (free tier)
Symptom: terraform apply fails with
`The zone '.../zones/us-central1-a' does not have enough resources available...`
This is a GCP-side capacity shortage, NOT a code bug. It recurred in us-central1-a
AND us-central1-c during one session.
Working zones observed: `us-east1-b` (e2-micro available).
Mitigation: default Terraform zone to `us-east1-b`; if it fails, try
`us-west1-b` / `europe-west1-b`. Always run `terraform destroy` after a failed
apply so no partial resources linger.

## 3. Terraform must run in the generated dir
Symptom: `terraform apply` → "No configuration files".
Cause: my `deploy()` ran `terraform apply` from the project CWD, but `main.tf` was
written to `--out`. Fix: prefix every terraform cmd with `cd <outDir> &&`.

## 4. Terraform -var undeclared
Symptom: `apply` → "Value for undeclared variable: project".
Cause: passed `-var project=X` but the template hardcoded `project = "%s"` in the
provider (no `variable "project" {}` block). Fix: declare
`variable "project" { type = string }` in the template, OR drop the `-var` flag.

## 5. HCL string split by pubkey newline
Symptom: `Invalid multi-line string` / `Unterminated template string` in generated
`main.tf` at the `ssh-keys` line.
Cause: `ssh.MarshalAuthorizedKey` returns a trailing `\n`; interpolating it into
`"deeone:%s"` split the quoted string. Fix: `strings.TrimSpace(pub)` before the
`fmt.Sprintf`.

## 6. Cloud DNS: zone won't delete with custom records
Symptom: `gcloud dns managed-zones delete` → HTTP 400 "cannot be deleted because it
contains one or more 'resource records'".
Fix: delete the custom record-set BEFORE the zone:
`gcloud dns record-sets delete www.<domain> --zone=<z> --type=A --quiet`, then delete zone.

## 7. Firewall 409 "already exists" (orphan collision)
Symptom: repeated `apply` runs hit `Error 409: .../firewalls/<name> already exists`.
Cause: an earlier aborted run left the firewall; my code reused the same name.
Fix: make the firewall name unique per run (e.g. `nameFlag + "-fw-" + timestamp`)
so it never collides with an orphan. Also run `terraform destroy` (or
`gcloud compute firewalls delete <name> --quiet`) to clear orphans between attempts.

## 8. SSH verify "Connection refused" on port 22
Symptom: `gcloud compute ssh` fails immediately after instance creation:
`ssh: connect to host <ip> port 22: Connection refused`.
Cause: the VM booted but sshd inside wasn't ready (1–2s lag). Fix: `sleep 15`
before the ssh-verify step. The firewall allowed 22; sshd was just slow to start.

## 9. Cloud Monitoring: `gcloud beta monitoring` subcommands missing
Symptom: `gcloud beta monitoring descriptors|time-series ...` → "Invalid choice"
(no such subcommands in SDK 573).
Fix: do NOT use gcloud for Monitoring. Use the REST API via curl + token:
```
TOK=$(gcloud auth print-access-token)
curl -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  -d '{"name":"projects/PROJ/metricDescriptors/NAME","type":"NAME","metricKind":"GAUGE","valueType":"DOUBLE"}' \
  https://monitoring.googleapis.com/v3/projects/PROJ/metricDescriptors
curl -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  -d '{"timeSeries":[{"metric":{"type":"NAME"},"points":[{"interval":{"endTime":"ISO8601"},"value":{"doubleValue":1.0}}]}]}' \
  https://monitoring.googleapis.com/v3/projects/PROJ/timeSeries
curl -X DELETE -H "Authorization: Bearer $TOK" \
  https://monitoring.googleapis.com/v3/projects/PROJ/metricDescriptors/NAME
```
Verify delete with a GET that should return HTTP 404.

## 10. Always-destroy-on-error
Pattern: wrap deploy steps so `terraform destroy` (or resource delete) ALWAYS runs,
even if apply/ssh failed. Store first error, run teardown, then return the error.
This guarantees no orphaned billable resources when a step mid-pipeline fails.

## Orphan verification (run after every teardown)
- Compute: `gcloud compute instances list --project=<P>` → expect no <name>
- Firewall: `gcloud compute firewalls list --project=<P>` → expect no <name>
- DNS: `gcloud dns managed-zones list --project=<P>` → expect no <name>
- GCS: `gcloud storage ls gs://<bucket>` → expect 404
- Monitoring: GET descriptor → expect 404
