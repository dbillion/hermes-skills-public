# ColorNote Decryption — Verified Recipe (2026-08-19)

## Confirm
```
file colornote-20260819.backup        # -> data
head -c 16 ... | xxd                  # 00 4e 00 4f 00 54 00 45  = "NOTE" UTF-16LE
```

## Decryptor
```
git clone --depth 1 https://github.com/olejorgenb/ColorNote-backup-decryptor.git
cd ColorNote-backup-decryptor
java -jar colornote-decrypt.jar 0000      < in.backup > out.raw   # V1 -> FAILED
java -jar colornote-decrypt.jar 0000 28   < in.backup > out.raw   # V2 -> OK
```
V1 failed with:
`Exception in thread "main" java.io.IOException: javax.crypto.IllegalBlockSizeException: last block incomplete in decryption`
That exception = wrong version. V2 (offset 28) succeeded; head of out.raw:
`\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\tM{"_id":5098848004,"client_uuid":...,"auth_token":"..."}`

## Note record schema (per record)
- `_id` (long), `uuid`
- `title`, `note` (body)
- `created_date`, `modified_date`, `minor_modified_date` — **epoch milliseconds**
- `color_index` (0-9), `encrypted` (0/1), `folder_id`, `tags`
- `note_type` (0 text), `type`, `status`, `active_state`, `space`
- `reminder_type`, `reminder_date`, `reminder_repeat`, `reminder_option`, `reminder_base`, `reminder_duration`, `reminder_last`, `reminder_repeat_ends`
- `account_id`, `revision`, `dirty`, `staged`, `importance`, `latitude`, `longitude`, `note_ext`

## Meta/account record (DROP — holds secrets)
Keys: `_id`, `auth_token`, `base_revision`, `client_uuid`, `fb_access`, `fb_user_name`, `repository_built`.
- `auth_token` is base64: `NTA5ODg0ODAwNDo...` (contains ColorNote user id).
- `fb_access` embeds a Google `access_token` (`ya29....`) and `refresh_token` (`1//....`).
- `fb_user_name` embeds identities incl. email (`<YOUR_EMAIL>`).

## Observed corpus (this file)
- 2,377 notes + 1 meta record.
- created range 2010-01-02 → 2026-02-13.
- Per-year counts: 2010:1, 2013:3, 2015:209, 2016:442, 2017:273, 2018:300, 2019:350, 2020:282, 2021:183, 2022:161, 2023:43, 2024:57, 2025:65, 2026:8.

## Leak check after redaction
```
grep -cE "ya29|NTA5ODg" out.redacted.md    # -> 0  (good)
grep -c "dayozoe@gmail" out.redacted.md     # -> 54 (user's own email inside own notes, not a secret)
```
