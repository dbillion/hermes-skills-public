# Secret-scan guard — wiring + test recipe

Reusable secret hygiene for any repo that touches credentials. Built and verified in
the tgforwarder session: a staged real-looking `TELEGRAM_API_HASH` was blocked, and
an actual `git commit` carrying it was refused by the hook.

## Files
- `scripts/secret-scan.sh` — the scanner (modes: `staged`, `all`).
- `templates/githooks-pre-commit.sh` — pre-commit hook body.
- `.github/workflows/secret-scan.yml` — CI job.

## Install (per repo)
```
mkdir -p .githooks scripts .github/workflows
cp templates/githooks-pre-commit.sh .githooks/pre-commit
chmod +x .githooks/pre-commit scripts/secret-scan.sh
git config core.hooksPath .githooks
```
Add `.github/workflows/secret-scan.yml`:
```yaml
name: Secret Scan
on: [push, pull_request]
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: bash scripts/secret-scan.sh all
```

## Test recipe (prove it works)
```
# 1. clean tree passes
bash scripts/secret-scan.sh all          # -> "clean (all)", exit 0

# 2. staged secret blocks
printf 'TELEGRAM_API_HASH=2a08e3e1c377472a2dc8fc60976bc921\n' > _probe.env
git add _probe.env
bash scripts/secret-scan.sh staged        # -> "POSSIBLE SECRET DETECTED", exit 1
git reset -q _probe.env && rm -f _probe.env

# 3. REAL commit attempt is refused by the hook
echo probe > _p.txt && git add _p.txt
git commit -m "probe"                      # hook fires, commit rejected (exit 1)
git reset -q _p.txt && rm -f _p.txt
```

## Tuning
- Add a known non-secret token to the `ALLOW` var in `secret-scan.sh`.
- Bypass locally: `SECRET_SCAN_SKIP=1` or `git commit --no-verify` (CI still catches it).
- The 32-hex pattern is bounded so sha256 content hashes in code don't false-positive.
