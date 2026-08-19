# Secret-Redaction Pitfalls (learned the hard way)

When templating `~/.hermes/config.yaml` for a commit-safe backup, the goal is to
replace every live secret value with `${ENV:VAR}` and write NOTHING confidential.

## Pitfall: multi-line secret leak inside `env:` blocks

Hermes MCP server definitions embed credentials in an `env:` block. Some (e.g.
Substack) store a full session cookie as a **multi-line scalar**:

```yaml
mcp_servers:
  substack-api:
    command: npx
    args: [-y, substack-mcp@latest]
    env:
      SUBSTACK_PUBLICATION_URL: https://dbillion.substack.com/
      SUBSTACK_SESSION_TOKEN: substack.sid=s%3AMZtn...;
        cf_clearance=wUMlMpnk...;          # <-- continuation, NO colon
        __cf_bm=2V1ejrudc...;
        AWSALBTG=GM++qkO...;               # <-- leaked if not handled
        substack.lli=eyJhbG...;            # <-- JWT leaked
      SUBSTACK_USER_ID: '36196425'
```

The continuation lines (`cf_clearance=`, `AWSALBTG=`, `eyJ…`) have **no `key:`
colon**, so a per-line regex `^(\s*)key:\s*value$` does NOT match them. They
fall through to the bottom `cfg_lines.append(line)` and get written **verbatim** —
leaking session cookies + JWTs into the committed template.

### Symptom
`grep -c 'cf_clearance\|AWSALBTG\|substack.sid\|eyJhbG' config.yaml.template`
returns a non-zero number even though the `SUBSTACK_SESSION_TOKEN:` line itself
was masked.

### Fix
Intercept env-block lines **before** the main `if m:` parse guard, and while
`in_env_block` is True:
- `env:` key line → keep as-is (`    env:`).
- line matching `^\s+([\w-]+):` → mask the nested key as `${ENV:KEY}`.
- **anything else** (continuation with no colon, deeper indentation) → append a
  blank line (`"\n"`). Never write the original text.
- Exit the block when indent <= env_indent on a non-`env:` line.

```python
if in_env_block:
    ind = len(line) - len(line.lstrip(" "))
    if ind <= env_indent and not re.match(r"^\s*env:\s*$", line):
        in_env_block = False
    else:
        if re.match(r"^\s*env:\s*$", line):
            cfg_lines.append(line + "\n"); continue
        elif re.match(r"^\s+([\w-]+):\s*(.*)$", line):
            nk = re.match(r"^\s+([\w-]+):\s*(.*)$", line)
            envname = nk.group(1).upper().replace(" ", "_")
            cfg_lines.append(f"{nk.group(0).split(':',1)[0]}: ${{ENV:{envname}}}\n")
            continue
        else:
            cfg_lines.append("\n")   # drop continuation (secrets never written)
            continue
```

### Always verify
After generating templates, run a leak scan and require 0 hits:
```bash
grep -c 'cf_clearance\|AWSALBTG\|substack\.sid=\|eyJhbG\|GITHUB_PERSONAL' config.yaml.template
# must print 0
python3 -c "import yaml; yaml.safe_load(open('config.yaml.template'))"  # must be valid YAML
```

## Pitfall: masking the `env:` keyword itself
The `env:` mapping key is at the same indentation as its parent. Guard the
masking branch so the literal `env:` line is kept, not turned into
`env: ${ENV:ENV}` (which would break YAML and confuse bootstrap).

## Pitfall: over-masking non-secrets
Don't mask sibling keys like `timeout:`, `command:`, `args:`. Track the env block
by indentation, not by "any key inside mcp_servers". A new sibling key at
indent <= env_indent must EXIT the block (so `timeout:` stays literal).
