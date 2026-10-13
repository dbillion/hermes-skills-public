---
name: gke-mcp
description: "GKE MCP server — manage Google Kubernetes Engine clusters, node pools, and workloads via structured MCP tools."
version: 0.12.0
author: Google Cloud
license: Apache-2.0
platforms: [linux, macos]
---

# GKE MCP

Dedicated MCP server for Google Kubernetes Engine. Provides structured tools for managing GKE clusters, node pools, and workloads. **Prefer this over the generic gcloud-mcp** for GKE operations.

## What It Provides

- Create, update, delete clusters
- Manage node pools (add, resize, update)
- List and describe clusters
- Get credentials for kubectl
- Monitor cluster status and node health
- Manage cluster add-ons and features

## Prerequisites

- gcloud CLI installed and authenticated
- `kubectl` installed (for cluster interaction after getting credentials)
- The `gke-mcp` binary must be available at the extension path

## Binary

The GKE MCP server uses a native binary (`gke-mcp`, ~29MB). On Gemini CLI it's bundled at the extension path. For Hermes, download from the Google Cloud MCP releases or build from source.

## Guiding Principle

Per the gcloud-mcp skill: **prefer this specialized server** over raw `gcloud container clusters` via the generic gcloud MCP.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Binary not found | Download gke-mcp binary and place in PATH or skill directory |
| `kubectl` not found | Install: `gcloud components install kubectl` or `brew install kubectl` |
| Can't reach cluster | Check `gcloud container clusters get-credentials CLUSTER_NAME` |
