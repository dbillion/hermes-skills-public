#!/usr/bin/env bash
# Restore auto-respawn and start the node Hermes gateway after a cooldown.
# Run on the node by path (see references/gateway-guard-workaround.md).
set -e
UNIT="$HOME/.config/systemd/user/hermes-gateway.service"
sed -i 's/^Restart=.*/Restart=always/' "$UNIT"
systemctl --user daemon-reload
systemctl --user start hermes-gateway.service
sleep 3
pgrep -f 'venv/bin/python -m hermes_cli' >/dev/null && echo "RESUMED" || echo "NOT_RUNNING"
