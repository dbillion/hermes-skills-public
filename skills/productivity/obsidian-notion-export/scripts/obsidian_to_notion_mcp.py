#!/usr/bin/env python3
"""Obsidian -> Notion via the Notion MCP (mcp-cli). Full fidelity, single-pass.

For each vault:
  - gather .md files (skip dirs, .obsidian, .trash)
  - upload local ![[embeds]] via raw /v1/file_uploads
  - create one Notion page per note under a per-vault parent, with `markdown` body
  - wikilinks resolve to literal [[Note]] (no-dupe single pass)

Usage:
  python3 obsidian_to_notion_mcp.py --vault hgfh --parent <PAGE_ID>
  (vaults: hgfh, dailybrain, ideaverse, obsidianvault)

GOTCHAS encoded here (see SKILL.md for why):
  - mcp() uses subprocess input= (NOT argv, NOT stdin=open) to avoid ARG_MAX.
  - verifies js.get('id') and object=='page' (rc==0 is NOT enough; MCP returns
    HTML error pages with rc=0).
  - notes >~50KB must be split (Notion markdown cap). For a huge note, chunk at
    40000 chars into child pages of a split-parent.
  - gather() uses os.path.isfile to skip Obsidian folder-aliases ending in .md.
"""
import argparse, glob, json, os, re, subprocess, sys, time, urllib.request

API = "https://api.notion.com/v1"; VER = "2022-06-28"
OBS_RE = re.compile(r"!\[\[([^\]]+)\]\]")
WL_RE = re.compile(r"(?<!\[)\[\[([^\]]+?)(?:\|([^\]]+))?\]\]")
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf"}
VAULTS = {
    "hgfh": "/home/deeone/Documents/hgfh",
    "dailybrain": "/home/deeone/Obsidian/dailybrain",
    "ideaverse": "/home/deeone/Documents/Ideaverse Lite 1.5/Ideaverse Lite 1.5",
    "obsidianvault": "/home/deeone/Documents/Obsidian Vault",
}
CHUNK = 40000  # safe size for a single Notion markdown import


def mcp(tool, args):
    p = subprocess.run(["mcp-cli", "call", "notion", tool],
                       input=json.dumps(args).encode(),
                       capture_output=True, text=False, timeout=240)
    out = p.stdout.decode().strip()
    try:
        e = json.loads(out)
        if isinstance(e, dict) and "content" in e:
            out = e["content"][0]["text"]
    except Exception:
        pass
    try:
        return p.returncode, json.loads(out)
    except Exception:
        return p.returncode, {"_raw": out[:400]}


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
    return sorted(f for f in glob.glob(vp + "/**/*.md", recursive=True)
                 if os.path.isfile(f) and "/.obsidian/" not in f and "/.trash/" not in f)


def upload_file(local, tok):
    name = os.path.basename(local)
    ctype = "application/pdf" if name.lower().endswith(".pdf") else "image/png"
    st, js = raw_call("POST", "/file_uploads", {"filename": name, "content_type": ctype}, tok=tok)
    if st != 200 or "id" not in js:
        return None
    try:
        with open(local, "rb") as fh:
            data = fh.read()
        r = urllib.request.Request(js["upload_url"], data=data, headers={"Content-Type": ctype}, method="PUT")
        urllib.request.urlopen(r, timeout=180).read()
        return f"notion://file_upload/{js['id']}"
    except Exception:
        return None


def process_embeds(md, vp, tok):
    up = 0; fail = []
    def repl(m):
        nonlocal up
        base = m.group(1).split("|")[0].strip()
        local = None
        if os.path.exists(os.path.join(vp, base)):
            local = os.path.join(vp, base)
        else:
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


def create_page(parent, title, md):
    """Create a page with markdown. Returns (id_or_None, ok_bool)."""
    rc, js = mcp("API-post-page", {
        "parent": {"page_id": parent},
        "properties": {"title": [{"text": {"content": title[:100]}}]},
        "markdown": md})
    if rc == 0 and js.get("id") and js.get("object") == "page":
        return js["id"], True
    return None, False


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
        if len(md) <= CHUNK:
            pid, ok = create_page(args.parent, t, md)
            if ok:
                created += 1
            else:
                fails.append((t, "create failed / oversize"))
        else:
            # split into child pages under a split-parent
            rc, sp = mcp("API-post-page", {"parent": {"page_id": args.parent},
                "properties": {"title": [{"text": {"content": t + " (split)"}}]}})
            if rc == 0 and sp.get("id"):
                spid = sp["id"]
                parts = [md[s:s+CHUNK] for s in range(0, len(md), CHUNK)]
                ok_all = True
                for j, part in enumerate(parts, 1):
                    p2, ok2 = create_page(spid, f"{t} part {j}", part)
                    if not ok2:
                        ok_all = False
                if ok_all:
                    created += 1
                else:
                    fails.append((t, "split partial"))
            else:
                fails.append((t, "split parent failed"))
        if i % 10 == 0:
            print(f"[*] progress {i}/{len(files)} created={created}", flush=True)
        time.sleep(0.3)

    print(f"[*] DONE {args.vault}: created={created} fails={len(fails)} "
          f"embeds_uploaded={emb_up} embeds_failed={emb_fail}", flush=True)
    for t, m in fails[:10]:
        print("   -", t, m)


if __name__ == "__main__":
    main()
