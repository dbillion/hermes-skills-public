---
name: colornote-backup-decrypt
description: Recover notes from a ColorNote backup file.
version: 1
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [data-recovery, mobile-backup, colornote, decryption, android]
    related_skills: []
---

# ColorNote Backup Decryptor

## Overview
ColorNote (Android notepad app) exports **device backups** that are proprietary AND encrypted with an undocumented scheme. The app has no real export. A backup is a single binary blob: a `NOTE` magic header, then AES-encrypted payload. The first decrypted JSON record is an **account/meta record that contains LIVE credential tokens** (Google access + refresh tokens, a Facebook token, the user's email). Every other record is one note. Recovering the notes is a 2-step job: (1) AES-decrypt the blob, (2) split the decrypted stream into JSON objects and redact secrets.

ColorNote-backup-decryptor (olejorgenb, MIT) does the AES step. There are **two format versions**; you must trial them.

## When to use
- User hands you a `.backup` / `.dat` / `.doc` file that is "ColorNote" data.
- `file` reports `data` and the first bytes are `00 4e 00 4f 00 54 00 45` ("NOTE" in UTF-16LE).
- User says "recover my notes", "read my backup", "analyze my plans/notes from ColorNote".

## Prereqs
- `java` (OpenJDK 21 works; the decryptor uses BouncyCastle, bundled in the jar).
- `git`, `python3`.
- No network needed beyond cloning the decryptor repo once.

## Step 1 — Confirm it's ColorNote
```
file <file>
head -c 16 <file> | xxd        # expect "NOTE" UTF-16LE => 00 4e 00 4f 00 54 00 45
```

## Step 2 — Get the decryptor
```
git clone --depth 1 https://github.com/olejorgenb/ColorNote-backup-decryptor.git
cd ColorNote-backup-decryptor
# jar + lib/ (bcprov, bcpkix) are present
```

## Step 3 — Decrypt (trial V1 then V2)
The decryptor reads stdin, writes stdout. Password default is `0000`; offset is 0 (V1) or 28 (V2).
```
# V1
java -jar colornote-decrypt.jar 0000      < in.backup > out.raw
# V2  (if V1 fails)
java -jar colornote-decrypt.jar 0000 28   < in.backup > out.raw
```
**Version signal:** if you get `javax.crypto.IllegalBlockSizeException: last block incomplete in decryption`, that version is WRONG — switch to the other. In practice V2 (offset 28) is the common one for recent backups. A successful run produces a ~same-size file whose head reads `\x00\x00\x00\x01...{"_id":...` (binary prefix + JSON).

## Step 4 — Clean the decrypted stream into notes
The decrypted `out.raw` is NOT clean JSON. It has a ~20-byte binary header and records separated by `\x00\x00` + 2 bytes. The repo's `fixup-v2` shell helper (`tail -c +21 | tr '\n' X | perl -p -e 's/\0\0../\n/g'`) does this, but it shelled out and can hit an approval/timeout block in some harnesses. ****Just run `scripts/parse_colornote.py <out.raw> [out.md]`** — it is deterministic, needs no perl, splits records, drops the meta/token record, redacts any Google tokens leaked into note bodies, and emits the redacted Markdown + per-year counts. Re-type the recipe below only if you need to tweak it.

Split recipe (Python):
```python
import json, re
raw = open('out.raw','rb').read()
data = raw.replace(b'\n', b'X')          # newlines only appear inside binary separators
parts = re.split(b'\x00\x00..', data)     # split on NUL NUL + 2 bytes
notes = []
for p in parts:
    p = p.strip()
    if not p: continue
    try: notes.append(json.loads(p.decode('utf-8','replace')))
    except Exception: pass
```
Records with a `title` key are notes; the record with `auth_token` is the meta/account record. Note fields: `created_date`/`modified_date` are **epoch milliseconds**; `note` is the body, `title` the subject, `color_index` the color, `encrypted` 0/1, `folder_id`, `tags`, `reminder_*`.

## Step 5 — REDACT CREDENTIALS (MANDATORY)
The meta record and sometimes note bodies embed secrets. **Strip before delivering or saving anything:**
- `auth_token` (base64), `fb_access`, `fb_user_name` from the meta record — drop the whole meta record.
- Google `access_token` / `refresh_token` strings (look like `ya29....` and long `1//...` tokens) if they appear in any note body.
- The user's email if it appears only as an account identifier (it's fine if the user wrote it in their own notes, e.g. a CV — that's not a secret).
Verify with `grep -cE "ya29|NTA5ODg" out_redacted.md` → must be 0.
Recommend the user **revoke that Google app's access and delete the raw `.backup`**, since the refresh token may still grant account access.

## Step 6 — Analyze / export
- Sort by `created_date` for a timeline; `datetime.fromtimestamp(int(ms)/1000)`.
- Theme-tag by keyword (faith/teaching, business, goals, personal, health, people, music) — notes often match several.
- Export as one redacted Markdown file (per-year headings) so the user owns the content. Deliver via MEDIA path.

## Pitfalls
- **Wrong version silently errors** with `IllegalBlockSizeException` — that is the version signal, not a corrupt file. Try the other offset.
- **Never deliver the raw decrypted file** — it contains live tokens. Always redact (Step 5) and verify.
- **Don't trust `strings`** on the encrypted blob — payload is ciphertext; only the decrypted stream is readable.
- **The shell `sh fixup-v2` can be blocked** by command-approval timeouts; use the Python parser instead.
- Note bodies have escaped newlines; replace `\r` and collapse when rendering.

## Verification
- `len(notes)` > 0 and the first parsed object has `title`.
- `grep -cE "ya29|NTA5ODg" <export>` == 0 (no leaked tokens).
- Date range sane (ColorNote notes span many years).

## References
- `references/decryption-recipe.md` — exact command transcript and per-field schema notes.
- `scripts/parse_colornote.py` — end-to-end: read `out.raw`, split, redact, emit redacted Markdown + per-year counts.
