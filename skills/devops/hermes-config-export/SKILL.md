---
name: hermes-config-export
description: "Export and share Hermes Agent configuration — skills, config, memories, profiles — as a git repo or zip archive. Use when setting up a new Hermes instance, backing up your config, or sharing your setup with others."
---

# Hermes Config Export

Export your entire Hermes setup so another instance can import it with one command.

## What Gets Exported

```
hermes-config/
├── config/
│   ├── config.yaml         # Settings (API keys redacted)
│   └── .env.example        # Template for required keys
├── skills/                 # All custom skills
├── memories/
│   ├── MEMORY.md           # Personal notes
│   └── USER.md             # User profile
├── profiles/               # Profile configs
├── scripts/
│   ├── install.sh          # One-command install
│   └── export.sh           # Export current state
└── .gitignore
```

## Option A: Git Repo (Recommended)

### Export
```bash
# Run the export script
bash ~/.hermes/skills/hermes-config-export/scripts/export.sh
```

This creates `./hermes-config/` with all skills, config, and memories. API keys are automatically redacted.

### Install (on another Hermes instance)
```bash
git clone <your-repo-url> hermes-config
cd hermes-config
bash scripts/install.sh
```

The install script:
1. Copies `config.yaml` to `~/.hermes/config.yaml`
2. Copies skills to `~/.hermes/skills/`
3. Copies memories to `~/.hermes/memories/`
4. Prompts for `.env` values (API keys, tokens)
5. Runs `hermes doctor` to verify

## Option B: Zip Archive

### Export
```bash
bash ~/.hermes/skills/hermes-config-export/scripts/export.sh --zip
# Creates: hermes-config-YYYYMMDD.zip
```

### Install
```bash
unzip hermes-config-YYYYMMDD.zip
cd hermes-config
bash scripts/install.sh
```

## What's Redacted

The export script automatically redacts:
- API keys (`sk-*`, `ghp_*`, `AIza*`, etc.)
- Tokens (`Bearer ...`, `token=...`)
- Passwords
- Secret values in `.env`

Replace with `PLACEHOLDER` values in `.env.example`.

## Customization

Edit `scripts/export.sh` to:
- Add/remove skill directories to include
- Change redaction patterns
- Add profile-specific exports
- Include/exclude session data

## Tips

- Use git for ongoing sync between instances
- Run export after adding new skills or changing config
- Keep `.env` out of git — only commit `.env.example`
- Branch for different profiles (work, personal, etc.)
