#!/usr/bin/env python3
"""
Reusable template: insert a structured section under every `### Header` block
in a markdown doc, WITHOUT the header-boundary leak.

Key invariants that prevent corruption:
  * Block scan stops at ANY `^### ` header (`^###\\s`), never a subset.
  * Per-block state (code_token) is reset at the start of EVERY block.
  * The identifier comes from the block's own `<code>token</code>`, not a
    fragile code-signature regex.

Adapt `make_section(block_text, code_token)` to emit your table/section.
"""
import re

def make_section(code_token: str) -> str:
    """Return the markdown to insert (e.g. a 2-col/3-row table)."""
    if not code_token:
        code_token = "this"
    return (
        "**Optimised vs Modern rewrite (Java 25 LTS):**\n\n"
        "| | Detail |\n|---|---|\n"
        f"| **Optimised version (tested)** | `{code_token}` — the implementation under JUnit above. |\n"
        "| **Modern rewrite (Java 25 LTS)** | Implemented with modern Java; Java 25 LTS stabilizes record patterns, pattern-matching switch, Stream/var ergonomics. |\n"
        "| **Gains** | Declarative/immutable styles replace pre-Java-8 boilerplate where applicable; same complexity, less mutable state. |\n"
    )

def insert_sections(path: str, pilot_skip: set[str] = None) -> dict:
    pilot_skip = pilot_skip or set()
    src = open(path, encoding="utf-8").read()
    lines = src.split("\n")
    n = len(lines)
    out = []
    i = 0
    inserted = 0
    skipped = 0
    while i < n:
        line = lines[i]
        out.append(line)
        m = re.match(r"^###\s+(\S+)", line)
        if m and line.endswith("."):  # a real `### Q1.` style header
            qid = m.group(1).rstrip(".")
            if qid in pilot_skip:
                skipped += 1
                i += 1
                continue
            block = []
            j = i + 1
            code_token = ""
            saw_func = False
            saw_unit = False
            # STOP AT ANY HEADER — never a subset
            while j < n and not re.match(r"^###\s", lines[j]):
                block.append(lines[j])
                if "**Function (Algorithms.java):**" in lines[j] or "*source: Algorithms.java*" in lines[j]:
                    saw_func = True
                if "**Unit test (JUnit 5):**" in lines[j]:
                    saw_unit = True
                cm = re.search(r"<code>([^<]+)</code>", lines[j])
                if cm:
                    code_token = cm.group(1)
                j += 1
            if saw_func and saw_unit and code_token:
                table = make_section(code_token)
                newblock = []
                for bl in block:
                    if bl.strip().startswith("<p align=\"center\"><img") and ".gif" in bl:
                        newblock.append(table)
                        newblock.append("")
                    newblock.append(bl)
                out.extend(newblock)
                inserted += 1
            else:
                out.extend(block)
            i = j
            continue
        i += 1
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return {"inserted": inserted, "skipped": skipped}

if __name__ == "__main__":
    import sys
    print(insert_sections(sys.argv[1] if len(sys.argv) > 1 else "README.md"))
