# gcloud PATH fix + GCS static-site deploy/teardown

## The bug
`gcloud storage ...` fails with `gcloud: command not found` when called from a Go program via
`exec.Command("/bin/sh","-c", cmd)` (or any non-login shell). The gcloud CLI lives at
`/home/deeone/google-cloud-sdk/bin/gcloud` and is only on PATH in the interactive login shell
(via the SDK's own rc file), NOT inherited by spawned `/bin/sh`.

## The fix (reusable helper)
Always prefix the command with a PATH export:

```go
func sh(c string) (string, error) {
    cmd := exec.Command("/bin/sh", "-c",
        "export PATH=$PATH:/home/deeone/google-cloud-sdk/bin && "+c)
    b, err := cmd.CombinedOutput()
    return string(b), err
}
```

Use `sh()` for every gcloud/terraform shell-out. No need to hardcode the binary path in the command string.

## B4-style GCS static-site deploy then teardown (reproduce with modifications)
```go
proj := os.Getenv("GOOGLE_CLOUD_PROJECT"); if proj == "" { proj = "future-abode-338616" }
bucket := "devops-" + name + "-" + timestamp
mb   := fmt.Sprintf("gcloud storage buckets create gs://%s --project=%s --location=us-central1 --uniform-bucket-level-access", bucket, proj)
web  := fmt.Sprintf("gcloud storage buckets update gs://%s --web-error-page=index.html --web-main-page-suffix=index.html", bucket)
cp   := fmt.Sprintf("gcloud storage cp -r %s/* gs://%s", outDir, bucket)
rm   := fmt.Sprintf("gcloud storage rm -r gs://%s", bucket)
// run mb, web, cp in order; print live URL; then run rm unconditionally.
```
Verify teardown with: `/home/deeone/google-cloud-sdk/bin/gcloud storage ls gs://<bucket>` → expect 404.

## Notes
- `gcloud projects list` / `gcloud config get-value project` via the tool sometimes emits a stray
  `rtk:` alias error — use the full SDK path directly to avoid it.
- GCP project for this user: `future-abode-338616`. Creds at `GOOGLE_APPLICATION_CREDENTIALS`.
