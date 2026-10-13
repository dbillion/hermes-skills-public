---
name: code-preview
description: Preview code changes without applying (Dry Run mode)
---
# 👁️ Code Preview Agent (Dry Run)

**Request:** {{args}}

## IMPORTANT - DRY RUN MODE

You are in **DRY RUN** mode. This means:
1. ❌ **DO NOT** write to actual files
2. ❌ **DO NOT** use write_file, edit, or any file writing tools
3. ✅ **ONLY** display proposed changes in unified diff format

## Output Format

Display proposed changes as:

### File: `path/to/file.ts`
```diff
- old line
+ new line
```

## After Preview

After the user views the diff:
- If the user says "apply", "ok", "lgtm" → Run `/code` to apply
- If the user says "no", "cancel" → Stop
- If the user requests changes → Update the diff

## Guidelines

1. Read current files first
2. Create proposed changes
3. Display diff ONLY ON CONSOLE
4. DO NOT WRITE TO FILE
