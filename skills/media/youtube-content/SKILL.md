---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs. Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts)."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

## Preferred Method: NLM (NotebookLM)

**ALWAYS try NLM first** — it ingests YouTube URLs directly with full transcript extraction, no extra packages needed.

**Critical: Do NOT install youtube-transcript-api.** Use NLM's `--youtube` source option instead. If you find yourself reaching for pip install, stop and use NLM.

```bash
# Step 1: Create a notebook (or reuse existing)
nlm notebook create "YouTube: [Topic]"
# Note the notebook ID returned

# Step 2: Add the YouTube video as a source
nlm source add <notebook-id> --youtube "https://youtu.be/VIDEO_ID" --wait

# Step 3: Extract the transcript
nlm notebook query <notebook-id> "Extract the full transcript from the video. Include timestamps if available. Format as a clean transcript with speaker labels if identifiable."

# Step 4: For structured output, ask NLM to format it
nlm notebook query <notebook-id> "Summarize the video in 10 sentences."
nlm notebook query <notebook-id> "List the key topics with timestamps as chapters."
```

**This is the preferred workflow** because NLM handles auth, transcript fetching, and processing automatically. Do NOT install `youtube-transcript-api` unless NLM is unavailable.

## Fallback Method: youtube-transcript-api

Only use this if NLM is not available or the video is not processable by NLM.

### Setup

```bash
pip install youtube-transcript-api --break-system-packages
```

### Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript (via NLM or fallback), format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Error Handling

- **NLM preferred**: Always try NLM first with `--youtube` source
- **Fallback script**: Only install `youtube-transcript-api` if NLM unavailable
- **Transcript disabled**: Some videos have no captions — inform the user
- **Private/unavailable video**: Relay the error and ask the user to verify the URL
- **No matching language**: Retry without `--language` to fetch any available transcript
