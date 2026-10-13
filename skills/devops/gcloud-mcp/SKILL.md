---
name: gcloud-mcp
description: "Google Cloud MCP server — manage GCP resources via gcloud CLI through MCP tools. Compute, GKE, Cloud Run, Cloud SQL, DNS, IAM, and more."
version: 0.5.3
author: Google Cloud
license: Apache-2.0
platforms: [linux, macos]
mcp_servers:
  gcloud:
    command: npx
    args: ["-y", "@google-cloud/gcloud-mcp"]
---

# gcloud MCP

Google Cloud MCP server wrapping `gcloud` CLI. Enables AI agents to create, manage, troubleshoot, and optimize Google Cloud resources through structured MCP tool calls instead of raw shell commands.

## What It Provides

The MCP server exposes gcloud operations as typed tools with structured input/output:
- **Compute Engine**: VM instances, disks, firewalls, images
- **Cloud SQL**: Instances, databases, users
- **GKE**: Clusters, node pools
- **Cloud Run**: Services, jobs
- **Cloud DNS**: Managed zones, record sets
- **IAM**: Service accounts, policies, keys
- **Deployment Manager**: Deployments
- **App Engine**: Applications, versions
- **Storage**: Buckets, objects
- **Artifact Registry**: Repositories, images
- **Secret Manager**: Secrets, versions

## Guiding Principles

1. **Prefer specific, native tools** — if a GKE-specific or Cloud Run-specific MCP server is available, prefer it over the generic gcloud tool for the same operation. Specialized servers return better-structured data.
2. **Never guess required parameters** — project ID, cluster name, region, zone must come from the user or be explicitly resolved. No assumptions.
3. **Use defaults from environment** — if `project_id` is not specified, use the gcloud default (`gcloud config get-value project`).
4. **Reference docs**: https://cloud.google.com/sdk/gcloud/reference or append `--help` to any command.

## Prerequisites

- **gcloud CLI installed and authenticated** (`gcloud auth login` done)
- **Node.js 18+** (for npx)
- **Project selected** (`gcloud config set project PROJECT_ID` or pass per-command)

## Usage

The MCP server is started automatically by Hermes when tools from this skill are invoked. No manual setup needed.

### Common Operations

```bash
# Verify gcloud auth (run directly, not via MCP)
gcloud auth list
gcloud config get-value project

# List compute instances (via MCP tool)
# Tool: gcloud_compute_instances_list

# Create a Cloud Run service (via MCP tool)
# Tool: gcloud_run_deploy

# Get GKE cluster info (via MCP tool)
# Tool: gcloud_container_clusters_describe
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CLOUD_PROJECT` | Default project ID |
| `GOOGLE_CLOUD_REGION` | Default region |
| `CLOUDSDK_CORE_PROJECT` | gcloud SDK project override |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `npx` fails or hangs | Clear npx cache: `npx clear-npx-cache`, retry |
| `gcloud: command not found` | Install gcloud CLI: https://cloud.google.com/sdk/docs/install |
| `No project set` | Run `gcloud config set project PROJECT_ID` |
| `Insufficient permission` | Run `gcloud auth login` or check IAM roles |
| MCP server won't start | Check Node.js version: `node --version` (need 18+) |
