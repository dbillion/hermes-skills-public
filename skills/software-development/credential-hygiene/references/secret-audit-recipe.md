# Secret-Audit Recipe (run before every push / merge)

Paste-and-run. Substitute `<REAL_SECRET>` with the actual secret string to check
(never echo it back in chat output — these commands print only booleans/paths).

```bash
cd <repo>

# 1. Is the real .env ignored? (expect a matched rule, e.g. ".gitignore:12:.env")
git check-ignore -v .env

# 2. Is .env.example NOT ignored? (expect NO output = good; output = still ignored = BAD)
git check-ignore .env.example || echo "OK: .env.example will be committed"

# 3. Nothing secret tracked? (expect empty)
git ls-files | grep -iE "\.env|\.key|\.pem|secrets|credentials" || echo "none tracked"

# 4. Real secret in ANY commit in history? (expect empty = never committed)
git log --all -S "<REAL_SECRET>" --oneline || echo "clean history"

# 5. What would `git add -A` stage? confirm .env / *.session are absent
git add -A --dry-run 2>/dev/null | grep -iE "\.env|session" || echo "no secrets staged"

# 6. Real secret in any TRACKED file right now? (expect "CLEAN")
git grep -c "<REAL_SECRET>" && echo "FOUND (BAD)" || echo "CLEAN"
```

## The `.env.*` negation gotcha

A `.gitignore` like this:
```
.env
.env.*
```
will ALSO ignore `.env.example` (because `.env.*` matches `.example`). The fix —
add the negation AFTER the ignore line:
```
.env
.env.*
# allow the committed placeholder template:
!.env.example
```
Verify with step 2. Negations only win if they appear after the pattern they
override.

## Test-pollution trap (real, bitten us once)

A credential-prompting function may persist the entered value to disk, e.g.
`ensure_credentials()` calling `_persist_creds()` which writes to the repo
`.env`. If a test feeds canned creds to the prompt and does NOT stub that persist
call, running pytest **overwrites the real `.env`** with fake values.

Symptom we hit: `ApiIdInvalidError` on `tgf login` because the test had replaced
the real `TELEGRAM_API_HASH` with `deadbeefdeadbeefdeadbeefdeadbeef`. The creds
were gitignored so they couldn't be recovered from git.

Fix in the test:
```python
# Guard: never let the test persist its canned creds to the REAL repo .env.
monkeypatch.setattr(cl, "_persist_creds", lambda *a, **k: None)
answers = iter(["28150103", "deadbeefdeadbeefdeadbeefdeadbeef"])
with mock.patch.object(click, "prompt", side_effect=lambda *a, **k: next(answers)):
    cl.ensure_credentials()
```
Verify the guard with:
```bash
cp .env /tmp/env_before
pytest tests/test_client.py -q
diff /tmp/env_before .env && echo "NO CHANGE — test no longer writes to .env"
```

Also: a `_persist_creds` that writes obviously-placeholder values (`deadbeef…`)
should refuse outright, as a second line of defense.
