---
name: nlm-productivity
description: "NotebookLM CLI for research synthesis, knowledge management, and content generation. Use for creating audio overviews, reports, quizzes, flashcards, slides, and multi-source research with 80-95% token savings."
---

# NLM (NotebookLM) Productivity

NotebookLM CLI (`nlm`) provides direct access to Google NotebookLM for AI-powered research, synthesis, and content generation. Offload research to save 80-95% of AI CLI tokens.

**Install**: `uv tool install notebooklm-mcp-cli` (recommended) or `pip install notebooklm-mcp-cli`
**Auth**: `nlm login` (opens browser, extracts cookies automatically)

## Command Style

The CLI supports **two styles** — use whichever feels natural:
```bash
# Noun-first (resource-oriented)
nlm notebook create "Title"
nlm source add <notebook> --url <url>

# Verb-first (action-oriented)
nlm create notebook "Title"
nlm add url <notebook> <url>
```

## Quick Reference

```bash
# Create notebook and add sources
nlm notebook create "Research Topic"
NB_ID=$(nlm notebook list --json | jq -r '.[0].id')
nlm source add "$NB_ID" --url https://example.com/docs
nlm source add "$NB_ID" --file report.pdf --wait

# Query across all sources
nlm notebook query "$NB_ID" "How does X work?"

# Generate content
nlm video create "$NB_ID" --format explainer --style classic --confirm
nlm slides create "$NB_ID" --confirm
nlm report create "$NB_ID" --format "Briefing Doc" --confirm
nlm audio create "$NB_ID" --format deep_dive --length long --confirm

# Check generation status
nlm studio status "$NB_ID"

# Download artifacts (NOTE: --id flag required, not positional arg)
nlm download video "$NB_ID" --id <artifact-id> --output video.mp4
nlm download slide-deck "$NB_ID" --id <artifact-id> --output slides.pdf
nlm download report "$NB_ID" --id <artifact-id> --output report.md
nlm download audio "$NB_ID" --id <artifact-id> --output audio.m4a
```

## Core Commands

### Notebook Management
```bash
nlm notebook list                      # List all notebooks
nlm notebook list --json               # JSON output (for scripting)
nlm notebook create "Project Research" # Create notebook
nlm notebook get <id>                  # Get details
nlm notebook describe <id>             # AI-generated summary
nlm notebook rename <id> "New Title"   # Rename
nlm notebook delete <id> --confirm     # Delete (IRREVERSIBLE)
nlm notebook query <id> "question"     # Chat with sources
```

### File Delivery Note
When delivering generated artifacts (PDFs, videos, audio) to users on Telegram:
- Use `MEDIA:/absolute/path/to/file` format for native delivery
- **Pitfall**: Files > 20MB may fail silently or be truncated
- **Workaround**: Compress PDFs with `gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile=compressed.pdf input.pdf`
- **Alternative**: Upload to 0x0.st or transfer.sh and share link if MEDIA: fails
- Verify delivery by asking user to confirm receipt

### Source Management
```bash
# Add web sources
nlm source add <notebook> --url https://docs.spring.io/spring-boot
nlm source add <notebook> --url https://example.com --wait  # Add and wait until ready

# Add local files
nlm source add <notebook> --file ~/docs/guide.pdf --wait
nlm source add <notebook> --file ./research-notes.md --title "Notes"
nlm source add <notebook> --text "content" --title "Notes"  # Add raw text

# Add YouTube / Google Drive
nlm source add <notebook> --youtube "https://youtube.com/watch?v=..."
nlm source add <notebook> --drive <doc-id>

# List/get/delete sources
nlm source list <notebook>
nlm source get <source-id>
nlm source describe <source-id>         # AI summary
nlm source stale <notebook>            # Check stale Drive sources
nlm source sync <notebook> --confirm   # Sync stale sources
nlm source delete <source-id> --confirm # Delete (IRREVERSIBLE)
```

### Content Generation

**Video Overviews (slideshow presentations):**
```bash
nlm video create <notebook> --confirm
nlm video create <notebook> --format explainer --style classic --confirm
nlm video create <notebook> --style custom --style-prompt "A children's storybook" --confirm
# Formats: explainer, brief, cinematic
# Styles: auto_select, custom, classic, whiteboard, kawaii, anime, watercolor, retro_print, heritage, paper_craft
# PITFALL: --style flag does NOT work with --format cinematic — use --focus instead
# PITFALL: Video generation can take 3-5 minutes; check status with nlm studio status <id>
```

**Check generation status:**
```bash
nlm studio status <notebook-id>
# Returns JSON with status of all artifacts: in_progress, completed, unknown
# "unknown" often means completed — verify by re-running or checking notebook
```

## Slide Decks:
```bash
nlm slides create <notebook> --confirm
nlm slides create <notebook> --format detailed_deck --length default --confirm \\\n  --focus \"Act as a senior presentation designer. Dark luxury aesthetic. One message per slide. Max 4 bullets, 12 words each.\"\nnlm slides create <notebook> --format detailed_deck --length short --confirm \\\n  --focus \"Clean academic style. White background, dark text. One key point per slide. Minimal bullets. Professional typography.\"\nnlm slides revise <artifact-id> --slide '1 Make the title larger' --confirm\nnlm slides revise <artifact-id> --slide '1 Fix title' --slide '3 Remove image' --confirm
```
# Formats: detailed_deck (default), exploratory\n# Styles: auto_select, custom, classic, whiteboard, kawaii, anime, watercolor, retro_print, heritage, paper_craft\n# PITFALL: --style flag does NOT work with format cinematic — use --focus instead\n# PITFALL: Slide deck generation can take 2-5 minutes; check status with nlm studio status <id>\n# PITFALL: Valid --length options are 'default' and 'short' only — 'dynamic' is not supported
nlm audio create <notebook> --format deep_dive --length long --confirm
# Formats: deep_dive, brief, critique, debate
# Lengths: short, default, long
```

**Reports:**
```bash
nlm report create <notebook> --format "Briefing Doc" --confirm
# Formats: "Briefing Doc", "Study Guide", "Blog Post", "Create Your Own"
```

**Quiz & Flashcards:**
```bash
# NOTE: --difficulty is an INTEGER (1-5) for quiz, STRING (easy/medium/hard) for flashcards.
# --focus (NOT --prompt) guides generation for quiz/flashcards/mindmap.
# -y/--confirm is REQUIRED or the command prompts interactively and aborts (exit 130) in non-interactive shells.
nlm quiz create <notebook> --count 5 --difficulty 3 --focus "Key concepts" --confirm
nlm flashcards create <notebook> --difficulty hard --focus "Definitions" --confirm
```

**Mindmap & Infographic:**
```bash
# mindmap takes NO --prompt/--focus flag — it generates from all sources. -y still required.
nlm mindmap create <notebook> --confirm
nlm infographic create <notebook> --orientation landscape --style professional --focus "Clean technical diagram" --confirm
```
**PITFALL — artifact subcommand flag shapes differ:**
- `report create` uses `--prompt "<text>"` (free text) + `--format "Study Guide"`.
- `quiz`/`flashcards`/`mindmap` use `--focus "<text>"`, NOT `--prompt`. Passing `--prompt` to these is silently ignored or errors.
- `mindmap` has NO focus/prompt flag at all.
- ALL `create` commands need `-y`/`--confirm` or they hang on an interactive `[y/N]` prompt and abort in non-interactive shells.
- When batching multiple `create` calls in one shell command, a too-long shared PROMPT/FOCUS string can break argument parsing (one call returned a truncated error box). Pass a concise focus and run them in separate calls if unsure.

**Other:**
```bash
nlm data-table create <notebook> --description "Sales by region" --confirm
```
### Downloads

```bash
# All downloads use --id flag (not positional artifact ID)
nlm download video "$NB_ID" --id <artifact-id> --output video.mp4
nlm download slide-deck "$NB_ID" --id <artifact-id> --output slides.pdf
nlm download report "$NB_ID" --id <artifact-id> --output report.md
nlm download mind-map "$NB_ID" --id <artifact-id> --output mindmap.json
nlm download infographic "$NB_ID" --id <artifact-id> --output infographic.png
nlm download data-table "$NB_ID" --id <artifact-id> --output data.csv

# Audio: NotebookLM delivers AAC in MP4 container — use .m4a (not .mp3)
nlm download audio "$NB_ID" --id <artifact-id> --output podcast.m4a
# To convert to mp3: ffmpeg -i podcast.m4a -acodec libmp3lame -q:a 2 podcast.mp3

# Interactive formats (quiz/flashcards)
nlm download quiz "$NB_ID" --id <artifact-id> --format json --output quiz.json
nlm download flashcards "$NB_ID" --id <artifact-id> --format markdown --output cards.md
```

**PITFALL — always pass `--id` to downloads, and poll status first.**
- Downloading `quiz`/`flashcards`/`report`/`infographic` WITHOUT `--id` grabs a **default/stale artifact** and may return EMPTY content (e.g. `{"title":"Java Flashcards","questions":[]}` for quiz, or a 51-byte file). Always get the real artifact ID from `nlm studio status "$NB_ID"` (or the ID printed at `create` time) and pass `--id`.
- **Mindmap export does NOT work via CLI.** `nlm download mind-map --id <id>` fails with `Error: Download failed for mind_map` even when `studio status` shows `completed`. The mindmap is generated and viewable in the NotebookLM **web UI** only — there is no CLI export path. Don't burn cycles retrying; tell the user to open it in the UI. (Report JSON, quiz JSON, flashcards, infographic PNG, slides PDF, video/audio all download fine with `--id`.)
- **Mindmap/interactive-format downloads also need the artifact to be `completed`**, not `unknown`. Re-poll `nlm studio status "$NB_ID"` until `completed`, then download.


## Workflow Ordering Rules (USER-ENFORCED — follow strictly)

These came from direct user corrections. Violating them wastes quota and produces
weak output:

1. **CHECK THE CLI BEFORE AUTHORING A WORKAROUND.** The user explicitly corrected:
   "your assumption is much, check again using the help manual on the command." If a
   capability seems missing (e.g. web search, discovery), run `nlm <cmd> --help` and
   `nlm <cmd> --help --ai` FIRST. Do NOT assume a feature doesn't exist and write a
   stand-in file from training data. (The `research` deep-search command was missed
   this way — it DOES exist: `nlm research start --mode deep`.)

2. **ENRICH BEFORE YOU GENERATE.** Always run `nlm research ... --auto-import` (and verify
   with `nlm source list | jq length`) BEFORE creating any slide/video/audio/report. The
   user corrected: "are you using the enriched sources to generate a better more filled
   slidedecks?" Generating first, then regenerating after research, wastes the 3/day
   per-profile slide cap. Order: create notebook → add local files → `research` deep →
   verify import → THEN generate artifacts.

3. **ANIME / CARTOON VISUALS = STATIC NOTEBOOKLM DECK, NOT VIDEO.** "Anime" means the
   *cartoon-genre visual art direction* (Ghibli / Naruto / Superbook worlds) applied to a
   **static slide deck** via a rich `--focus` prompt — it is NOT motion/animation. The user
   explicitly corrected an attempt to build a HyperFrames/anime.js *video*: "slidedeck skills
   dont have animation features, anime here means cartoon genre that have rich visuals
   themes." For anime-style decks, use the **`anime-slidedeck` skill** (which drives
   `nlm slides create` with theme-specific `--focus` prompts + `nlm research` enrichment).
   Do NOT spin up HyperFrames/anime.js video generation when the user wants an anime slide
   deck — that is a different deliverable and was rejected. (HyperFrames is only relevant if
   the user separately asks for an actual *animated* video, which is out of scope here.)

## Token-Saving Workflows

### Offload Research (95% Token Savings)
```bash
# Instead of: gemini "research Spring Boot best practices" (10,000+ tokens)
nlm notebook create "Spring Boot Research"
NB_ID=$(nlm notebook list --json | jq -r '.[0].id)
nlm source add "$NB_ID" --url https://spring.io/guides
nlm source add "$NB_ID" --url https://docs.spring.io/spring-boot/reference
nlm notebook query "$NB_ID" "What are Spring Boot best practices?"
nlm report create "$NB_ID" --format "Briefing Doc" --confirm
# Total tokens to AI CLI: 0
```

### Codebase → NLM Content Pipeline (Repomix + NLM)

For generating educational content from a code repository:

```bash
# 1. Pack repo with repomix (per-phase or per-directory)
repomix --compress --remove-comments --remove-empty-lines \
  --include "phases/<phase-name>/**" \
  -o /tmp/<phase-name>.md --style markdown

# 2. Create NLM notebook per phase
nlm notebook create "Topic: <phase-name>"
NB_ID=$(nlm notebook list --json | jq -r '.[] | select(.title=="Topic: <phase-name>") | .id' | head -1)

# 3. Add repomix output as source
nlm source add "$NB_ID" --file /tmp/<phase-name>.md --title "<phase-name>" --wait

# 4. Generate all content types (rotate profiles to avoid rate limits)
nlm report create "$NB_ID" --format "Briefing Doc" --confirm
nlm slides create "$NB_ID" --confirm
nlm quiz create "$nb_id" --count 10 --confirm
nlm flashcards create "$nb_id" --confirm
nlm mindmap create "$nb_id" --confirm
nlm infographic create "$nb_id" --orientation landscape --style professional --confirm
nlm audio create "$nb_id" --format deep_dive --length long --confirm
nlm video create "$nb_id" --format explainer --style classic --confirm

# 5. Download all artifacts (check status first, then download by ID)
nlm studio status "$NB_ID" --json | jq -r '.[] | select(.status=="completed") | "\(.type) \(.id)"'
nlm download video "$NB_ID" --id <artifact-id> --output video.mp4
nlm download audio "$NB_ID" --id <artifact-id> --output podcast.m4a
nlm download slide-deck "$NB_ID" --id <artifact-id> --output slides.pdf
nlm download report "$NB_ID" --id <artifact-id> --output report.md
nlm download quiz "$NB_ID" --id <artifact-id> --format html --output quiz.html
nlm download flashcards "$NB_ID" --id <artifact-id> --format markdown --output flashcards.md
nlm download mind-map "$NB_ID" --id <artifact-id> --output mindmap.json
nlm download infographic "$NB_ID" --id <artifact-id> --output infographic.png
```

**Profile rotation strategy**: Distribute notebooks across multiple NLM profiles. When one profile hits rate limits (INVALID_ARGUMENT error), switch to the next profile with `nlm login switch <profile>`. Space video generations by 60-90s. Generate lighter artifacts (slides, report, quiz, flashcards, mindmap, infographic) while waiting for video/audio.

### Competitive Research
```bash
nlm notebook create "Competitor Analysis"
NB_ID=$(nlm notebook list --json | jq -r '.[0].id)
nlm source add "$NB_ID" --url https://competitor1.com/docs
nlm source add "$NB_ID" --url https://competitor2.com/features
nlm notebook query "$NB_ID" "Compare features of all competitors"
nlm report create "$NB_ID" --format "Briefing Doc" --confirm
```

### Research → Video Pipeline (for presentations)
```bash
# 1. Deep research via Gemini API
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Research topic here"}]}]}' \
  | jq -r '.candidates[0].content.parts[0].text' > /tmp/research.md

# 2. Create notebook and add research
nlm notebook create "Research Presentation"
NB_ID=$(nlm notebook list --json | jq -r '.[0].id)
nlm source add "$NB_ID" --file /tmp/research.md --title "Deep Research" --wait

# 3. Generate video/slides
nlm video create "$NB_ID" --format explainer --style classic --confirm
nlm slides create "$NB_ID" --confirm

# 4. Download
nlm download video "$NB_ID" <artifact-id> --output presentation.mp4
nlm download slide-deck "$NB_ID" <artifact-id> --output slides.pdf
```

## Best Practices

1. **Create topic-specific notebooks** — separate notebooks per subject
2. **Add 3-5+ sources** before generating complex artifacts
3. **Use `--wait` flag** when adding files/URLs to ensure they're processed before generating content
4. **Use `--confirm`** on all generation commands (required by the CLI)
5. **Use `--json` output** for notebook list when scripting (pipe through jq)
6. **Combine with repomix** for codebase + documentation analysis
7. **Download artifacts** with `nlm download <type> <notebook> --id <artifact-id> --output file.ext`

**PDF Ingestion**: Add PDFs directly to NLM with `nlm source add <nb_id> --file <path> --wait`. NLM extracts text from PDFs natively. Do NOT use pdftotext, python docx, or other local PDF tools — NLM handles all of this.

**Bible Passage Ingestion**: When you need to study specific Scripture passages, add them as text sources: `nlm source add <nb_id> --text "Exodus 20:8-11 (ESV) — ..." --title "Exodus 20:8-11"`. Then query NLM for analysis, application questions, and theological reflection on those passages.

**Course Material Workflow**: For seminary assignments, create one notebook per course. Ingest ALL materials (syllabus, lessons, slides, readings, assignment sheets). Query NLM to extract assignment requirements first, then write the paper using the seminary-writer skill. Use NLM to get proper APA 7 citations for all sources.

## User Workflow Preference

When the user asks to "get nlm/gemini cli to the work", they want **direct terminal execution** — not a description of what to do. Always:
1. Run the commands directly in the terminal
2. Report results back with file paths and sizes
3. Handle errors and retries inline
4. Deliver generated artifacts (video, slides, audio, reports) to the user

Do NOT just explain what commands to run. Actually run them.

## Pitfalls

- **Slides revise failures:** `nlm slides revise` is strict about per-slide instructions. Large multi-slide revisions often fail; apply changes **one slide at a time**, wait for completion, then chain the next revision from the latest artifact ID. This is especially important for theme changes or new content on the final slide.
- **`nlm research` is FLAKY:** `research start` frequently returns an error box or hangs, and `research status` can hang/interrupt. It succeeded once (Speechify, imported 77 sources) but is NOT reliable. Treat research enrichment as best-effort — do NOT loop on it. If it hangs (command times out), skip it and generate the digest from existing sources.
- **Mindmap not CLI-exportable:** `nlm download mind-map` errors with "Download failed for mind_map". The mindmap generates fine in the NotebookLM UI but there is no CLI path to pull it to a file. Report it as "generated, viewable in UI, not exportable via CLI" rather than retrying endlessly.
- **Use dedicated artifact subcommands, not `nlm query`:** `nlm report create`, `nlm quiz create --focus "..."`, `nlm flashcards create --focus "..."`, `nlm mindmap create` (NO --focus flag), `nlm infographic create --focus "..."`. Each prompts `[y/N]` interactively — pass `--confirm` (or pipe `yes`) to run non-interactively. `nlm query` is just chat; it does NOT produce a retrievable artifact.
- **Pass `--id` on download when multiple artifacts exist:** `nlm download <type> <notebook> --id <artifactId>` is required when several artifacts of one type exist or the default download grabs a stale/wrong one (observed: `download quiz` pulled a flashcards-shaped stub until `--id` was passed).

- **Rate limiting**: Video/audio/slide generation can hit rate limits (error code 8). When the user requests cooldown, **wait 5 minutes between heavy artifacts** (video/audio/slide deck). Use `--format explainer` instead of `cinematic`. If rate limit persists, try `--format brief` which is lighter.
- **SLIDE-DECK cooldown is STIFFER than other artifacts**: In one session, `nlm slides create` hit `RESOURCE_EXHAUSTED` (code 8, `R7cb6c`) after a 30s wait AND after a 120s wait AND after a 300s wait — all three failed with "Wait a few minutes before retrying slide deck creation." The user explicitly mandated a **5-minute sleep before slide generation**; even that was not always enough. Empirical rule: after any slide-deck rate-limit error, wait **≥5 min (300s)**, and if it still fails, wait **~25 min** before retrying. Do NOT loop retries at 30s/120s intervals — that burns the window and never clears it. Other artifacts (report, quiz, flashcards, infographic) are less sensitive; slides are the strictest.
- **Missing-only runs**: If the user asks to “finish only missing artifacts,” do **not** restart a full generation loop. Run a missing-only pass and preserve completed outputs.
- **Profile rotation needs access**: If you see `Error: Could not retrieve notebook sources.`, the profile does **not** have access to that notebook. Share the notebook to that account before switching.
- **Sharing notebooks for rotation**:
  - `nlm share batch` can return **INVALID_ARGUMENT** with comma lists. Use **single invites** instead:
    - `nlm share invite <notebook-id> <email> --role editor`
  - **DEFAULT ROLE IS VIEWER.** A viewer can read sources but CANNOT generate artifacts
    (slides/video/audio). You MUST pass `--role editor` for the collaborator to be able to
    generate their own deck. (Session: 8 invites landed as "viewer" first, had to re-invite
    with `--role editor`.)
  - **You need the collaborator's EMAIL, not the profile name.** `nlm share invite` takes
    `{notebook} {email}` — there is no profile-name alias. The CLI does NOT expose profile
    emails (`nlm login` shows "Account: Unknown"; no `list` subcommand). Get the emails from
    the user (e.g. `<YOUR_EMAIL>`). `nlm login switch <profile>` is for operating AS
    a profile; inviting requires the email address.
  - **Editor invites do NOT bypass an active rate-limit window.** All profiles in this setup
    share one backend quota pool (the same `R7cb6c` RESOURCE_EXHAUSTED id appeared on every
    profile). Inviting editors helps you run PARALLEL *different* decks (e.g. one profile =
    Ghibli, another = Naruto) once the window resets, but it will NOT get you past a live
    "wait a few minutes" slide-deck rate limit. For that, wait out the window (often longer
    than 5 min — a 300s cooldown still failed; schedule a retry ~25 min later).
  - If you see **PERMISSION_DENIED**, switch to the notebook **owner profile** and invite from there.
  - Confirm with `nlm share status <notebook-id>` — owner only means no collaborators yet.
  - **Notebook visibility after invite**: an editor invite may need the collaborator to
    ACCEPT before the notebook appears in their `nlm notebook list`. The CLI lists only
    notebooks created by the active profile, so cross-profile *generation* may still require
    acceptance. Don't assume switching profiles makes a shared notebook immediately visible.
- **Multi-profile rotation**: The user maintains 10+ NLM profiles to avoid rate limits. Check available profiles with `nlm login profile list`. Switch with `nlm login switch <profile>`. Distribute notebook creation and content generation across profiles. Profiles with fewer notebooks have more headroom. When one profile hits INVALID_ARGUMENT (code 3), switch to the next profile. Valid profiles from this session: dayozoe, mentora, trinity, abiodun, default, adeoye53, oludayo35, glorious, architect, adeoye55er.
- **Background processes**: The terminal blocks `&` backgrounding in foreground mode. Run `nlm` commands sequentially, not in parallel with `&`.
- **Gemini CLI + NLM**: Do NOT use `gemini --yolo` to orchestrate NLM commands. Gemini CLI's security policy enforcement blocks NLM shell commands, causing massive overhead and failures. Run NLM commands directly in the terminal instead.
- **Quiz difficulty**: `nlm quiz create` `--difficulty` takes an integer, NOT a string like "medium". Use `--count 10` without `--difficulty` to avoid the error.
- **Studio status JSON format**: `nlm studio status <id> --json` returns an ARRAY of artifact objects, not an object with `.artifacts` key. Query with: `jq -r '.[] | select(.type=="video" and .status=="completed") | .id'`. Do NOT use `.artifacts.video[0].id` — it will fail with "Cannot index array with string".
- **Download subcommand name uses HYPHEN, not underscore**: `nlm download slide-deck` (correct) — `nlm download slide_deck` FAILS with "No such command 'slide_deck'. Did you mean 'slide-deck'?". Similarly the valid subcommands are `video`, `audio`, `slide-deck`, `infographic`, `report`, `mind-map`, `data-table`, `quiz`, `flashcards`. A background poller that loops over artifact types MUST use the hyphenated form or every slide-deck download silently fails (logs "done (0 bytes)"). Verify with `nlm download --help`.
- **Shell wait loops**: When polling `nlm studio status` in a shell loop, redirect stderr and use `head -1` to avoid null byte output flooding. Example: `nlm studio status "$nb_id" --json 2>/dev/null | jq -r '.[] | select(.type=="video") | .status' | head -1`
- **Large file writes**: The `write_file` tool may fail with \"interrupted\" errors for files >10KB. Use `printf` or `python3 -c` with file writes for large content. Avoid `cat << 'EOF'` heredocs — they also fail in this environment.
- **Report ignores uploaded local source, anchors on web docs only**: `nlm report create`
  synthesizes from the *imported research/web sources*, NOT reliably from a
  file you added via `nlm source add --file`. In this session the notebook
  had 275 web sources + the bot's own source file, yet the generated
  report discussed library trends and quoted maintainers but OMITTED the
  bot's actual capacity, git history, and the user's specific conversion ask.
  FIX: treat the NLM report as the *library-research section only*; author
  the project-specific sections (current state, architecture, roadmap) yourself
  from the source you already read. Do NOT expect one `report create` to
  tie web research back to your uploaded code — it won't.
- **Video + style**: `cinematic` format rejects `--style`. Use `explainer --style classic` for reliable results.
- **Artifact IDs**: Download commands require `--id <artifact-id>` flag, not positional arguments.
- **Gemini CLI extension installs**: Use `--consent` flag to skip interactive confirmation: `gemini extensions install <url> --consent`
- **File delivery via messaging**: The `send_message` tool's `MEDIA:` tag may report success but not actually attach files. For files >5MB, consider compressing first or sharing via alternative means. File sharing services (0x0.st, transfer.sh) may be unavailable — have fallback delivery methods ready.
- **Video status "unknown"**: On some accounts `nlm studio status` returns `"status": "unknown"` for videos/infographics/slides that are STILL PROCESSING (downloads of "unknown" artifacts fail with "Download failed"). Do NOT assume "unknown" = completed here — re-poll after 60-120s and only attempt download once status reads `"completed"`. (Older guidance claimed "unknown often means completed"; that does NOT hold on every account — verify by polling, not by assuming.)
- **Authoring vs researching sources**: When the user wants credible/external material, use `nlm research` to discover real sources — do NOT author replacement content from the agent's own training data. The user explicitly relies on NotebookLM's own search for credibility. If a topic is missing from the uploaded files, run `nlm research start --mode deep` rather than writing a stand-in markdown file.
- **Profile source-ingestion failure**: A profile can have valid auth (`nlm notebook list` works) yet fail to add URL sources ("Could not add URL sources") or fail artifact generation with "Could not retrieve notebook sources." This is account-specific, not a CLI bug. Fix: recreate the notebook on a DIFFERENT profile and retry. Do not waste cycles debugging the stuck profile — switch and move on.
- **Audio download failures**: `nlm download audio` can fail even when status shows "completed". Retry after 30s. If persistent, the audio may still be accessible via the NotebookLM web UI.
- **Large PDF sources**: Adding large PDF files (e.g., annual reports >5MB) as sources may timeout with `--wait`. Add without `--wait` and proceed with other sources; the PDF will process in the background.
- **Multiple video generations**: Generating multiple videos in sequence can trigger rate limits. Space video generations by **5 minutes** when the user requests cooldown. Generate other artifacts (slides, report, infographic, mindmap) while waiting.
- **Cross-notebook query timeout**: `nlm cross query --all` times out when querying all notebooks due to rate limits. Target specific notebooks with `--notebooks "Notebook Name"` instead. Query 2-3 relevant notebooks at a time.
- **chat vs query**: `nlm chat` is interactive only (starts a session). For programmatic queries, use `nlm cross query` (cross-notebook) or `nlm notebook query <id> <question>` (single notebook).

## YouTube Transcript Extraction

**NLM is the best tool for YouTube transcripts** — no external packages needed. This replaces the `youtube-transcript-api` pip package approach entirely.

```bash
# Create notebook and add YouTube video
nlm notebook create "YouTube: [Topic]"
nlm source add <notebook-id> --youtube "https://youtu.be/VIDEO_ID" --wait

# Extract transcript
nlm notebook query <notebook-id> "Extract the full transcript from the video. Include timestamps if available. Format as a clean transcript with speaker labels if identifiable."

# Other useful queries
nlm notebook query <notebook-id> "Summarize this video in 10 sentences."
nlm notebook query <notebook-id> "List the key topics/chapters with timestamps."
nlm notebook query <notebook-id> "What are the main arguments or points made?"
```

**PITFALL**: Do NOT install `youtube-transcript-api` for transcript extraction. NLM handles it natively. The pip package approach fails due to environment issues and is unnecessary overhead.

**PITFALL**: The Zapier YouTube MCP (`zapier-youtube-mcp`) does NOT have a transcript extraction tool. It's for search, analytics, uploads, and API calls only. Route all transcript requests through NLM.

## Source Discovery (Deep Web Research) — CLI-FIRST

NotebookLM can search the web and auto-add credible sources via the **`research`** command.
This is the PREFERRED way to enrich a notebook with authoritative external material
instead of authoring content from the agent's own training data. The user relies on this
for credible sourcing — always run it when a topic needs external authority
(hardware, compilation, complexity theory, competitive research, etc.).

```bash
# Deep web search (~40 sources, ~5 min) and auto-import into an existing notebook
nlm research start "<detailed query>" --mode deep --notebook-id "$NB_ID" --auto-import

# Or: start, poll, then explicitly import (use if --auto-import returns early)
nlm research start "<query>" --mode deep --notebook-id "$NB_ID"
nlm research status "$NB_ID"          # wait until Status: completed
nlm research import "$NB_ID" <task-id>  # add discovered sources to the notebook
```

**Flags:**
- `--mode fast` (~30s, ~10 sources) or `--mode deep` (~5min, ~40 sources, web only)
- `--source web` (default) or `--source drive`
- `--title <t>` to create a NEW notebook instead of `--notebook-id`
- `--auto-import` waits for completion and imports automatically
- `--force` starts even if a task is already pending

**Workflow:** run `research` BEFORE generating artifacts whenever the topic needs
external credibility. A single deep search can add 40-64 sources (a notebook grew from
15 → 141 sources in one run). The imported sources then feed slides/video/audio/report.

**Gotcha:** `--auto-import` sometimes returns before all sources land. After it finishes,
run `nlm research import "$NB_ID" <task-id>` explicitly, then verify with
`nlm source list "$NB_ID" --json | jq 'length'`.

### Workflow Pitfalls (session-verified — these BIT the agent)

**P1 — Do NOT reverse the order: build/run code BEFORE repomix+upload.**
The documented pipeline is repomix → notebook → research → generate. The agent
reversed it (wrote + tried to compile the solution first, deferred repomix/NLM
to "after"), and the user called it out: "you did not use repomix cli to
pack... why". For a "digest this repo / upload the solution" task, the repomix
PACK + NOTEBOOK UPLOAD is the deliverable — code correctness is a *parallel
verification*, not a gate that precedes packing. Run repomix on the repo FIRST
(one command, ~30s), upload to NLM, THEN verify the code compiles/tests in
parallel. Never let compile/test debugging block the pack+upload step.

**P2 — `nlm research start` DISCARDS pending results; `import` prompts interactively.**
If a previous `research start` left a pending task, running `research start` again
prints "Starting new research will discard existing results... Continue? [y/N]" and
**aborts (exit 130) when non-interactive**. Fix: run `nlm research import "$NB" <task-id>`
FIRST to save the pending 77 sources, then start new research only if needed.
The `import` itself may also prompt — pipe `yes |` to it. Never assume a prior
research task is gone; check `nlm research status "$NB"` before starting new.

**P3 — Asserting SOLID/clean-code compliance without re-auditing is a lie.**
When refactoring, do NOT label files "SRP/OCP/DI" from memory. After writing,
re-READ every final file and check each principle against the actual code. The
agent claimed DI was applied, but repositories still did `new Database()` /
`new LRUCache()` internally (DI only at the service layer). User (verbatim, twice):
"you didnt use the solid on all those files" and "you did not use the solid on all
those files / first commit it before editing so we can revert if it fails / just
tell me which file you fixed." Fix sequence the user enforced:
  1. **COMMIT the tested/working state FIRST** (`git commit` on the baseline or last
     green build) BEFORE any further edit — clean revert point. Use
     `git diff --diff-filter=A/M/D --name-only <baseline> HEAD` to PROVE which files
     are new vs modified vs untouched; never claim "fixed an existing file" for a file
     you actually CREATED (verify with `git ls-tree <baseline> --name-only | grep`).
  2. **Re-audit every file against S/O/L/I/D** by reading it, not asserting. If a class
     still `new`s a concrete dependency internally, DI is NOT done — delete the no-arg
     constructor, keep ONLY injected constructors.
  3. **Prove with the test, not with prose.** Run the actual test command
     (e.g. `./gradlew test`) and report the real count (e.g. "9/9 passing"). The test
     caught 3 genuine compile bugs the reasoning missed.
  4. **When asked "which file did you fix" — name the ONE file** the test forced a change
     in (here: `UserRepository.java`), separately from files changed for principle
     strengthening. Be precise; don't over-claim.
After the DI fix, commit AGAIN as a separate commit so each change is independently
revertible (`git revert <hash>`).

**Web-UI alternative** (only if CLI is unavailable): open the notebook in NotebookLM web
UI → "Discover sources" → type query → select sources to auto-add. Prefer the CLI.

Tips:
- Be specific in the query: "time and space complexity tradeoffs in algorithms" not "algorithms"
- Look for authoritative sources (official docs, university lectures, established tech blogs)
- Aim for 6-40 sources depending on `--mode`; deep mode yields the richest set
- Verify each imported source has complete metadata after import

## Slide Decks with Visual Focus
## Slide Decks with Visual Focus
For high-quality slide decks, use `--focus` with `--length` options (default or short):

```bash
# Basic slide deck
nlm slides create <notebook-id> --confirm

# Detailed deck with visual design focus
nlm slides create <notebook-id> --format detailed_deck --length default --confirm \
  --focus "Act as a senior presentation designer. Dark luxury aesthetic. One message per slide. Max 4 bullets, 12 words each."

# Custom visual style
nlm slides create <notebook-id> --format detailed_deck --length default --confirm \
  --focus "Clean academic style. White background, dark text. One key point per slide. Minimal bullets. Professional typography."

# Shorter, more concise deck
nlm slides create <notebook-id> --format detailed_deck --length short --confirm \
  --focus "Executive summary style. Focus on key takeaways only. Minimal text, maximum visual impact."
```

The `--focus` parameter controls visual design, layout, and content density. Use `--length default` for standard decks (~10-15 slides) or `--length short` for concise presentations (~5-10 slides). Note: The `--length dynamic` option is not supported.

## See Also

- `references/gemini-cli-extensions.md` — Installation, features, and token impact of Gemini CLI extensions.
- `references/dsa-enriched-pipeline.md` — Full reproduce-with-modifications DSA teaching pipeline (source files, profile rotation, poller, rich-visual split).
- `references/java-gradle-version-test.md` — Gradle 8.2 vs Java 21 incompat fix (sdkman Java 17), how to run + verify `./gradlew test` on a Java repo you must build/test as part of a digest task.
- `references/nlm-artifact-commands.md` — EXACT artifact generate/download command surface (report uses --prompt; quiz/flashcards/infographic use --focus; mindmap takes neither; all need -y), the empty-quiz `--id` bug, and the mindmap-CLI-export limitation.
- `seminary-writer` skill — for theological paper writing with NLM source extraction, APA 7 citations, and humanization.
- `notebooklm-visuals` skill — for McKinsey/Apple-style premium slide deck design with `--focus` prompts.
- `anime-slidedeck` skill — for Ghibli/Naruto/Superbook CARTOON-GENRE static slide decks (the user's "anime" = rich cartoon art direction on a PDF/PPTX deck, NOT video; see Workflow Ordering Rule #3).
