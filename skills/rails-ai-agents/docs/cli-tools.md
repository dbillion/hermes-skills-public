# CLI Tools for Claude Code

Tools that improve how Claude Code searches, navigates, diffs, and audits code. Each entry covers what the tool does, why it matters in an AI-assisted workflow, and how to install and configure it.

---

## ripgrep (`rg`)

### What it does
A search tool that recursively greps file contents. Faster than `grep` and `git grep`, written in Rust, with native `.gitignore` support and smart encoding detection.

### Benefits for Claude Code
Claude Code's built-in `Grep` tool already uses `rg` internally. The gain is in shell commands: every time I write a `grep` invocation in a bash command, having `rg` on PATH means I naturally reach for it — `.gitignore`-aware by default, no need to pass exclusion flags for `node_modules`, build artifacts, etc. On a large repo, this is 10–100× faster than `grep -r` and produces less noise.

### Install
```bash
# macOS
brew install ripgrep

# Verify
rg --version
```

### Configuration
`~/.ripgreprc` — set as the default config file via `RIPGREP_CONFIG_PATH`:

```bash
# ~/.ripgreprc
--smart-case          # case-insensitive unless pattern has uppercase
--max-columns=150     # truncate very long lines
--max-columns-preview # show a preview when truncating
--hidden              # search hidden files (but still respect .gitignore)
```

Add to shell profile:
```bash
export RIPGREP_CONFIG_PATH="$HOME/.ripgreprc"
```

---

## fd

### What it does
A modern replacement for `find`. Simpler syntax, faster execution, `.gitignore`-aware by default, with colorized output and sensible defaults.

### Benefits for Claude Code
`find` has notoriously verbose syntax (`find . -name "*.ts" -not -path "*/node_modules/*"`). When I write file-discovery shell commands, `fd` cuts that to `fd -e ts`. Shorter commands mean fewer syntax errors, less token waste, and outputs that are easier for me to parse. Also skips `node_modules`, `.git`, and build dirs automatically — no flags needed.

### Install
```bash
# macOS
brew install fd

# Verify
fd --version
```

### Configuration
`fd` has no config file. Key flags to know:

```bash
fd -e ts                    # find all .ts files
fd -t f -e md kb/           # files only, .md, under kb/
fd --hidden --no-ignore .   # include hidden + ignored files
fd -x wc -l                 # run command on each result (like find -exec)
```

For use in Claude Code sessions, I combine it with ripgrep:
```bash
fd -e ts | xargs rg "useEffect"   # search only in TypeScript files
```

---

## git-delta

### What it does
A syntax-highlighted pager for `git diff`, `git show`, `git log -p`, and `git blame`. Adds line numbers, section headers, side-by-side view, and theme support.

### Benefits for Claude Code
When I run `git diff` in a shell command, the output lands directly in my context as raw text. Delta's default human-optimized config adds ANSI color codes and decorative elements that pollute that text. Configured for LLM consumption — line numbers on, colors off, no side-by-side — delta makes diffs significantly more navigable: section headers identify which function changed, line numbers let me reference `file.ts:42` precisely without re-reading the whole file.

### Install
```bash
# macOS
brew install git-delta

# Verify
delta --version
```

### Configuration
Add to `~/.gitconfig`. The default config is for terminal humans; this config is for LLM-parseable output:

```ini
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true           # n/N to jump between diff sections
    line-numbers = true       # critical: gives me file:line references
    side-by-side = false      # single column — cleaner for text parsing
    syntax-theme = none       # no ANSI color codes in captured output
    file-style = bold         # minimal file header decoration
    hunk-header-style = line-number syntax
    paging = never            # stream directly, don't buffer

[merge]
    conflictstyle = diff3

[diff]
    colorMoved = default
```

To verify the output is clean for LLM context, run:
```bash
git diff HEAD~1 | cat   # 'cat' bypasses the pager — should show plain numbered text
```

---

## semgrep

### What it does
A static analysis tool that runs pattern-matching rules against source code. Rules look like the code they match — no complex AST knowledge required. Covers security vulnerabilities, bug patterns, and code quality checks across 30+ languages.

### Benefits for Claude Code
This is the highest-leverage tool on this list. The difference:

- Without semgrep: "this looks like it might be vulnerable to SQL injection" (probabilistic)
- With semgrep: `python.django.security.injection.sql` flagged `line 42` (deterministic)

Semgrep has an [official MCP server](https://github.com/semgrep/mcp) that lets me run scans directly within a session and iterate on code until scans are clean — closing the feedback loop. Rule-based checks find different vulnerability classes than AI heuristics; combining both produces significantly better coverage.

### Install
```bash
# macOS (via Homebrew)
brew install semgrep

# Or via pip
pip install semgrep

# Verify
semgrep --version
```

### Semgrep MCP Server (Claude Code integration)

Install the MCP server so I can trigger scans directly:

```bash
# Install the semgrep MCP package
npm install -g @semgrep/mcp
# or check https://github.com/semgrep/mcp for the current install method
```

Add to `~/.claude/settings.json`:
```json
{
  "mcpServers": {
    "semgrep": {
      "command": "semgrep-mcp",
      "args": []
    }
  }
}
```

### Manual usage (without MCP)
```bash
# Run default security rules on current directory
semgrep --config=auto .

# Run a specific ruleset
semgrep --config=p/javascript .
semgrep --config=p/python .
semgrep --config=p/secrets .

# Run on a single file, JSON output for scripting
semgrep --config=auto --json src/auth.ts

# CI mode (non-zero exit on findings)
semgrep --config=auto --error .
```

### Key rulesets
| Ruleset | Purpose |
|---------|---------|
| `p/default` | General best practices |
| `p/secrets` | Hardcoded credentials, tokens |
| `p/javascript` | JS/TS security patterns |
| `p/python` | Python security patterns |
| `p/owasp-top-ten` | OWASP Top 10 vulnerabilities |
| `p/sql-injection` | SQL injection patterns |
| `p/xss` | Cross-site scripting |

---

## Quick reference

| Tool | Replaces | Key flag to know |
|------|----------|-----------------|
| `rg` | `grep -r` | `--smart-case` |
| `fd` | `find` | `-e <ext>` for extension filter |
| `delta` | raw `git diff` | configured via `~/.gitconfig` |
| `semgrep` | manual review | `--config=auto` for sensible defaults |
