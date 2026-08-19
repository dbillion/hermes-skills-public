# Agentic CLI probe results (host machine, this session)

Probed each CLI non-interactively (version + a `-p`/`exec` prompt) to see which are
usable as sub-agents. `command -v` first, then a real prompt.

| CLI | Installed | Auth / usable? | Notes |
|---|---|---|---|
| **pi** | yes (`~/.nvm/.../bin/pi` v0.84.1) | ✅ **works** | `pi -p "..."` returned clean output; has read/bash/edit/write tools. The one proven sub-agent. |
| kilo | yes (`/usr/bin/kilo` 7.4.17) | untested prompt | present; not probed with a prompt this session. |
| kiro | yes (`/usr/bin/kiro` 0.11.107) | untested prompt | present; not probed with a prompt. |
| antigravity | yes (`/usr/local/bin/antigravity`) | ❌ hangs | launched a browser/DevTools and never returned (killed at 220s). |
| cursor | yes (`/usr/bin/cursor`) | ❌ GUI only | no CLI stdout; not usable as a subprocess sub-agent. |
| gemini | yes (`~/.nvm/.../bin/gemini` 0.48.0) | ❌ "Invalid auth method" | not logged in for non-interactive use. |
| codex | yes (`~/.nvm/.../bin/codex` 0.130.0) | ⚠️ broken config | starts but errors loading `~/.codex/skills/*.md` (invalid YAML); exit 101. |
| claude | yes (`~/.nvm/.../bin/claude` 2.1.222) | ❌ "Not logged in · run /login" | needs auth. |
| qwen | yes (`~/.nvm/.../bin/qwen` 0.14.5) | ❌ hung | timed out (124) on a `-p` prompt. |
| opencode / devin / grok / deepseek / vela | **no** | n/a | not installed. |

## How to re-probe
```
for c in pi kilo kiro claude codex gemini qwen; do
  command -v "$c" && timeout 45 "$c" -p "Reply with exactly: PONG" 2>&1 | head -3
done
```
Flag meanings: `-p` = print/non-interactive prompt mode; for codex use `codex exec "..."`.

## Takeaway
Only **pi** is a verified, authenticated, non-interactive sub-agent on this host. Others
need login (claude/gemini), have broken configs (codex), hang (qwen/antigravity), or are
GUI-only (cursor). Don't claim the others work until re-probed and authenticated.
