# Scavenger Hunt: Checking for Existing Resources
When a tool or behavior seems wrong, or something "doesn't exist," check these locations BEFORE adapting.

## User-Specific Skill Locations

### Primary directories to check:
1. `~/.hermes/skills/` — Primary Hermes skills (structured `<category>/<name>/SKILL.md`).
2. `~/.gemini/skills/` + `~/.gemini/extensions/` — **CRITICAL**: Google Gemini CLI imports. Many skills are packed here and should be imported into Hermes if they did not come through the Skills Hub.
3. `~/.openclaw-imports/` — External imported skills (defuddle, browser-use, shadcn-ui, etc.) — each imported skill has its own subdirectory.
4. `~/.agents/skills/` — Older agent framework skills (rarely used).

### Gemini Extension Format
Gemini extensions live in `~/.gemini/extensions/<name>/` with:
- `GEMINI.md` — The prompt/instruction content (this becomes the Hermes SKILL.md body)
- `gemini-extension.json` — MCP server config (command + args)
- Files in `skills/<name>/` subdirectory with per-skill SKILL.md scripts

### Converting a Gemini Extension to Hermes Skill
```
skill category: based on domain (e.g., devops/, frontend/, productivity/)
skill name: the extension directory name (e.g., gcloud-mcp, firebase)
skill content: copy GEMINI.md → Hermes SKILL.md body (add YAML frontmatter)
mcp_servers: extract from gemini-extension.json → SKILL.md mcp_servers field
```

### Converting Gemini Skills to Hermes Skills
Gemini skills in `~/.gemini/skills/<name>/` are often individual scripts:
- `gws-gmail/`, `gws-calendar/`, `gws-drive/` — These should become reference files under an existing umbrella skill (like `google-workspace`) if the umbrella already exists, OR as standalone skills if unique.

## User Environment Check
### Important gcloud / CLI setup
```bash
gcloud config get-value project
gcloud auth list
gcloud components list 2>/dev/null | grep alpha
```

### Rails Server Process Check
```bash
lsof -i :3000 | grep -i ruby
```

## Common "False Negative" Patterns
| Symptom | Checklist |
|---------|-----------|
| "Skill doesn't exist" | Check `~/.hermes/skills/`, `~/.gemini/skills/`, `~/.gemini/extensions/` before creating new ones |
| "CLI can't do X" | `which <binary>`, `gcloud auth`, install alpha components |
| "API key missing" | Check `~/.mcp_servers.json` |
| "Feature unavailable" | Check Node 18+, check if MFA blocks scoped API |
| "Can't find skill" | Namespaced paths: `stitch-to-rails-erb` vs `frontend/stitch-to-rails-erb` — use bare name without category prefix |
