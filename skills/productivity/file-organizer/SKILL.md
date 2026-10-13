---
name: file-organizer
description: "Intelligently organizes files and folders by understanding context, finding duplicates, and suggesting better organizational structures. Use when user wants to clean up directories, organize downloads, remove duplicates, or restructure projects."
---

# File Organizer

Analyzes, categorizes, and organizes cluttered file systems to establish logical folder structures and reclaim disk space.

## When to Use

- Downloads folder is chaotic
- Files are scattered and hard to find
- Duplicate files consume disk space
- Folder structure no longer makes sense
- Starting a new project needing structure
- Preparing to archive old projects

## Workflow

### 1. Understand the Scope

Ask clarifying questions:
- Which directory needs organization?
- What's the main problem?
- Any files/folders to avoid?
- Conservative vs. comprehensive cleanup?

### 2. Analyze Current State

```bash
# Overview of structure
ls -la [target_directory]

# Check file types and sizes
find [target_directory] -type f -exec file {} \; | head -20

# Identify largest files
du -sh [target_directory]/* | sort -rh | head -20

# Count file types
find [target_directory] -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
```

Summarize: total files/folders, type breakdown, size distribution, date ranges, and obvious issues.

### 3. Find Duplicates

```bash
# Exact duplicates by hash (macOS)
find [directory] -type f -exec md5 {} \; | sort | uniq -d

# Exact duplicates by hash (Linux)
find [directory] -type f -exec md5sum {} \; | sort | uniq -w32 -d

# Files with same name
find [directory] -type f -printf '%f\n' | sort | uniq -d

# Large duplicates (fdupes)
fdupes -r [directory]
```

> **CRITICAL**: Always ask for confirmation before deleting any files.

### 4. Propose Organization Plan

Present a clear plan before making changes:

```markdown
# Organization Plan for [Directory]

## Current State
- X files across Y folders
- [Size] total
- File types: [breakdown]
- Issues: [list problems]

## Proposed Structure
[Directory]/
├── Documents/
│   ├── Work/
│   └── Personal/
├── Media/
│   ├── Photos/
│   ├── Videos/
│   └── Audio/
├── Archives/
└── Temp/

## Changes
1. Create: [list folders]
2. Move: [specific moves]
3. Delete: [duplicates - with confirmation]

Ready to proceed?
```

### 5. Execute Organization

```bash
# Create structure
mkdir -p "path/to/new/folders"

# Move with logging (preserve dates)
rsync -av --remove-source-files "src/" "dest/"

# Safe delete (move to trash on macOS)
# Use trash CLI if available, otherwise:
mv "file" ~/.Trash/
```

### 6. Summary

Report what changed:
- Folders created
- Files moved
- Disk space freed
- Duplicates removed

## Organization Patterns

**By Type:**
- Documents: PDF, DOCX, TXT, MD
- Images: JPG, PNG, SVG, GIF, WEBP
- Videos: MP4, MOV, AVI, MKV
- Archives: ZIP, TAR, GZ, DMG, DEB
- Code: directories with .git, package.json, etc.
- Spreadsheets: XLSX, CSV, ODS
- Presentations: PPTX, KEY

**By Purpose:**
- Work vs. Personal
- Active vs. Archive
- Project-specific vs. Reference

**By Date:**
- Current year/month
- Previous years
- Very old (archive candidates)

## Maintenance Tips

1. **Weekly**: Sort new downloads
2. **Monthly**: Review and archive completed projects
3. **Quarterly**: Check for new duplicates
4. **Yearly**: Archive old files
