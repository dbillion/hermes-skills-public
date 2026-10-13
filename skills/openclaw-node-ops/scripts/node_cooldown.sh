#!/usr/bin/env bash
# Stop the node Hermes gateway and keep it DOWN during a cooldown (Restart=no).
# Run on the node by path (see references/gateway-guard-workaround.md).
set -e
UNIT="$HOME/.config/systemd/user/hermes-gateway.service"
if grep -q '^Restart=' "$UNIT"; then
  sed -i 's/^Restart=.*/Restart=no/' "$UNIT"
else
  echo 'Restart=no' >> "$UNIT"
fi
systemctl --user daemon-reload
P=$(pgrep -o -f 'venv/bin/python -m hermes_cli')
[ -n "$P" ] && /bin/kill -TERM "$P"
sleep 2
pgrep -f 'venv/bin/python -m hermes_cli' >/dev/null && echo "STILL_UP" || echo "DOWN_FOR_COOLDOWN"
