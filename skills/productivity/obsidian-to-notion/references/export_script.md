# Single-pass Obsidian → Notion exporter (via Notion MCP)

Verified on 2026-08-10 moving 4 vaults (460 notes) into Notion. One page per note,
full fidelity, zero dupes. Run per vault; give each vault its own parent page first
(`API-post-page` under a known parent), then pass that parent id.

```python
#!/usr/bin/env python3
"""obsidian_to_notion_mcp.py — one page per note, markdown via Notion MCP."""
import argparse, glob, json, os, re, subprocess, sys, time, urllib.request

API = "https://api.notion.com/v1"; VER = "2022-06-28"
OBS_RE = re.compile(r"!\[\[([^\]]+)\]\]")
WL_RE = re.compile(r"(?<!\[)\[\[([^\]]+?)(?:\|([^\]]+))?\]\]")
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf"}
VAULTS = {  # adjust to your paths
    "hgfh": "/home/deeone/Documents/hgfh",
    "dailybrain": "/home/deeone/Obsidian/dailybrain",
    "ideaverse": "/home/deeone/Documents/Ideaverse Lite 1.5/Ideaverse Lite 1.5",
    "obsidianvault": "/home/deeone/Documents/Obsidian Vault",
}

def mcp(tool, args):
    p = subprocess.run(["mcp-cli", "call", "notion", tool, json.dumps(args)],
                       capture_output=True, text=True, timeout=240)
    out = p.stdout.strip()
    try:
        env = json.loads(out)
        if isinstance(env, dict) and "content" in env:
            out = env["content"][0]["text"]
    except Exception:
        pass
    return p.returncode, json.loads(out)

def token():
    d = json.load(open(os.path.expanduser("~/.mcp_servers.json")))
    return d["mcpServers"]["notion"]["env"]["NOTION_TOKEN"]

def raw_call(m, p, body=None, binary=None, ctype=None, tok=None):
    h = {"Authorization": f"Bearer {tok}", "Notion-Version": VER}
    data = None
    if binary is not None:
        h["Content-Type"] = ctype; data = binary
    elif body is not None:
        h["Content-Type"] = "application/json"; data = json.dumps(body).encode()
    r = urllib.request.Request(API + p, data=data, headers=h, method=m)
    for _ in range(5):
        try:
            with urllib.request.urlopen(r, timeout=120) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode() or "{}")
            if e.code in (429, 502, 503, 504) or err.get("code") in ("rate_limited", "service_unavailable"):
                time.sleep(5); continue
            return e.code, err
    return 429, {"code": "rate_limited"}

def clean_title(path):
    base = os.path.splitext(os.path.basename(path))[0]
    return re.sub(r"^[A-Za-z0-9]+_", "", base) or base

def gather(vp):
    # os.path.isfile guards against Obsidian folders named *.md
    return sorted(f for f in glob.glob(vp + "/**/*.md", recursive=True)
                 if os.path.isfile(f) and "/.obsidian/" not in f and "/.trash/" not in f)

def upload_file(local, tok):
    name = os.path.basename(local)
    ctype = "application/pdf" if name.lower().endswith(".pdf") else "image/png"
    st, js = raw_call("POST", "/file_uploads", {"filename": name, "content_type": ctype}, tok=tok)
    if st != 200 or "id" not in js:
        return None
    with open(local, "rb") as fh:
        data = fh.read()
    r = urllib.request.Request(js["upload_url"], data=data, headers={"Content-Type": ctype}, method="PUT")
    urllib.request.urlopen(r, timeout=180).read()
    return f"notion://file_upload/{js['id']}"

def process_embeds(md, vp, tok):
    up = 0; fail = []
    def repl(m):
        nonlocal up
        base = m.group(1).split("|")[0].strip()
        local = os.path.join(vp, base) if os.path.exists(os.path.join(vp, base)) else None
        if not local:
            for ext in IMG_EXT:
                if os.path.exists(os.path.join(vp, base + ext)):
                    local = os.path.join(vp, base + ext); break
        if not local:
            fail.append(base); return m.group(0)
        url = upload_file(local, tok)
        if not url:
            fail.append(base); return m.group(0)
        up += 1
        return f"![]({url})"
    return OBS_RE.sub(repl, md), up, fail

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True, choices=list(VAULTS))
    ap.add_argument("--parent", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    tok = token()
    vp = VAULTS[args.vault]
    files = gather(vp)
    print(f"[*] {args.vault}: {len(files)} files", flush=True)
    created = 0; fails = []; emb_up = 0; emb_fail = 0
    for i, f in enumerate(files, 1):
        t = clean_title(f)
        md = open(f, encoding="utf-8", errors="ignore").read()
        md, nu, nf = process_embeds(md, vp, tok)
        emb_up += nu; emb_fail += len(nf)
        if args.dry_run:
            print(f"  [{i}/{len(files)}] {t} embeds_up={nu} emb_fail={len(nf)}", flush=True)
            continue
        st, js = mcp("API-post-page",
                     {"parent": {"page_id": args.parent},
                      "properties": {"title": [{"text": {"content": t[:100]}}]},
                      "markdown": md})
        if st == 0 and js.get('id'):
            created += 1
        else:
            fails.append((t, js.get('message', '')[:100]))
        if i % 10 == 0:
            print(f"[*] progress {i}/{len(files)} created={created}", flush=True)
        time.sleep(0.3)
    print(f"[*] DONE {args.vault}: created={created} fails={len(fails)} "
          f"embeds_uploaded={emb_up} embeds_failed={emb_fail}", flush=True)

if __name__ == "__main__":
    main()
```

## Usage
```bash
# one parent page per vault, created via:
mcp-cli call notion API-post-page '{"parent":{"page_id":"<ROOT>"},"properties":{"title":[{"text":{"content":"Obsidian Export — hgfh"}}]}}'
# then:
python3 obsidian_to_notion_mcp.py --vault hgfh --parent <PARENT_ID>
```
For 80+ notes run in background (`terminal(background=True, notify_on_complete=True)`);
~7s per note (npx warm). Verify after: count child pages under the parent and read back
blocks of one note with `API-get-block-children`.

## Notes / trade-offs
- Wikilinks `[[Note]]` stay literal text (single-pass can't know target IDs). Acceptable.
- Images embedded via `![[local.png]]` are uploaded; remote URLs pass through untouched.
- Excalidraw `.excalidraw`, `.canvas`, `.base` files have no Notion equivalent — skipped
  (only `.md` is gathered).
