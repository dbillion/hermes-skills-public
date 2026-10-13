# tailscale serve --tcp (new CLI syntax, v1.102+)

## The old/intuitive form is WRONG
- `tailscale serve tcp 7456` → "invalid argument format" (tcp read as subcommand).
- `tailscale serve --tcp 7456` → "invalid argument format" (no target given).
- `tailscale serve --tcp 100.71.136.81:7456` → "invalid value ... parse error"
  (`--tcp` takes a bare port only).

## Correct form
```
tailscale serve --bg --tcp //localhost:7456 --yes
```
- `--tcp 7456` = the **tailnet-side** listen port (what remote peers connect to).
- `//localhost:7456` = the **local backend** to forward to. The leading `//` makes it a
  `tcp://` scheme URL without the `tcp:` prefix (the new parser requires this shape).
- `--bg` runs it as a background serve; `--yes` skips the interactive prompt.
- Verify: `tailscale serve status --json`.

## Separate concern
- `tailscale serve --tcp` exposes a *local app* (e.g. the open-design node on :7456) over
  the tailnet. It is NOT for SSH — sshd on :22 is reachable directly via the node's
  tailnet IP (`ssh user@$(tailscale ip -4)`), no `serve` needed.
