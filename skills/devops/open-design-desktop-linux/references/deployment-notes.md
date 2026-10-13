# Open Design Desktop on Linux — Deployment Notes

Condensed, session-specific detail backing SKILL.md. Update as you re-verify.

## Verified environment
- Host: EndeavourOS (Arch), KDE Plasma, user `deeone`, home `/home/deeone`.
- Node: `/home/deeone/.nvm/versions/node/v24.19.0/bin` (pin in ~/.bashrc).
- OD source: `/home/deeone/open-design/open-design` (v0.19.2).
- Other apps holding ports: `3000` linkedin-scrape (pid 770), `3001` RedAmon.
- OD canonical ports used: daemon `7456`, web `4173`.

## Save bug — exact symptom (browser console via tools-dev web log)
```
[browser] ⨯ unhandledRejection: TypeError: Failed to fetch
    at AppInner.useCallback[handleConfigPersist] (src/App.tsx:2650:25)
[browser] [projects] failed to refresh after workspace switch TypeError: Failed to fetch
```
Root cause: web `next.config.ts` rewrites `/api/*` → `OD_PORT` (default 7456).
When `pnpm tools-dev` randomized the daemon to 37131, the web proxied to 7456
(nothing listening) → every save is a connection-refused.

## End-to-end save test that PROVES the fix
```
PUT http://127.0.0.1:4173/api/app-config  -> HTTP 200
```
This is exactly the request the Electron renderer makes. 200 = saves work.

## Hermes model fix — exact call
```
GET  /api/app-config   -> shows agentModels.hermes = { model: "hy3:free" }
PUT  /api/app-config    body { agentModels: { hermes: { model: "default" } }, ... }  -> 200
```
Smoke test before fix: `[test:agent] Hermes → not_found_model: Model 'hy3:free' not found`.
After fix the run proceeds.

## deepseek-harness (dsh) — status as of this session (UNRESOLVED)
- Installed: `npm install -g @deepseek-ai/dsh@0.1.0-rc.6` → `dsh --version` = `0.1.0-rc.6`. OK.
- Profile created: `dsh plugin --profile open-design --help` initialized
  `~/.dsh/profiles/open-design`. (The `--help` side-effect creates the profile.)
- OD STILL reports `deepseek-harness: available:false, not-on-path` even after:
  (a) dsh on Node24 bin (symlink), and
  (b) a real wrapper at `~/.local/bin/dsh` (exec -> node24 bin/dsh).
- OD diagnostics list `fixActions: [{kind:"setEnv", envKey:"DSH_BIN"}]`.
  NEXT STEP to try (not yet verified): export `DSH_BIN=/home/deeone/.local/bin/dsh`
  in the daemon env and restart the stack; confirm OD flips to `available:true`.
- Do NOT claim deepseek-harness works until OD reports `available:true`.

## KDE menu + autostart — verified sequence
```
# write ~/.local/share/applications/open-design-default.desktop  (Categories=Development; single)
kbuildsycoca6 --noincremental
kquitapp6 plasmashell; plasmashell --no-desktop &   # repaint menu
# autostart: copy same .desktop -> ~/.config/autostart/open-design.desktop
desktop-file-validate ~/.local/share/applications/open-design-default.desktop   # must be clean
```
Icon must exist: `~/.local/share/icons/hicolor/512x512/apps/open-design-default.png`.

## Stopping the stack — DO NOT pkill -f
`pkill -f "next dev"` / `pkill -f "tools/dev"` SIGTERMs the agent's own shell (exit -15).
Instead extract exact PIDs:
```
D=$(ss -ltnp | grep 7456 | grep -oE 'pid=[0-9]+' | cut -d= -f2)
W=$(ss -ltnp | grep 4173 | grep -oE 'pid=[0-9]+' | cut -d= -f2)
kill $D $W
```

## Security audit of dbillion/hermes-setup — CLEAN
`grep -rniE 'ghp_|gho_|ghu_|sk-[A-Za-z0-9]{12}|AKIA[0-9A-Z]{12}|xox[baprs]-|eyJ[A-Za-z0-9_-]{10}\.' \
  . --include=*.yaml --include=*.json --include=*.template | grep -v '\${ENV:'`
Only hits: mock tokens in unit tests (`gho_abc123`) and redacted sample (`xoxb-Y...OKEN`).
Real secret files are gitignored and untracked. Templates use `${ENV:VAR}`. Safe to share.
