# WinBoat install + precheck recipe (Arch Linux)

## Precheck (read-only, run before install)
```bash
ls -la /dev/kvm                 # must exist → KVM available
docker info >/dev/null 2>&1 && echo "docker OK" || echo "docker DOWN"
which yay                       # AUR helper
pacman -Q winboat 2>/dev/null || echo "not installed"
sudo -n true 2>&1 && echo "sudo passwordless" || echo "sudo NEEDS password"
```

## Install (requires sudo — agent usually blocked here)
User runs in their own terminal:
```bash
yay -S winboat
# prompts: cleanBuild [N], Diffs [N]; then sudo password
```
The AUR source lands in `~/.cache/yay/winboat/` (PKGBUILD + src). If a previous
attempt left it half-built but uninstalled (`pacman -Q winboat` → "not found"),
just re-run `yay -S winboat` — it resumes from build files and finishes the install step.

## First launch
- WinBoat is a GUI Electron app. Launch it; first-run wizard picks Windows version + resources.
- It downloads a Windows image (several GB) into a Docker container — expected, slow first time.
- Then: "Install New App" → in-VM File Explorer → run the `.exe`/`.msi`.
- App composites as a native OS-level window via FreeRDP/RemoteApp.

## Blocker notes
- sudo is NOT passwordless for the agent on this machine → `yay`/any `pacman -S` must be
  done by the user, OR a `/etc/sudoers.d/` passwordless rule is added for the agent.
- WinBoat needs Docker + KVM; if either is missing, install fails.
- WinBoat does NOT need wine installed (it's a VM, not a translator).
