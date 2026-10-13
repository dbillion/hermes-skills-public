---
name: gemini-cli
description: "Delegate tasks to Google's Gemini CLI agent (gemini-cli)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [agent, cli, gemini, google, automation, delegation]
---

# Gemini CLI

The `gemini` CLI is Google's autonomous agent for the terminal, similar to Claude Code or Hermes. It supports tool-calling, MCP servers, and extensions.

## Usage Patterns

### Headless Execution
To use Gemini CLI as a sub-tool without interaction:
```bash
gemini -p "Prompt here" --output-format text
```

### Auto-Approval (YOLO)
To allow Gemini to execute tools (file edits, terminal commands) without prompting:
```bash
gemini --yolo -p "Task requiring tool use"
```

### Resuming Sessions
```bash
gemini --resume latest -p "Follow-up question"
```

## Pitfalls & Lessons Learned

- **Heavy Initialization:** The CLI loads many extensions and MCP servers at startup. This often causes the first command to time out (default 60s is sometimes insufficient). Use `timeout=120` or higher in `terminal()` calls.
- **MCP Errors:** It is common to see MCP discovery errors (SSE 400, connection closed) during startup if servers are misconfigured or down. These are usually non-fatal but add to the delay.
- **Pathing:** On this system, it is located at `/usr/bin/gemini`.
- **Output Sanitization:** If you need to process the output programmatically, use `--output-format json` or `--raw-output`.
- **Security policy blocks NLM commands:** Gemini CLI's security policy enforcement (Conseca) blocks `nlm` shell commands when run via `gemini --yolo -p`. The model tries many workarounds (aliases, different argument formats, title-based selection) but all fail. Do NOT use Gemini CLI to orchestrate NLM workflows. Run NLM commands directly in the terminal instead. This is the #1 pitfall when the user asks to "use gemini cli with nlm" — they mean use NLM directly, not through Gemini CLI.
- **Rate limits:** Gemini CLI itself can hit 429 rate limits on the Gemini API. When this happens, wait 60s and retry. For long-running tasks, prefer direct terminal execution over Gemini CLI orchestration.

## Integration with Hermes
When Hermes needs to delegate a Google Cloud or Firebase specific task, `gemini-cli` is often the better choice due to its pre-installed extensions.
