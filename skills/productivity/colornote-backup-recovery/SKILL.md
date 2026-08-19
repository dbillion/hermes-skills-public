---
name: colornote-backup-recovery
category: productivity
version: 0.1.0
author: hermes-curator
license: MIT
description: Decrypt ColorNote .backup files and export their notes.
triggers:
  - User shares a colornote-*.backup / .dat / .doc file and asks to read, analyze, or export it
  - User says recover my ColorNote notes or extract notes from this backup
  - Any encrypted ColorNote export where file reports data and the header spells NOTE in UTF-16LE
metadata:
  hermes:
    tags: [colornote, backup, recovery, android, decrypt, notes, export]
    related_skills: [notebooklm-nlm-cli, notebooklm-multi-account-rotation]
---

# ColorNote backup recovery

## When to Use
- User shares a `colornote-*.backup` / `.dat` / `.doc` file and asks to read, analyze, or export it.
- User says "recover my ColorNote notes" / "extract notes from this backup".
- Any encrypted ColorNote export where `file` reports `data` and the header spells `NOTE` (UTF-16LE).

ColorNote (Android notepad app) writes **proprietary, AES-encrypted** backups. There is no
official export. The format has at least two versions; the right invocation is found by trial.

## Format facts (verified 2026-08)
- Header is `NOTE` in UTF-16LE (`00 4e 00 4f 00 54 00 45`).
- Encrypted with `PBEWITHMD5AND128BITAES-CBC-OPENSSL`, salt `"ColorNote Fixed Salt"`, 20 iterations.
- Default master password in the app is `0000` (the backup was made with this unless the user set one).
- Decrypted payload is JSON: one "note" object per line/record, with weird binary separators
  (`\x00\x00` + 2 length bytes) between records. The first record is an ACCOUNT/META object
  containing live `auth_token`, Google `access_token`/`refresh_token`, and email — **treat as a
  secret; strip before delivering any export.**

## Recovery steps
1. Identify version by trial (do NOT guess — the error tells you):
   - `java -jar colornote-decrypt.jar 0000 < file.backup` (V1, offset 0)
   - `java -jar colornote-decrypt.jar 0000 28 < file.backup` (V2, 28-byte offset)
   - If you see `IllegalBlockSizeException: last block incomplete in decryption`, the offset is wrong — try the other. (V2 is the common one for recent app versions.)
2. The decryptor reads stdin, writes stdout. Pipe to a file: `> out.json`.
3. Clean separators (the jar's bundled `fixup-v2` is a shell script; replicate in Python instead to
   avoid shell-approval blocks — see `references/cleanup.py`):
   - Strip first 20 bytes (V2 magic), replace `\n` with a placeholder, then `re.split(b'\x00\x00..', data)`.
   - `json.loads` each surviving segment; the first with `auth_token` is the meta record.
4. **Redact** the meta record. Deliver only `note`-typed records. Replace any email inside note
   bodies with `[user-email]` before writing any file the user will keep.

## Known-good tool
Clone `https://github.com/olejorgenb/ColorNote-backup-decryptor` (Java 21 works; prebuilt
`colornote-decrypt.jar` included). No build step needed. Alternatively a Python port of the same
PBE/AES params is feasible but the jar is fastest.

## Analysis ideas once decrypted
- Notes carry `created_date`/`modified_date` (epoch ms), `title`, `note` (body), `note_type`,
  `color_index`, `folder_id`, `status`. Build a CSV/JSON (id, created, modified, year, month, title,
  body, word_count, char_count, themes, has_url, has_email) for pivot/charts.
- Theme-tag by keyword (faith/teaching, goals/plans, work/business, personal, health, music…).
- Era-split for NotebookLM upload (see `notebooklm-nlm-cli`): cap 50 sources/notebook, ~47KB/text
  source via `--text`, so split a large corpus across 2 notebooks.

## Security / safety
- The raw `.backup` contains credentials. Never paste it to a third party or print token strings.
- The user should rotate/revoke the embedded Google app access after recovery.
- A decrypted `auth_token`/`refresh_token` pair can still grant account access even past its
  `expires_at` (refresh token). Stored export MUST have tokens removed.

## References
- `references/cleanup.py` — Python snippet that strips V2 magic + separators and emits a list of
  note dicts, then writes a redacted markdown + CSV. Reuse instead of hand-typing the regex.
