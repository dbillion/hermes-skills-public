# Obsidian: Local REST API + reading plugin config

Companion notes for driving an Obsidian vault programmatically. The bundled
`obsidian` skill covers filesystem-first note work; this file covers the
*running app* surface and plugin-data discovery. Verified on vault
`/home/deeone/Documents/hgfh`.

## `obs` is NOT Obsidian — verify the binary first

Both `/usr/bin/obs` and `/usr/bin/obsidian` exist on this box, but **`obs` is
OBS Studio** (the video streamer). If `--help` prints `--startstreaming`,
`--startrecording`, `--scene`, you have the wrong tool. There is no official
Obsidian CLI installed here. Always confirm a candidate binary with `--help`
before building a workflow on it — the name collision is an easy silent trap.

## Local REST API plugin (the real programmatic path)

Plugin `obsidian-local-rest-api` v5.1.0+ ("Local REST API with MCP") serves the
live vault over HTTP **while Obsidian is running**.

- Insecure: `http://127.0.0.1:27123`  ·  TLS: `https://127.0.0.1:27124`
- Config + key: `<vault>/.obsidian/plugins/obsidian-local-rest-api/data.json`
  (`apiKey`, `port`, `insecurePort`, `enableInsecureServer`, `crypto`)

Liveness (no auth required):

```bash
curl -s -m 8 http://127.0.0.1:27123/
# {"status":"OK","manifest":{"id":"obsidian-local-rest-api", "version":"5.1.0", ...}}
```

Empty output / connection refused means Obsidian is not running — the plugin
only serves while the app is open. That is an app-state fact, not a broken API.

Authenticated calls:

```bash
python3 -c "import json;print(json.load(open('<vault>/.obsidian/plugins/obsidian-local-rest-api/data.json'))['apiKey'])" > /tmp/obs_key
curl -s -H "Authorization: Bearer $(cat /tmp/obs_key)" http://127.0.0.1:27123/vault/
curl -s -H "Authorization: Bearer $(cat /tmp/obs_key)" http://127.0.0.1:27123/vault/Excalidraw/Libraries/
```

**Never put the API key directly on the command line** — it lands in argv,
shell history, and logs. Write it to a file and interpolate with `$(cat ...)`.
Offer to move it somewhere permanent (`~/.config/obsidian-api-key`) and delete
the temp copy.

Because this plugin also speaks MCP, the vault can be registered as an MCP
server in `~/.mcp_servers.json` (see the parent SKILL.md registration recipe).

## Read plugin config instead of guessing paths

Every community plugin stores its settings at
`<vault>/.obsidian/plugins/<plugin-id>/data.json`. Read it to learn the real
folder layout rather than assuming conventional names.

Worked example — installing Excalidraw libraries:

1. `data.json` for `obsidian-excalidraw-plugin` gave
   `libraryStorageMode: "vault"` and `libraryFolderPath: "Excalidraw/Libraries"`.
   The folder did **not** exist yet and had to be created.
   (`libraryFolder` is a different, unrelated key and was `None` — do not read it.)
2. Catalog: `https://libraries.excalidraw.com/libraries.json` — 231 entries with
   `name`, `source`, `description`, and usually `id`.
   **Pitfall:** some entries have NO `id` key, so `L['id']` raises `KeyError`
   mid-loop. Use `L.get('id')` and skip falsy values.
3. Download each as `https://libraries.excalidraw.com/libraries/<source>`,
   `json.loads` the bytes to validate before writing, then save into the library
   folder. Count `libraryItems` to report what actually landed.
4. Verify through the REST API (`GET /vault/Excalidraw/Libraries/`) so you know
   the *app* sees the files, not just the filesystem.

A URL like
`https://libraries.excalidraw.com/?target=_blank&referrer=app%3A%2F%2Fobsidian.md&useHash=true&token=...`
is the **library browser with a session token**, not a single library. It does
not identify one item. Ask which library is wanted, or select by topic and
state plainly which ones you picked.

DSA/software-relevant library ids (useful for diagram work):

| id | name |
|---|---|
| `9yQARBgin4G` | Algorithms and Data Structures (arrays, matrices, trees) |
| `4lxTil7j6Pz` | Graphs |
| `9CN5lxMi2iu` | Shapes for UML & ER Diagrams |
| `4SlkJRmBgDQ` | System Design Components |
| `mzQjGLHnDi`  | Software Architecture |
| `73c4J61D8Ke` | Data Flow |
| `5EQHJmvPfDg` | Decision flow control |
| `3wNGI8ycyjj` | Database |
