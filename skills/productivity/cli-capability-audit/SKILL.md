---
name: cli-capability-audit
description: Verify CLI auth and real commands before claiming value.
---

# CLI Capability Audit

## When to use
- User: "i have X cli", "what value can you bring with X", "what can you do with X".
- Onboarding a new CLI into the workflow, or about to use a CLI unverified this session.

## Process (always verify, never assume)
1. **Confirm binary exists** — `which <cli>` / `ls` common paths. Note exact path (some live in nvm/uv/venv, not default PATH — e.g. `/home/deeone/.local/bin`, `/home/deeone/.nvm/.../bin`).
2. **Verify AUTH with a real read-gated call** — NOT `--help`:
   - gws → `gws drive files list` or `gws gmail users getProfile --params '{"userId":"me"}'`
   - nlm → `nlm notebook list`
   - kaggle → `kaggle config view` + `kaggle competitions list`
   - hf → `hf auth whoami` (NOT `hf whoami` — that command doesn't exist)
   - colab → `colab log`
   If real data returns → authed. If "Not logged in"/auth error → flag clearly, give exact login command; do NOT describe write capabilities you can't use.
3. **Enumerate REAL commands** — `<cli> --help`. Capture actual subcommands; don't invent.
4. **Propose 2–3 concrete tasks** from the user's actual data (their notebooks, Drive files, repos). Tie to ongoing work.
5. **Flag honest limits** — plan restrictions, missing auth, read-only scope, what the CLI CANNOT do (e.g. NotebookLM/gws won't post to LinkedIn; agent-reach has no publish command).

## Pitfalls
- Never describe capabilities from memory alone. A live read call is the only proof.
- Don't fabricate commands. Gotchas: `kaggle whoami`→`kaggle config view`; `hf whoami`→`hf auth whoami`; `nlm notebooks list`→`nlm notebook list`.
- Don't guess repo/dataset slugs. Use web-verified real repos. HF public-domain books: `manu/project_gutenberg`, `common-pile/project_gutenberg`, `stevez80/Sci-Fi-Books-gutenberg`. Large parquet downloads can exceed 60s timeout — that's a timeout, not a failure.
- Chain value across the stack: HF book → Colab process → NotebookLM summarize → gws store.

## This-user stack (verified this session — re-verify each session)
- gws (Google Workspace) → <YOUR_EMAIL>, authed. 17 services.
- nlm (NotebookLM) → 22 profiles, notebooks listed. 2026 upgrades: research-from-idea (`nlm research start/status/import`), studio/code-exec artifacts (`nlm studio`), export to Docs/Sheets (`nlm export to-docs/to-sheets`), audio overviews (`nlm audio`).
- kaggle → oludayoadeoye777, authed. v2.0.0 (upgrade to 2.2.2 available).
- hf → `/home/deeone/.local/bin/hf`, NOT logged in.
- colab → 9 named sessions (dsa-nb-*), authed. `colab ls` shows no active VM (history only); `colab new` starts one.
- agent-reach + opencli → 5 social platforms, LinkedIn MCP persistent (systemd). (agent-reach skill is user-owned — do not patch; recommend `hermes curator adopt` if fixes needed.)
