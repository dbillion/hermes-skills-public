---
name: gcp-cloud-run-deploy
description: Deploy to Cloud Run cost-safe; avoid build failures.
---

# GCP Cloud Run Deploy (Go / containers)

## When this applies
Deploying a service or container to Google Cloud Run via `gcloud run deploy --source=.` or
`gcloud builds submit`, then tearing it down. Covers gotchas causing silent build failures
and lingering billable resources — learned deploying a Go service for this user.

## Prerequisites
- `gcloud` authenticated; default project set (`gcloud config get-value project`).
- Cloud Run, Cloud Build, Artifact Registry APIs enabled (verify: `gcloud services list --enabled`).
- Dockerfile in the deployed directory.

## Deploy pattern (cost-safe)
```
SVC=my-svc; REGION=us-central1; PROJ=$(gcloud config get-value project)
gcloud run deploy $SVC --source=. --region=$REGION --project=$PROJ \
  --allow-unauthenticated --port=8080 --timeout=400
URL=$(gcloud run services describe $SVC --region=$REGION --project=$PROJ --format='value(status.url)')
curl -s --max-time 20 "$URL/" ; curl -s --max-time 20 -w "healthz %{http_code}\n" "$URL/healthz"
# TEARDOWN (always)
gcloud run services delete $SVC --region=$REGION --project=$PROJ --quiet
gcloud artifacts repositories delete cloud-run-source-deploy --location=$REGION --project=$PROJ --quiet
```

## Gotchas
- **Base image tags:** `golang:1.26-alpine` does NOT exist on Docker Hub (latest is `1.27rc2`).
  Use a real stable tag like `golang:1.23-alpine` even if local Go is newer — the container
  build pulls its own toolchain. A non-existent tag fails with cryptic
  "Building Container... failed" and no inline error.
- **Build context must contain `go.mod`:** `gcloud run deploy --source=.` runs `COPY go.mod ./`
  in the Dockerfile. If `go.mod` is in a parent dir, build fails:
  `COPY failed: file not found in build context or excluded by .dockerignore`.
  Put a minimal `go.mod` (`module x\n\ngo 1.23`) in the deployed folder.
- **`--source=.` auto-creates an Artifact Registry repo** `cloud-run-source-deploy` in the
  region. On failure OR success, **delete it after** or it lingers as a billable resource.
- **Verify before teardown races:** capture URL, curl, THEN delete. A 404 on `/healthz` during
  verify is often a teardown-timing artifact, not a code bug — confirm locally first.
- **Cost discipline:** this user requires every cloud resource closed after use. Confirm with
  `gcloud run services list` + `gcloud artifacts repositories list` = empty for the project.

## Multi-stage Dockerfile (known-good)
```
# syntax=docker/dockerfile:1
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod ./
RUN go mod tidy || true
COPY . .
RUN CGO_ENABLED=0 go build -o /app main.go
FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /
COPY --from=build /app /app
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/app"]
```

## Diagnostic
- Build failed with no error? `gcloud builds list --project=$PROJ --filter=status=FAILURE` then
  `gcloud builds log <id> --project=$PROJ` to see the Docker error (often missing go.mod or bad base tag).
- Stray repo left behind? `gcloud artifacts repositories delete cloud-run-source-deploy --location=$REGION`.
