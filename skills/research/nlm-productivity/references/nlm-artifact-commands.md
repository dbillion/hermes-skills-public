# NLM Artifact Commands — Verified Surface (session 2026-07-16)

Condensed, copy-pasteable reference for generating + downloading NotebookLM
studio artifacts. Derived from a real "digest a GitHub repo" task where the
agent initially used wrong flags and lost output.

## Generation commands (all need `-y`/`--confirm` or they prompt + abort)

```bash
# Report — uses --prompt (free text) + --format
nlm report create <nb> --format "Study Guide" --prompt "<text>" --confirm

# Quiz — uses --focus (NOT --prompt); --difficulty is INTEGER 1-5
nlm quiz create <nb> --count 5 --difficulty 3 --focus "<text>" --confirm

# Flashcards — uses --focus; --difficulty is STRING easy/medium/hard
nlm flashcards create <nb> --difficulty hard --focus "<text>" --confirm

# Mindmap — NO --prompt/--focus flag; generates from all sources
nlm mindmap create <nb> --confirm

# Infographic — --focus optional; --orientation landscape/portrait
nlm infographic create <nb> --orientation landscape --style professional --focus "<text>" --confirm

# Slides (quota-limited, shared pool R7cb6c) / Video / Audio / Data-table
nlm slides create <nb> --confirm
nlm video create <nb> --format explainer --style classic --confirm
nlm audio create <nb> --format deep_dive --length long --confirm
nlm data-table create <nb> --description "X by Y" --confirm
```

## Download commands (ALWAYS pass --id, never omit it)

```bash
nlm download report      <nb> --id <art> --output report.md
nlm download quiz        <nb> --id <art> --format json     --output quiz.json
nlm download flashcards  <nb> --id <art> --format markdown --output cards.md
nlm download infographic <nb> --id <art> --output info.png
nlm download slide-deck  <nb> --id <art> --output slides.pdf
nlm download video       <nb> --id <art> --output video.mp4
nlm download audio       <nb> --id <art> --output pod.m4a
nlm download mind-map    <nb> --id <art> --output mindmap.json   # FAILS — see below
```

## Gotchas that bit this session

1. **Never download without `--id`.** Omitting `--id` grabs a default/stale
   artifact → EMPTY content. Quiz came back as `{"title":"Java Flashcards","questions":[]}`
   (51 bytes). Always pull the real ID from `nlm studio status <nb>` or the ID
   printed at `create` time.
2. **Mindmap CANNOT be exported via CLI.** `nlm download mind-map --id <id>`
   fails with `Error: Download failed for mind_map` even when status=completed.
   The mindmap exists and is viewable only in the NotebookLM **web UI**. Do not
   retry endlessly; tell the user to open it there. (All other types download fine.)
3. **`--prompt` != `--focus`.** `report create` takes `--prompt`; `quiz`/
   `flashcards`/`infographic` take `--focus`; `mindmap` takes neither. Passing
   `--prompt` to quiz/flashcards is ignored or errors.
4. **`-y` is mandatory in non-interactive shells.** Without it the command prints
   `Create 'X'? [y/N]` and aborts (exit 130) when piped/backgrounded.
5. **Long shared PROMPT/FOCUS across a batched shell command can break arg
   parsing** (one call returned a truncated error box). Use a concise focus and
   run creations in separate calls if a batch misbehaves.
6. **Poll before download.** `nlm studio status <nb>` → only download artifacts
   whose status is `completed`, not `unknown`. Re-poll every ~15-60s.
