---
name: git-secret-purge
description: Prevent, detect, and remediate secrets committed to git history. Covers externalizing credentials (never hardcode), GitHub push-protection (GH013) remediation via history rewrite, the critical pitfall of destroying the recovery ref before push succeeds, and the git-bundle escape hatch when pushes stall.
license: MIT
---

# Git Secret Purge

Use this skill whenever a credential, API key, or token has been (or might be)
committed to a git repo, or when wiring secrets into an app. The guiding rule
from hard experience: **a committed secret is a live incident — rotate it AND
purge it, in that order.**

## Rule 0 — Never hardcode secrets

- A *publishable* key (e.g. `pk_test_...`, `NEXT_PUBLIC_*`) is client-safe but
  still must not be typed literally into a committed source file. Keep it in a
  gitignored env file and inject at build time.
- A *secret* key (`sk_...`, `CLERK_SECRET_KEY`, `DATABASE_URL`, any `AIza...`/
  `AQ.Ab...` GCP key) lives ONLY in gitignored `.env` (server side) or
  `.env.local`. Never in `environment.ts`, config constants, or scripts.
- Angular cannot natively read `.env.local` at build time. Pattern that works:
  1. `clerk env pull` (or manual) writes `CLERK_PUBLISHABLE_KEY` to gitignored
     `.env.local`.
  2. A `prebuild` npm script (`node scripts/inject-clerk-key.mjs`) reads it and
     writes `src/environments/environment.ts`.
  3. **Gitignore `src/environments/environment.ts`** (repo-root-relative path,
     e.g. `src/environments/environment.ts` from the app dir — a leading `/`
     anchors to the gitignore's own dir, so `/environments/...` is WRONG if the
     file is under `src/`). Verify with `git check-ignore <path>` and
     `git add -A --dry-run | grep <path>` (must show NOT added).
- Verify before commit: `git grep -l "pk_test\|AIza\|sk_\|DATABASE_URL=" HEAD`
  must return nothing.

## Preventive — pre-commit + CI secret scanner (stop the leak before it happens)
Detection/rewrite (above) is remediation. Prefer PREVENTION: a portable POSIX
`git grep` scanner wired as a pre-commit hook AND a GitHub Action, so a secret is
blocked at commit time and again in CI (catches `--no-verify` bypasses).

**`.gitignore` GOTCHA — `.env.*` silently swallows `.env.example`:**
If you write `.env` and `.env.*` to ignore real secrets, the glob ALSO matches
`.env.example` (the committed placeholder template), so it gets ignored too. Fix
with an explicit negation placed AFTER the ignore rule:
```gitignore
.env
.env.*
# BUT allow the committed placeholder template:
!.env.example
*.session
```
Verify: `git check-ignore .env.example` must report NOT ignored; `.env` MUST be
ignored. Add `.env.example` with placeholder keys only (never real values).

**Scanner engine (`scripts/secret-scan.sh`)** — modes `staged` (hook) / `all` (CI).
Blocks: private-key blocks, AWS (`AKIA[0-9A-Z]{16}`), Slack (`xox[baprs]-…`),
32-char hex secrets (bounded so it won't false-positive on sha256 content hashes),
and secret-bearing filenames (`.env`, `.env.*`, `*.session`) even on `git add -f`.
Skip `.env.example` and an allowlist of known non-secret fixtures (e.g.
`deadbeefdeadbeefdeadbeefdeadbeef`, `YOUR_*_HERE`). Bypass: `SECRET_SCAN_SKIP=1`
or `git commit --no-verify` (CI still catches it). Pattern:
```sh
MODE="${1:-staged}"
FILES=$(git diff --cached --name-only --diff-filter=ACM)   # staged mode
GIT_GREP_TARGET="--cached"
MATCHES=$(git grep -nE -e "$PATTERNS" $GIT_GREP_TARGET -- $FILES 2>/dev/null | grep -vE "$ALLOW")
[ -n "$MATCHES" ] && { echo "POSSIBLE SECRET:"; echo "$MATCHES"; exit 1; }
```
**Activate the hook** without copying into every clone:
```bash
git config core.hooksPath .githooks
# .githooks/pre-commit -> exec sh "$ROOT/scripts/secret-scan.sh" staged
```
**CI (`.github/workflows/secret-scan.yml`):** on push + pull_request, run
`bash scripts/secret-scan.sh all`. This is the real safety net — it runs even if
a developer uses `--no-verify`.

**VERIFY the guard actually works** before trusting it:
```bash
bash scripts/secret-scan.sh all                 # clean tree -> exit 0
printf 'TELEGRAM_API_HASH=2a08e3e1c377472a2dc8fc60976bc921\n' > _p.env && git add _p.env
bash scripts/secret-scan.sh staged; echo $?      # must be non-zero (blocked)
git reset -q _p.env && rm -f _p.env
```

## Detecting a blocked push (GitHub GH013)

When `git push` is rejected with:
```
remote: error: GH013: Repository rule violations found for refs/heads/master.
remote: - GITHUB PUSH PROTECTION
remote:   - Push cannot contain secrets
remote:     - GCP API Key Bound to a Service Account
remote:       locations:
remote:         - commit: <sha>
remote:           path: stitch.js:3
```
The secret is in history at `<sha>` (and possibly later commits). Push
protection scans the FULL commit graph, so fixing only the working tree is not
enough — you must rewrite history.

Find every commit carrying the key:
```bash
git log --all --oneline -S "<unique-key-substring>"
```
Locate the exact files/lines (mask output, never echo the full key):
```bash
grep -n "AIza\|AQ.Ab" stitch.js | sed -E 's/(AQ.Ab[0-9A-Za-z_-]{0,6})[0-9A-Za-z_-]*/\1****/'
```

## Remediating (rewrite history)

Prefer `git filter-repo` (install: `pip install git-filter-repo`). If
unavailable, `git filter-branch --index-filter` works:
```bash
# remove the leaky files from ALL history (they are scratch helpers, not app code)
git filter-branch --force \
  --index-filter 'git rm --cached --ignore-unmatch leaky.js other.js' \
  --prune-empty -- --all
```
This rewrites `master`, all branches, and remote-tracking refs. Verify the key
is gone from every LIVE ref (NOT just `--all`, which includes the backup):
```bash
git log master -S "<key>" --oneline      # must be empty
git log tailwind-spartan -S "<key>" --oneline   # must be empty
git rev-list --all | while read c; do git grep -q "<key>" "$c" && echo "FOUND $c"; done
```

## CRITICAL PITFALL — do NOT destroy the recovery ref early

`filter-branch` writes a backup to `refs/original/*`. **LEAVE IT until the push
succeeds.** Never run this before confirming the push landed:

> User correction (verbatim, 2026): *"if you reflog, you remove all 10 hours
> of work, you cant be that stupid."* — running `git reflog expire --all` +
> `git gc --prune=now` after a history rewrite but before the push is verified
> destroys the only recovery point. The rewritten work still exists on the
> branch tips; what you lose is the UNDO button, not the code — but that is
> exactly what you need if the push then fails.
```bash
git reflog expire --expire=now --all   # ❌ DESTROYS undo trail + 10h of work
git gc --prune=now                     # ❌ prunes the old commits permanently
```
Those two commands permanently delete the pre-rewrite history. If the push then
fails for any reason, the work is unrecoverable. Remove the backup ONLY after
`git push` returns success:
```bash
# AFTER a verified successful push:
git for-each-ref --format="%(refname)" refs/original/ | while read r; do git update-ref -d "$r"; done
git reflog expire --expire=now --all
git gc --prune=now
```

## Escape hatch — git bundle when push stalls

If `git push` hangs at the pack-upload stage (SSH `git-receive-pack` stalls
while `ls-remote` and `ssh -T` work; `GIT_TRACE=1` shows it stops right after
`git pack-objects ... --stdout`), the host network is blocking outbound push
data. Read operations work; writes stall. Do NOT keep retrying blindly.

Create a self-contained bundle (no network needed) and transfer it to a machine
with working egress:
```bash
git bundle create /path/to/repo.bundle master tailwind-spartan
git bundle verify /path/to/repo.bundle     # confirms complete history
```
On the egress machine:
```bash
git clone /path/to/repo.bundle ks-push
cd ks-push
git push --force-with-lease origin master
git push -u origin tailwind-spartan
```
Note: `--force-with-lease` may report "stale info" if local remote-tracking
refs are out of date — run `git fetch origin` first to refresh them.

## Also: rotate the key

A purged secret is still compromised if it was ever pushed or visible. Rotate/
revoke it at the provider (GCP, Clerk, OpenAI, Neon) regardless of the purge.
Purging history is cleanup; rotation is the real fix.

## See also
- `hermes-config-safe-edit` — safe edits to Hermes config without yaml round-trip.
- Project memory: "Agent LLM keys ... Copy into sub-project gitignored .env as
  OPENAI_API_KEY=<key> + OPENAI_BASE_URL=... Never hardcode/echo secrets."
