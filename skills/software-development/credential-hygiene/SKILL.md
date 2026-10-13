---
name: credential-hygiene
description: "Keep secrets out of code and git via .env and .gitignore."
version: 1.0.0
author: Hermes Agent (captured from user correction)
license: MIT
platforms: [linux, macos, windows]
tags: [secrets, credentials, gitignore, security, .env, testing, hygiene]
related_skills: [build-discipline, requesting-code-review]
---

# Credential Hygiene (dbillion — explicit, non-negotiable mandate)

Captured from a direct user correction during tgforwarder work:
*"ensure the environment credentials are not in the codes and are not uploaded to github, use the gitignore files."*

This governs EVERY repo that touches API keys, tokens, session files, or any
secret. It is a process rule, not language-specific.

## The Rules

1. **Real secrets live ONLY in a gitignored `.env` (or the platform's secret store).**
   Never hardcode keys/tokens/hashes in source. Never pass them as literals that
   could be mistaken for real (use obviously-fake placeholders like `deadbeef…`).

2. **Commit a `.env.example`, not `.env`.** The example carries placeholder keys +
   comments documenting what's needed. The real `.env` is gitignored.

3. **`.gitignore` must cover secrets — AND must not accidentally swallow `.env.example`.**
   This is the most common mistake:
   ```
   .env
   .env.*
   *.session
   *.session-journal
   ```
   `.env.*` matches `.env.example` too, so the template would be ignored. Add an
   explicit negation AFTER the ignore rule:
   ```
   # BUT allow the committed placeholder template:
   !.env.example
   ```
   (Negations only take effect if they appear after the pattern they override.)

4. **Audit before every push/merge.** Never assume `.gitignore` is correct —
   verify with the recipe in `references/secret-audit-recipe.md`. Check: file is
   ignored, nothing secret is tracked, and no secret string exists in history.

5. **Tests must NOT write to the real secret file.** A test that prompts for or
   persists credentials must stub the persist step (e.g. `monkeypatch.setattr(
   client, "_persist_creds", lambda *a, **k: None)`). Otherwise a run of pytest
   can overwrite the real `.env` with canned test values (this actually happened:
   a `test_ensure_credentials_prompts_when_missing` test persisted
   `deadbeef…` into the repo `.env`, polluting real creds). See
   `references/secret-audit-recipe.md` for the repro + fix.

## Workflow (concrete)

1. Put real creds in `.env` (gitignored). Confirm: `git check-ignore -v .env`.
2. Create `.env.example` with placeholders; confirm it is NOT ignored:
   `git check-ignore .env.example` should print nothing (i.e. "NOT IGNORED").
3. Run the secret-audit recipe (below) before `git add` / `git push`.
4. If a test exercises credential prompting, stub the persist function.

## Pitfalls (this user's triggers — avoid)

- **`.env.*` eats `.env.example`** — always add `!.env.example` after the ignore.
- **Assuming `.gitignore` works** — verify with `git check-ignore`; a misplaced
  rule or missing negation silently uploads secrets.
- **Test pollutes real `.env`** — any code path that writes creds to disk must be
  stubbed in tests. Run the audit after adding such a test.
- **Real secret in a fixture** — even a "temporary" real hash in a test file is a
  leak risk if the file is committed. Use fake placeholders; if you must use a
  real-looking value for a repro, delete it before commit and never let it persist
  to disk.
- **Reading secret files with the file-read tool** — some environments block
  reading `.env` to prevent leakage; use the terminal (`cat`/python) when you must
  inspect, and prefer not to print values back.

## Secret-scan guard (pre-commit + CI)

A reusable scanner that blocks secrets BEFORE commit and in CI. Built and verified
this session: a staged real-looking API hash was blocked, and an actual `git commit`
with that secret was refused by the hook.

Runnable files (see skill dir):
- `scripts/secret-scan.sh` — engine. Modes: `staged` (hook) and `all` (CI). Blocks
  private-key blocks, AWS (`AKIA…`), Slack (`xoxb-…`), and BOUNDED 32-char hex
  secrets; blocks secret filenames (`.env`, `*.session`); skips `.env.example` and
  an allowlist of known non-secret fixtures. Bypass: `SECRET_SCAN_SKIP=1` or
  `git commit --no-verify`.
- `templates/githooks-pre-commit.sh` → drop into `.githooks/pre-commit` and run
  `git config core.hooksPath .githooks`.
- `.github/workflows/secret-scan.yml` → runs `secret-scan.sh all` on push/PR.
- `references/secret-scan-guard.md` → full wiring + test recipe.
- `references/secret-audit-recipe.md` → the audit commands + test-pollution repro.

The 32-hex rule is BOUNDED — `(^|[^0-9a-fA-F])[0-9a-f]{32}([^0-9a-fA-F]|$)` — so it
does NOT match substrings inside longer hex (sha256 content hashes in code). This
avoids false positives that would otherwise block normal commits.

### `git check-ignore` nuance
`git check-ignore -v <file>` prints the LAST matching pattern. If that pattern is a
`!` negation, the file is NOT ignored — the negation is shown to explain why. So a
clean `.env.example` prints `!:!.env.example`, which means "not ignored", NOT a
failure. Don't misread it as the file being swallowed.

## Verification (proof of done)

- `git check-ignore -v .env` → matches an ignore rule (file is protected).
- `git check-ignore .env.example` → no output (template will be committed).
- `git ls-files | grep -iE "\.env|\.key|\.pem|secrets"` → empty (nothing tracked).
- `git log --all -S "<real-secret>" --oneline` → empty (never committed).
- Full test suite green, with the credential-persist test stubbed.
- Secret-scan guard: clean tree passes; a staged secret is blocked; a real commit
  with a secret is refused by the hook.

See `references/secret-audit-recipe.md` for the exact commands + the test-pollution
repro/fix, and `references/secret-scan-guard.md` for the guard wiring + test recipe.
