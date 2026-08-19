---
name: gws-shared
description: Shared authentication and configuration for Google Workspace CLI (gws). Covers auth setup, credential storage, scope management, and troubleshooting.
---

# GWS Shared — Auth & Configuration

The `gws` CLI (v0.22.5) provides unified access to all Google Workspace APIs. Already installed and authenticated on this machine.

## Quick Verification

When the user says a tool is "already installed and authenticated", ALWAYS verify first:

```bash
which gws && gws --version && gws auth status
```

Do NOT attempt installation if the binary exists and auth is valid.

## Authentication Status

- **User**: <YOUR_EMAIL>
- **Auth method**: OAuth2 (encrypted credentials)
- **Credential storage**: `~/.config/gws/credentials.enc` (AES-256-GCM, OS keyring)
- **Client config**: `~/.config/gws/client_secret.json`
- **Scopes (11)**: email, calendar, cloud-platform, documents, drive, gmail.modify, presentations, spreadsheets, tasks, userinfo.email, openid

## Auth Commands

```bash
gws auth status          # Check current auth state
gws auth login           # Re-authenticate (interactive)
gws auth setup           # First-time setup (creates Cloud project + OAuth)
gws auth export          # Export credentials for headless use
```

## Scope Notes

- Unverified OAuth apps are limited to ~25 scopes
- The `recommended` preset (85+ scopes) WILL FAIL in testing mode
- Use individual services: `gws auth login -s drive,gmail,sheets`
- Current scopes cover: Gmail (modify), Calendar, Drive, Docs, Sheets, Slides, Tasks

## Environment Variables (headless/CI)

```bash
export GOOGLE_WORKSPACE_CLI_TOKEN=$(gcloud auth print-access-token)
# OR
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/credentials.json
```

## Command Syntax Pitfall

`gws` uses **helper commands** with `+` prefix, NOT standard REST resource paths:

```bash
# WRONG — standard REST path
gws gmail messages list
gws drive files list

# CORRECT — helper commands
gws gmail +triage                    # Inbox summary
gws gmail +read --params '{"id": "..."}'  # Read a message
gws gmail +send --params '{"to": "...", "subject": "...", "body": "..."}'
gws gmail +reply --params '{"id": "...", "body": "..."}'
gws drive files list --params '{"pageSize": 10}'  # Some resources DO use subcommands
```

Rule of thumb: Gmail uses `+helpers`, Drive/Sheets/Calendar use subcommands. Check `gws <service> --help` when unsure.

## Full Command Reference

See `references/gws-command-reference.md` for the complete command reference for all 17 services.
