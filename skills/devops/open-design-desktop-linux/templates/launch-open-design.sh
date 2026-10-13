#!/usr/bin/env bash
# Open Design — full-stack launcher for EndeavourOS (idempotent).
# Fixed ports (7456 daemon / 4173 web) so the web proxy rewrite target always
# matches the daemon. If a stack is already running, start only the desktop
# window (not the daemon) to avoid EADDRINUSE quick-fail on the port.
#
# Copy this to /home/deeone/open-design/launch-open-design.sh, chmod +x, and
# point the .desktop Exec at it. 3000 (linkedin-scrape) and 3001 (RedAmon) are
# owned by other apps; 7456 + 4173 are kept free for Open Design.
set -e
export PATH="/home/deeone/.nvm/versions/node/v24.19.0/bin:$PATH"
cd /home/deeone/open-design/open-design

DAEMON_UP=0
curl -s -o /dev/null http://127.0.0.1:7456/ 2>/dev/null && DAEMON_UP=1 || DAEMON_UP=0

if [ "$DAEMON_UP" -eq 1 ]; then
  echo "[launch-open-design] daemon already up on :7456 — starting desktop window only."
  exec pnpm tools-dev start desktop --daemon-port 7456 --web-port 4173
else
  echo "[launch-open-design] starting full stack (daemon + web + desktop)."
  exec pnpm tools-dev start --daemon-port 7456 --web-port 4173
fi
