---
name: local-llm-ops
description: "Use when operating local LLM gateways and memory daemons."
---

# Local LLM Ops

Operating rules for running model gateways, memory brains, and their wiring from inside an agent session on the user's own box.

## 1. Session discipline (hard rule)

After EVERY tool batch, emit a visible human-readable status: what ran, what it returned, what is next. NEVER return an empty response after executing tools — an empty turn reads as a stall and the user will (rightly) call it out. If tool output arrived truncated or demoted, say so explicitly, then re-query or poll rather than going silent. One status line minimum; a short table for multi-part work.

## 2. Secret hygiene

- API keys and bearer tokens are verified by LENGTH only (`printenv KEY | wc -c`, `len()` in a parser) and passed IN-MEMORY via env vars. Never print a value, never write one to disk outside the tool's own config store, never commit one.
- When a gateway server on the box already holds the key, retrieve it at runtime from the server's own process environ (`/proc/<pid>/environ`, pid found via the listening port) directly into a shell variable — no intermediate files. See `references/secret-handling.md`.
- Background shells start with an EMPTY environment (verified: key length 1 vs 47 in the main session). Key-dependent commands MUST run in the foreground session where the env lives; use background only for key-free long polls.

## 3. Single-writer embedded stores

PGLite-style brains allow exactly one writer. The serving daemon holds the lock; CLI writes refuse while it runs. Discipline: stop serve, mutate (init/mint/sync), restart serve, health-check. Reads that can delegate through the live serve (e.g. `sync`) need no restart. Never delete a lock directory while its PID is alive.

## 4. Rate-limited embedding runs

On provider 429s: shrink the batch (`--batch-size 5`), back off with sleeps between passes, and re-run `--stale` until it reports zero remaining. Track progress via the worker's I/O counters, not wall-clock. A leftover subset in a previous embedding space is acceptable; note it, offer the re-embed cost, do not loop forever.

## 5. Catalog is not availability

A gateway's `/v1/models` listing is a STALE CLAIM. Any model intended for real work gets a tiny live chat-completion smoke test first; record working vs dead vs quota-exhausted with exact error text. Provider prefixes route to different credential pools (`oc/` vs `openrouter/` vs `opencode/`), so keep one fallback per pool. Back up any config file before rewriting it, keep provider blocks intact, and verify the file still parses afterwards.

## 6. Daemon lifecycle

First starts download models and take minutes — background them with completion notify, then poll status plus an HTTP health endpoint. Daemonized CLIs with profiles (Hindsight-embed pattern: `profile create --port --env`, `daemon start/stop/status`, banks before retain) need env changes followed by a restart; budget one restart cycle per config change. See `references/hindsight-selfhosted.md`.
