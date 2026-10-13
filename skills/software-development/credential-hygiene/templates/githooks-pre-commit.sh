#!/bin/sh
# Pre-commit hook: scan staged changes for secrets before they are committed.
# Install: copy to .githooks/pre-commit and run `git config core.hooksPath .githooks`.
# Bypass for this commit only: git commit --no-verify
ROOT=$(git rev-parse --show-toplevel)
exec sh "$ROOT/scripts/secret-scan.sh" staged
