---
name: cloud-run-mcp
description: "Cloud Run MCP server — deploy and manage Cloud Run services and jobs via structured MCP tools."
version: 1.0.0
author: Google Cloud
license: Apache-2.0
platforms: [linux, macos]
mcp_servers:
  cloud-run:
    command: npx
    args: ["-y", "@google-cloud/cloud-run-mcp"]
---

# Cloud Run MCP

Dedicated MCP server for Google Cloud Run. Provides structured tools for deploying, managing, and troubleshooting Cloud Run services and jobs. **Prefer this over the generic gcloud-mcp** for Cloud Run operations — it returns better-structured data.

## Prerequisites

- gcloud CLI installed and authenticated
- Node.js 18+
- Project and region configured

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CLOUD_PROJECT` | Project ID |
| `GOOGLE_CLOUD_REGION` | Region (e.g., `us-central1`, `us-east1`) |

## What It Provides

- Deploy services from source or container images
- Manage service configurations (scaling, concurrency, memory, CPU)
- List and describe services and revisions
- Manage jobs and executions
- View logs and metrics
- Set IAM policies on services

## Usage

The MCP server starts automatically when Cloud Run tools are invoked. Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_REGION` for your target deployment.

## Guiding Principle

Per the gcloud-mcp skill: **prefer this specialized server** over raw `gcloud run deploy` via the generic gcloud MCP. This gives typed inputs/outputs and better error handling.
