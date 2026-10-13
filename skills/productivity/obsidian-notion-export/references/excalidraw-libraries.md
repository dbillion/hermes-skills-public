# Obsidian Excalidraw Library Activation

The Excalidraw plugin does NOT auto-load every `.excalidrawlib` file dropped
into its library folder. It reads exactly ONE file, named by `libraryFileName`
in the plugin's `data.json` (default `local-library.excalidrawlib`), located at
`libraryFolderPath` (e.g. `Excalidraw/Libraries`).

## Symptoms
- You copy 8 `.excalidrawlib` files into the folder; the Library panel shows none.
- `obsidian files folder="Excalidraw/Libraries"` returns NOTHING for non-md files
  unless you pass `ext=excalidrawlib`.
- The plugin rewrites `local-library.excalidrawlib` on its own (mtime newer than
  your copies) and ignores the extras.

## Fix (merge into the one file)
Concatenate every library's `libraryItems` into `local-library.excalidrawlib`:
```python
import json, glob, os
base = "<vault>/Excalidraw/Libraries"
target = os.path.join(base, "local-library.excalidrawlib")
cur = json.load(open(target))
items = cur.get("libraryItems", [])
seen = {json.dumps(it.get("elements"), sort_keys=True) for it in items}
for f in glob.glob(base + "/*.excalidrawlib"):
    if os.path.basename(f) == "local-library.excalidrawlib":
        continue
    d = json.load(open(f))
    for it in d.get("libraryItems") or d.get("library") or []:
        key = json.dumps(it.get("elements"), sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        items.append(it)
out = {"type": "excalidrawlib", "version": 2,
       "source": cur.get("source"), "libraryItems": items}
json.dump(out, open(target, "w"), indent=1)
```
Then reload Obsidian (`obsidian reload` — but note it may kill the app; relaunch
afterward) or reopen the Excalidraw Library panel.

## Verify activation
The plugin's runtime state confirms load (not just disk presence):
```
obsidian eval code="(()=>{const m=app.plugins.plugins['obsidian-excalidraw-plugin'].stencilLibraryManager;return JSON.stringify({loaded:m.loaded,count:(m.currentItems||[]).length});})()"
```
Expect `{"loaded":true,"count":N}` where N = total merged items.

## Alternative
Import each library manually via the Excalidraw UI: open a drawing → Library
panel → "Load library" per file. Native, zero risk, but manual.
