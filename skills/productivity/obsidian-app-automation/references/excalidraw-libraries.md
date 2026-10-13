# Excalidraw stencil libraries in Obsidian

Verified end-to-end on Obsidian 1.13.4 + Excalidraw plugin 2.26.3 (Linux).

## The core trap: visible ≠ active

Downloading `.excalidrawlib` files into the library folder makes them appear in
Obsidian's file index and in `ls`, but the Excalidraw plugin **will not load
them**. It reads exactly ONE file.

Session evidence: 8 libraries / 137 items were downloaded, the file index listed
all 8 — and the plugin had **0** of them. The plugin even rewrote its own
library file nine minutes *after* the downloads without absorbing any.

Answer "how many are active?" from plugin state only.

## Find the real target file

```bash
python3 -c "
import json; d=json.load(open('<vault>/.obsidian/plugins/obsidian-excalidraw-plugin/data.json'))
for k in ['libraryStorageMode','libraryFolderPath','libraryFileName']: print(k,'=',repr(d.get(k)))"
```

Typical: `libraryStorageMode='vault'`, `libraryFolderPath='Excalidraw/Libraries'`,
`libraryFileName='local-library'` → the only file read is
`<vault>/Excalidraw/Libraries/local-library.excalidrawlib`.

Do **not** trust `data.json`'s `library2.libraryItems` count. In `vault` storage
mode it is unused and reads `0` even when the plugin has items loaded.

## Catalog and download

231 libraries are indexed at `https://libraries.excalidraw.com/libraries.json`.
Each entry has `name`, `description`, `source`, and usually `id`.

- Fetch a library: `https://libraries.excalidraw.com/libraries/<source>`
- **Not every entry has an `id`** — guard with `L.get('id')` or you get a
  `KeyError` mid-loop.
- A `libraries.excalidraw.com/?...&token=...` URL is the **browser UI** with a
  session token, not a single downloadable library. Do not try to fetch it as a
  file; ask which library is wanted, or select from the catalog.

Always `json.loads()` each download before writing it — catches truncated fetches.

## Two library formats

| version | shape | handling |
|---|---|---|
| v2 | `{"libraryItems": [{"elements": [...]}, ...]}` | use directly |
| v1 | `{"library": [[el, el], ...]}` — items are **bare element arrays** | wrap: `{"elements": item}` |

Missing the v1 case makes item counts look right while element counts read `0`.

```python
items = d.get("libraryItems") or d.get("library") or []
for it in items:
    if isinstance(it, list):
        it = {"elements": it}   # v1
```

## Merge recipe (activation)

Back up first — this is the plugin's managed file.

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
        if isinstance(it, list):
            it = {"elements": it}                    # v1 normalisation
        k = json.dumps(it.get("elements"), sort_keys=True)
        if k in seen:
            continue
        seen.add(k)
        it.setdefault("status", "unpublished")
        it.setdefault("created", int(time.time() * 1000))
        it.setdefault("id", f"m-{abs(hash(k)) % 10**12}")
        merged.append(it)

json.dump({"type": "excalidrawlib", "version": 2,
           "source": cur.get("source"), "libraryItems": merged},
          open(target, "w"), indent=1)
```

Validate before restarting: every item a dict, non-empty `elements`, every
element a dict with a `type`, and the pre-existing item still present.

## Verify activation

```bash
obsidian eval code="(()=>{const m=app.plugins.plugins['obsidian-excalidraw-plugin'].stencilLibraryManager;const ci=m.currentItems||[];return JSON.stringify({loaded:m.loaded,count:ci.length,els:ci.reduce((a,i)=>a+((i.elements||[]).length),0)});})()"
```

`stencilLibraryManager.currentItems` is the authoritative count. Note:
- There is **no** `getLibrary()` method — that guess fails. The real surface is
  `getStencilLibrary` / `setStencilLibrary` / `stencilLibraryManager`. Enumerate
  with `Object.getOwnPropertyNames` instead of guessing.
- Expect the loaded count to **exceed** the merged count: the plugin also reads
  sibling `.excalidrawlib` files in that folder in their own format, so v1
  libraries get counted twice (harmless duplication, not data loss). Reconcile
  the arithmetic before reporting, and offer to dedupe.
- Most upstream items are **unnamed** (e.g. 26 named out of 150). Normal — they
  render as thumbnails.

## Reload caution

`obsidian reload` may **kill** the app instead of reloading it. Verify with
`pgrep -c electron39` / the REST endpoint, and relaunch with
`terminal(background=True)` if it died. Do not use shell `nohup`/`&`.

Panel caching: after activation, an already-open drawing may show a stale
library panel. Close and reopen the drawing.
