# Secret handling in agent sessions

Context: single-user Linux box, Hermes agent terminal. Goal: use the user's own keys without ever exposing them.

## Rules
- Verify by length only: `printenv NAME | wc -c`, or parse a config and print `len()` per value — never the value.
- Pass in-memory: `export KEY="$(...)"` inside the same command that consumes it; `unset` after.
- Never `echo`/print/tail a variable holding a secret. `tail`/`head` on commands containing `export KEY="literal"` leaks into transcripts — always use command substitution, never literals.
- Background process command lines are visible via `ps`: prefer foreground for commands whose argv would carry a secret; daemons should read secrets from their own profile/config store, not argv.

## Retrieving a gateway bearer key at runtime

When an OpenAI-compatible gateway (e.g. OmniRoute desktop) runs locally and the key is not in the shell:

1. Find the server pid: port scan for the gateway port (e.g. 20128).
2. Confirm the key name exists (names only): `tr '\0' '\n' < /proc/<pid>/environ | cut -d= -f1 | grep -i key`.
3. Length-check only via a short parser over `/proc/<pid>/environ`.
4. Consume in-memory: `KEY="$(python3 -c "print(open('/proc/<pid>/environ','rb').read().decode().split('OMNIROUTE_API_KEY=')[1].split(chr(0))[0])")"; curl ... -H "Authorization: Bearer $KEY"; unset KEY`.
5. Pids change across restarts — re-resolve the pid every session, never hardcode it.

## Background vs foreground environment

Observed (Hermes terminal): background shells start EMPTY — a var 47 chars in the main session measured length 1 in background. Consequence: any command needing a secret runs in the FOREGROUND session; background is for key-free long waits (sleeps, downloads, model pulls) with notify-on-complete.
