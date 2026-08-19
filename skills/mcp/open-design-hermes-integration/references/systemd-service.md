# systemd --user unit for the Open Design daemon

Save as `~/.config/systemd/user/open-design-daemon.service`. Pin Node 24 so the
native `better-sqlite3` (ABI 137) matches the runtime — without the pin the
daemon crashes with `ERR_DLOPEN_FAILED` under Node 25/22.

```ini
[Unit]
Description=Open Design local daemon (MCP + agent adapter for Hermes)
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/deeone/open-design/open-design
# Pin Node 24 so better-sqlite3 (ABI 137) matches the runtime.
Environment=PATH=/home/deeone/.nvm/versions/node/v24.19.0/bin:/usr/local/bin:/usr/bin:/bin
Environment=OD_DATA_DIR=/home/deeone/open-design/open-design/.od
ExecStart=/home/deeone/.nvm/versions/node/v24.19.0/bin/node /home/deeone/open-design/open-design/apps/daemon/bin/od.mjs --no-open --host 127.0.0.1 --port 7456
Restart=on-failure
RestartSec=5
TimeoutStartSec=60

[Install]
WantedBy=default.target
```

Enable + start:
```bash
systemctl --user daemon-reload
systemctl --user enable --now open-design-daemon.service
systemctl --user status open-design-daemon.service   # expect active (running), HTTP 200 on :7456
```

Requires `loginctl enable-linger $USER` for the service to survive logout/reboot
(already set on this host). To stop/restart: `systemctl --user stop|restart
open-design-daemon.service`.
