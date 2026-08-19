# Worked example: Excalidraw MCP + Obsidian CLI + stencil libraries

Verified end-to-end on Arch Linux. Three lessons that generalize:
registration ≠ installation, files-on-disk ≠ loaded state, and always
check the real binary before declaring a CLI missing.

---

## 1. Excalidraw MCP server

Already built locally but unregistered:

- server: `/home/deeone/picoclaw/excalidraw-mcp-app/excalidraw-mcp-app/dist/index.js`
- also: `~/.npm-global/bin/excalidraw-mcp-server`
- the `excalidraw-obsidian` skill documented the exact path — read skills during recon

Registration block for `~/.mcp_servers.json`:

```json
{
  "type": "stdio",
  "command": "node",
  "args": ["/home/deeone/picoclaw/excalidraw-mcp-app/excalidraw-mcp-app/dist/index.js", "--stdio"],
  "env": { "PORT": "3001", "HOST": "localhost", "DEBUG": "false" }
}
```

Tools: `read_me`, `create_view`, `export_to_excalidraw`, `save_checkpoint`, `read_checkpoint`.

- `read_me` returns a ~15KB cheat sheet (palette, element schema, camera rules). Call it first.
- `create_view` is a **UI/widget tool** — renders in an MCP-app iframe. Over `mcp-cli` you get
  the JSON envelope, not an image. Not a failure.
- `export_to_excalidraw` **uploads to excalidraw.com**. Third-party upload — ask before running.

---

## 2. Obsidian CLI — the binary confusion

**`obs` is OBS Studio. `obsidian` is Obsidian.** Testing with `obs` succeeds and prints
video-streaming flags, which reads as "wrong tool, no Obsidian CLI." That conclusion is wrong.

```bash
ls /usr/bin/obsidian          # the real CLI
obsidian version              # 1.13.4 (installer 1.12.7)
```

Facts worth keeping:

- Linux install is a bash wrapper around `electron39 /usr/lib/obsidian/app.asar`.
- Every call prints `vaInitialize failed: unknown libva error` to stderr. Harmless GPU noise.
  Use `2>/dev/null`.
- Obsidian must be RUNNING (IPC).
- `vault=<name>` must be the FIRST argument.

**GOTCHA — silent empty result:**

```bash
obsidian files folder="Excalidraw/Libraries"                  # -> NOTHING (filters to .md)
obsidian files folder="Excalidraw/Libraries" ext=excalidrawlib # -> all 8 files
```

Empty output here is indistinguishable from "not installed". Always retry with `ext=`.

**`obsidian reload` terminated the app** rather than reloading it; the vault and the REST API
went unreachable until relaunch. Prefer `obsidian plugin:reload id=<id>`. If you must relaunch,
use `terminal(background=true)` — shell `nohup`/`&` is rejected by the terminal tool.

**Local REST API plugin** (v5.1.0, also speaks MCP): `http://127.0.0.1:27123`, key at
`<vault>/.obsidian/plugins/obsidian-local-rest-api/data.json`. Keep the key out of argv:

```bash
curl -s -H "Authorization: Bearer $(cat /tmp/obs_key)" http://127.0.0.1:27123/vault/
```

Doubles as a liveness probe — connection refused means Obsidian is down.

---

## 3. The on-disk vs active trap (the important one)

Downloaded 8 libraries into `<vault>/Excalidraw/Libraries/`. Both the filesystem and
`obsidian files ... ext=` listed all 8. **Zero were active.**

The plugin reads exactly ONE file, named by its own settings:

```json
{ "libraryStorageMode": "vault",
  "libraryFolderPath": "Excalidraw/Libraries",
  "libraryFileName": "local-library" }
```

Everything else in that folder is ignored. The tell was `library2.libraryItems == 0`, plus the
plugin rewriting `local-library.excalidrawlib` nine minutes AFTER the downloads without
absorbing them.

Catalog: `https://libraries.excalidraw.com/libraries.json` (231 entries) →
fetch `https://libraries.excalidraw.com/libraries/<source>`. A `libraries.excalidraw.com/?token=…`
URL is the BROWSER with a session token, not a single library.

### Merge recipe (activates them)

```python
import json, glob, os, shutil, time
V = "<vault>/Excalidraw/Libraries"
target = os.path.join(V, "local-library.excalidrawlib")
shutil.copy(target, f"/tmp/local-library.bak_{int(time.time())}.excalidrawlib")

cur = json.load(open(target))
merged = list(cur.get("libraryItems", []))          # PRESERVE existing items
seen = {json.dumps(i.get("elements"), sort_keys=True) for i in merged}

for f in sorted(glob.glob(V + "/*.excalidrawlib")):
    if os.path.basename(f) == "local-library.excalidrawlib":
        continue
    d = json.load(open(f))
    for it in (d.get("libraryItems") or d.get("library") or []):
        if isinstance(it, list):            # v1 format: bare element arrays
            it = {"elements": it}
        k = json.dumps(it.get("elements"), sort_keys=True)
        if k in seen:
            continue
        seen.add(k)
        it.setdefault("status", "unpublished")
        merged.append(it)

json.dump({"type": "excalidrawlib", "version": 2,
           "source": cur.get("source"), "libraryItems": merged},
          open(target, "w"), indent=1)
```

Handle BOTH schemas: v2 uses `libraryItems` (list of dicts); **v1 uses `library`
(list of bare element arrays)**. Missing the v1 case silently drops items.

### Verify inside the app

```bash
obsidian eval code="JSON.stringify(Object.getOwnPropertyNames(app.plugins.plugins['obsidian-excalidraw-plugin']))"
# -> stencilLibraryManager, getStencilLibrary, exportLibrary, ...

obsidian eval code="(()=>{const m=app.plugins.plugins['obsidian-excalidraw-plugin'].stencilLibraryManager;return JSON.stringify({loaded:m.loaded,count:(m.currentItems||[]).length});})()"
# -> {"loaded":true,"count":150}
```

`settings.library2` stays 0 in vault mode — it is unused there. Do not read it as the answer.
`getLibrary()` does not exist; enumerating property names found the real API.

**Reconcile the delta:** merged file had 138 items but the plugin reported 150. The extra 12 were
`graphs.excalidrawlib`, a **v1** file the plugin also loads independently. Duplication, not loss.
Always explain a mismatch rather than reporting the bigger, flattering number.

---

## Checklist

1. Is it installed? (filesystem + skills) — before saying "unavailable".
2. Probe with a scratch `-c` config; make a REAL tool call.
3. Back up shared config, merge, verify count and that old entries survived.
4. Re-verify WITHOUT `-c`.
5. For plugin data: query the running app, never the filesystem.
6. Reconcile any count mismatch before reporting.
