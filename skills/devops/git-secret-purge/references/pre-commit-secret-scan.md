# Pre-commit + CI secret scanner (prevention, not remediation)

Stop secrets at commit time and again in CI. Portable POSIX `git grep` based — no
Python/test deps required.

## .gitignore (note the negation so .env.example still commits)
```gitignore
.env
.env.*
# BUT allow the committed placeholder template:
!.env.example
*.session
*.session-journal
```
Verify: `git check-ignore .env` (ignored) and `git check-ignore .env.example`
(NOT ignored). Add `.env.example` with placeholder keys only.

## scripts/secret-scan.sh
```sh
#!/bin/sh
# modes: staged (hook) | all (CI). Bypass: SECRET_SCAN_SKIP=1
set -eu
MODE="${1:-staged}"
[ "${SECRET_SCAN_SKIP:-0}" = "1" ] && { echo "skipped"; exit 0; }
ALLOW='deadbeefdeadbeefdeadbeefdeadbeef|YOUR_API_HASH_HERE|YOUR_API_ID_HERE'
PATTERNS='-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|xox[baprs]-[0-9A-Za-z-]{10,}|(^|[^0-9a-fA-F])[0-9a-f]{32}([^0-9a-fA-F]|$)'
if [ "$MODE" = "staged" ]; then
  FILES=$(git diff --cached --name-only --diff-filter=ACM); GIT_GREP_TARGET="--cached"
else
  FILES=$(git ls-files); GIT_GREP_TARGET="HEAD"
fi
[ -z "$FILES" ] && { echo "clean ($MODE)"; exit 0; }
# block secret filenames
for f in $FILES; do
  case "$f" in
    .env|.env.*|*.session|*.session-journal)
      [ "$f" = ".env.example" ] && continue
      echo "BLOCKED filename: $f"; exit 1;;
  esac
done
SCAN=""; for f in $FILES; do case "$f" in *.env.example) ;; *) SCAN="$SCAN $f";; esac; done
[ -z "$SCAN" ] && { echo "clean ($MODE)"; exit 0; }
MATCHES=$(git grep -nE -e "$PATTERNS" $GIT_GREP_TARGET -- $SCAN 2>/dev/null | grep -vE "$ALLOW" || true)
if [ -n "$MATCHES" ]; then
  echo "POSSIBLE SECRET DETECTED ($MODE):"; echo "$MATCHES"
  echo "Bypass: git commit --no-verify  (or SECRET_SCAN_SKIP=1)"; exit 1
fi
echo "clean ($MODE)"; exit 0
```

## .githooks/pre-commit
```sh
#!/bin/sh
ROOT=$(git rev-parse --show-toplevel)
exec sh "$ROOT/scripts/secret-scan.sh" staged
```
Activate (no per-clone copy): `git config core.hooksPath .githooks`

## .github/workflows/secret-scan.yml
```yaml
name: Secret Scan
on: { push: null, pull_request: null }
on:
  push:
  pull_request:
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: bash scripts/secret-scan.sh all
```

## Verify the guard works (before trusting it)
```bash
bash scripts/secret-scan.sh all                       # clean -> exit 0
printf 'TELEGRAM_API_HASH=2a08e3e1c377472a2dc8fc60976bc921\n' > _p.env
git add _p.env
bash scripts/secret-scan.sh staged; echo $?           # non-zero = blocked (good)
git reset -q _p.env && rm -f _p.env
```

## Pitfalls
- The 32-hex rule is BOUNDED (surrounding char classes) so it won't fire on
  substrings of longer hex (sha256 content hashes in code).
- CI mode is the real net — it catches `git commit --no-verify` bypasses.
- Keep the ALLOW list minimal; add only unambiguous non-secret fixtures.
