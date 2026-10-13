---
name: run-windows-exe-linux
description: Run Windows .exe on Linux. Wine first, WinBoat VM fallback.
---

# Run a Windows .exe on Linux

Class-level workflow for executing Windows binaries on a Linux dev machine — the recurring "help me run this .exe" task. Two tools, with a clear decision rule.

## The decision rule (most important)
- **Try Wine first.** It's lightweight (translates Windows syscalls; no VM). Works for most CLI/GUI apps.
- **Fall back to WinBoat when the exe crashes / hangs under Wine.** WinBoat runs a *full Windows VM inside Docker+KVM* and composites the app windows onto your Linux desktop via FreeRDP/RemoteApp — so apps that misbehave under Wine (Office, Adobe, and in practice random bundled downloaders) usually run fine.
- Do NOT skip straight to WinBoat for a small exe — it downloads a multi-GB Windows image and is heavy.

## Critical naming clarification (USER got this wrong once)
- **WinBoat ≠ WineBottler.** WineBottler is **macOS-only** and does not exist on Linux. **WinBoat** is a real, Linux-native open-source tool (winboat.app). Do not confuse the two when the user says "winboat".
- **WinBoat does NOT use Wine.** It is a Docker+KVM Windows VM. So "does WinBoat need wine?" → No. Installing wine is irrelevant to WinBoat.
- Arch package: `winboat` / `winboat-git` on the AUR (install via `yay -S winboat`).

## Path A — Wine (try first)
1. Check installed: `which wine` / `pacman -Q wine`. On Arch: `sudo pacman -S wine` (wine 11.x observed).
2. Run: `wine /path/to/app.exe`. Output often goes to the log file you redirect; GUI apps may print nothing.
3. **Detecting a hung/crashed Wine** (this is the signal to switch to WinBoat):
   - Process alive but **0.0% CPU for >60s** and no window appears → hung (typically stuck in `wineboot.exe --init` first-run prefix setup).
   - `cat ~/.wine/drive_c/...` log empty, no "Unhandled exception"/"Exception"/"err:" in watch patterns → not crashed-yet, just stuck.
   - If it actually crashes you'll see "Unhandled exception" and the process exits.
   - **Action on hang:** kill the wine processes (`pkill -f <exe>` + `pkill -f "wineboot.exe --init"`), then move to WinBoat.
4. Note: `DISPLAY` must be set (e.g. `DISPLAY=:1`) for GUI apps to open a window — verify before concluding it failed.

## Path B — WinBoat (when Wine fails)
Prerequisites (verify read-only first):
- `ls /dev/kvm` exists → KVM hardware virtualization available.
- Docker daemon running (`docker info` succeeds) — WinBoat uses Docker + KVM.
- AUR helper present (`which yay`).
- **Install blocker: needs sudo, and sudo is typically NOT passwordless for the agent.** `yay -S winboat` will stall at the sudo prompt. Either the user runs it themselves, or sudo is made passwordless for the agent.
  - User-run recipe: `yay -S winboat` → answer N to cleanBuild/Diffs → enter sudo password → done.
- First launch downloads a **Windows image (several GB)** — expected, not an error.

Launch/use (GUI, user-driven):
- Start WinBoat (desktop app). First-run wizard picks Windows version + resources.
- "Install New App" → use its in-VM File Explorer to run the `.exe`/`.msi`.
- App then appears as a native OS-level window via RemoteApp.

## Pitfalls
- **Don't trust a bloat/system report's exe path blindly** — same as Docker cleanup: confirm the file exists (`ls -la`) before acting.
- **Agent cannot see GUI windows** — when you launch Wine/WinBoat, the user must confirm the window appeared on their desktop; the agent can only check process state + CPU + DISPLAY.
- **`sudo -n true` returns "a password is required"** on this machine → any `yay`/`pacman -S` install must be done by the user or after passwordless-sudo is granted.

## Support
- `references/winboat_install.md` — exact AUR install recipe, KVM/Docker precheck commands, and the sudo-blocker handling.
