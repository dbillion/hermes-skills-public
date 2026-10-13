---
name: wayland-computer-use
description: Native Wayland computer-use via spectacle + ydotool.
category: devops
---

# Wayland Computer-Use Provider

Native alternative to cua-driver for Wayland sessions (KDE Plasma, GNOME, sway, etc.).

## Prerequisites
```bash
# Arch/EndeavourOS
sudo pacman -S ydotool grim slurp spectacle --noconfirm
sudo usermod -aG input $USER
# logout/login or newgrp input

ydotoold  # daemon for ydotool
```

## Tools

### Screenshot
- `spectacle -b -o <file>` - full screen capture (KDE)
- `grim -g "$(slurp)" <file>` - region capture (wlroots)
- `grim <file>` - full screen (wlroots)

### Input (ydotool)
- `ydotool mousemove -a X Y` - absolute move
- `ydotool click 0xC0` - left click (down+up)
- `ydotool type "text"` - type string
- `ydotool key KEYCODE:1 KEYCODE:0` - key press/release

## Keycodes
Linux input event codes from `/usr/include/linux/input-event-codes.h`:
- `KEY_ENTER` = 28
- `KEY_ESC` = 1
- `KEY_TAB` = 15
- `KEY_SPACE` = 57
- `KEY_A`-`KEY_Z` = 30-55
- `KEY_1`-`KEY_0` = 2-11

## Usage
```bash
# Start ydotoold daemon
ydotoold &

# Capture screen
spectacle -b -o /tmp/screen.png

# Click at 100,100
ydotool mousemove -a 100 100 && ydotool click 0xC0

# Type text
ydotool type "hello world"

# Press Enter
ydotool key 28:1 28:0
```