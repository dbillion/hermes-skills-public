# Importing Gemini CLI Extensions as Hermes Skills

Gemini CLI extensions live in `~/.gemini/extensions/` and can provide powerful MCP servers or agent behaviors. When the user says "check skills I imported from Gemini" or "did you not import everything Gemini had", they mean these extensions.

## Location
```
~/.gemini/extensions/
├── gcloud-mcp/         ← MCP server (gcloud CLI wrapper)
├── cloud-run/          ← MCP server (Cloud Run management)
├── gke-mcp/            ← MCP server (GKE management)
├── firebase/           ← Agent workflows
├── firestore-native/   ← Agent workflows
├── stitch/             ← Design agent
├── google-genmedia/    ← Media generation
└── ...
```

## Extension Structure

Each extension has:
- `gemini-extension.json` — metadata + MCP server config
- `GEMINI.md` — context/instructions injected into the agent
- `skills/` — sub-skills directory (if any)
- Binary or `package.json` (for npx-based extensions)

## How to Convert to Hermes Skill

### npx-based extensions (e.g., gcloud-mcp, cloud-run)

Read the `gemini-extension.json`:
```json
{
  "name": "gcloud-mcp",
  "mcpServers": {
    "gcloud": {
      "command": "npx",
      "args": ["-y", "@google-cloud/gcloud-mcp"]
    }
  }
}
 skill with MCP servers block:
```
skill_manage(action='create', name='gcloud-mcp',
  mcp_servers={'gcloud': {'command': 'npx', 'args': ['-y', '@google-cloud/gcloud-mcp']}},
  content=<GEMINI.md content>)
```

### Binary-based extensions (e.g., gke-mcp)

The binary must be available in PATH. Reference it in mcp_servers block:
```json
{
  "mcpServers": {
    "gke": {
      "command": "${extensionPath}${/}gke-mcp"
    }
  }
}
```

For Hermes, download the binary and use the full path in `mcp_servers`.

### Discovering All Gemini Extensions

To list all installed extensions:
```bash
ls ~/.gemini/extensions/
```

To read an extension's MCP config:
```bash
cat ~/.gemini/extensions/gcloud-mcp/gemini-extension.json
```

## Common Gemini Extensions for Development

| Extension | Type | Description |
|-----------|------|-------------|
| `gcloud-mcp` | MCP | Full gcloud CLI access (Compute, GKE, Run, SQL, DNS, IAM) |
| `cloud-run` | MCP | Cloud Run service management |
| `gke-mcp` | MCP (binary) | GKE cluster management |
| `gke` | Skill pack | GKE skills (separate from gke-mcp MCP) |
| `vertex` | MCP | Vertex AI model management |
| `firebase` | Agent | Firebase CLI workflows |
| `firestore-native` | Agent | Firestore operations |
| `stitch` | Agent | Design generation |
| `google-genmedia` | Agent | Image/video/audio generation |
| `conductor` | Agent | Project tracking |
| `maestro` | Agent | Multi-agent orchestration |
| `skill-porter` | Tool | Skill conversion utility |
| `skillz` | Tool | Skill installation/management |
| `superpowers` | Agent | Agent behavior patterns |

## Pitfall: Not Checking Extensions

When the user says "did you import everything Gemini had" or "check that directory for skills", look in `~/.gemini/extensions/` first. Many capabilities (GCP, Firebase, design, media) are hidden there and NOT in the Hermes skill library by default.
