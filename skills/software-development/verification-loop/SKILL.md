---
name: verification-loop
description: "Comprehensive verification system. Run after completing features, before PRs, or after refactoring. Checks build, types, lint, tests, security, and diff."
---

# Verification Loop

Comprehensive verification for code quality. Run after completing features, before PRs, or after refactoring.

## Verification Phases

### Phase 1: Build Verification
```bash
npm run build 2>&1 | tail -20
# OR
pnpm build 2>&1 | tail -20
```
If build fails, STOP and fix before continuing.

### Phase 2: Type Check
```bash
# TypeScript
npx tsc --noEmit 2>&1 | head -30

# Python
pyright . 2>&1 | head -30
```

### Phase 3: Lint Check
```bash
# JavaScript/TypeScript
npm run lint 2>&1 | head -30

# Python
ruff check . 2>&1 | head -30
```

### Phase 4: Test Suite
```bash
npm run test -- --coverage 2>&1 | tail -50
# Target: 80% minimum coverage
```

### Phase 5: Security Scan
```bash
# Check for secrets
grep -rn "sk-" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
grep -rn "api_key" --include="*.ts" --include="*.js" . 2>/dev/null | head -10

# Check for console.log in production code
grep -rn "console.log" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -10
```

### Phase 6: Diff Review
```bash
git diff --stat
git diff HEAD~1 --name-only
```

## Output Format

```
VERIFICATION REPORT
==================
Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]
Overall:   [READY/NOT READY] for PR
```
