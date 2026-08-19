---
name: git-history-safety
description: >-
  Safe git history operations when purging secrets or rewriting history. Encodes two hard rules:
  (1) NEVER run `git reflog expire --expire=now --all` + `git gc --prune=now` (or any reflog/gc that
  destroys the undo trail) without explicit user confirmation — it permanently deletes the pre-rewrite
  backup and all local undo history; (2) when `git push` stalls/hangs at pack upload (network egress
  blocked) while `git ls-remote`/`ssh -T` still work, use `git bundle` to move the repo across the
  backends) when purging secrets or rewriting history. Encodes three hard rules — (3) the newest:
  ALWAYS verify a push is conflict-free BEFORE pushing; a user correction fired on exactly this
  ("did you check the commit that it doesnt conflict before pushing it"). Use before any
  filter-branch/filter-repo, reflog expire, gc, push, or when a push hangs.
user-invocable: false
allowed-tools:
  - Bash(git filter-branch *)
  - Bash(git filter-repo *)
  - Bash(git bundle *)
  - Bash(git fetch *)
  - Bash(git push *)
---

# Git history safety

## Rule 1 — reflog / gc are destructive, confirm first
`git reflog expire --expire=now --all` + `git gc --prune=now` permanently deletes:
- The reflog (local undo trail — `HEAD@{1}` recovery).
- Any dangling objects from old commits (including the pre-rewrite state that `filter-branch`
  saved under `refs/original/`).

After a history rewrite (filter-branch / filter-repo) to purge a secret, the `refs/original/*`
backup IS the user's undo button. Do NOT expire/gc until the user has confirmed the push succeeded
and explicitly wants the backup gone. A user correction fired on exactly this: "if you reflog, you
remove all 10 hours of work." The committed work is safe (rewritten branches still exist); only the
safety net is destroyed — but that net is what lets the user say "revert this."

Safe purge sequence (only AFTER push confirmed, user OK):
```bash
git for-each-ref --format='%(refname)' refs/original/ | while read r; do git update-ref -d "$r"; done
git reflog expire --expire=now --all
git gc --prune=now
```

## Rule 2 — push hangs at pack upload → use git bundle
Symptom: `git ls-remote origin` and `ssh -T git@github.com` return instantly (auth/read OK), but
`git push` hangs at the pack-upload phase (both SSH and HTTPS, old repo and new repo). This is a
network egress block on `git-receive-pack`, NOT a GitHub rule (push protection would fail FAST with
"blocked", not hang).

Fix: don't retry the push. Create a self-contained bundle and move it across the egress boundary:
```bash
git bundle create /tmp/repo.bundle master tailwind-spartan   # or --all
# transfer /tmp/repo.bundle to a machine with working egress, then:
git clone /tmp/repo.bundle ks-push && cd ks-push
git remote set-url origin git@github.com:user/repo.git
git push -u origin master tailwind-spartan
```
A successful `git bundle verify` confirms the bundle is complete.

## Secret purge via filter-branch (history rewrite)
```bash
git filter-branch --index-filter \
  'git rm --cached --ignore-unmatch path/to/leaky-file.js' \
  --prune-empty -- --all
# then verify the secret is gone from all reachable commits:
git rev-list --all | xargs -I{} git grep -l "SECRET" {} 2>/dev/null   # expect empty
# backup refs/original/ still hold the key until explicitly deleted (see Rule 1).
```
Prefer `git filter-repo` (pip install) when available; it's faster and cleaner than filter-branch.

## Rule 3 — verify a push is conflict-free BEFORE pushing
A user correction fired on exactly this: "did you check the commit that it doesnt conflict before
pushing it." Never push blind. The remote default branch is often NOT `main` (e.g. `master`), so
check the real tracking ref first — using `main` when the branch is `master` makes every
divergence command error with "unknown revision".

Check sequence (run BEFORE `git push`):
```bash
git fetch origin
# discover the real default branch — do NOT assume main
git symbolic-ref refs/remotes/origin/HEAD        # e.g. -> origin/master
BR=$(git rev-parse --abbrev-ref --symbolic-full-name @{u})   # local tracking, e.g. master
# divergence: left=commits only local, right=commits only remote
git rev-list --left-right --count $BR...origin/$BR
# fast-forward check: if remote is an ancestor of local, push is clean
git merge-base --is-ancestor origin/$BR $BR && echo "FAST-FORWARD (no conflict)" || echo "NEEDS MERGE (conflict risk)"
# also confirm the specific file(s) you touched did not change on remote since your base:
git diff --stat $(git merge-base $BR origin/$BR) origin/$BR -- <file-you-edited>
```
If `git merge-base --is-ancestor` is true (and your edited files are unchanged on remote), the
push will fast-forward and cannot conflict. Only then push. If false, pull/rebase first and
re-resolve, then re-check. This is a read-only gate — it never mutates history.
