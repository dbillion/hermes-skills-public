# nlm command patterns (verified this session)

## Create notebook
```
nlm notebook create "Name Here" --json
# -> "notebook_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

## Upload a source (PDF/TXT/MD/DOCX/image/audio/video)
```
nlm source add "<nbid>" --file <path> --title "<title>" --wait --json
```
- NotebookLM REJECTS `.java` and `.pptx`.
  - Java → copy to `<name>.txt` with a header comment.
  - PPTX → `libreoffice --headless --convert-to pdf --outdir <dir> <file.pptx>` then upload the PDF.

## Invite editor (rate-limit rotation setup)
```
nlm share invite "<nbid>" "<email>" --role editor --profile <main_handle>
```
- Requires EMAIL, not a profile handle.
- `--role editor` (or `viewer`).

## Upload with a specific profile (rotation)
```
nlm source add "<nbid>" --file <path> --title "<t>" --profile <other_handle> --wait
```
- Cycle `--profile` through your editor list to dodge per-account 429s.

## Studio artifacts
```
nlm slides create "<nbid>" --format detailed_deck --length default --confirm --focus "your focus prompt"
nlm infographic create "<nbid>" --orientation portrait --detail detailed --style kawaii --focus "your focus prompt"
```

## Status / share / download
```
nlm studio status "<nbid>"          # takes notebook_id, not artifact_id; "unknown" = rendering
nlm share public "<nbid>"           # returns public notebook URL
nlm download infographic "<nbid>" --id <artid> --output <file.png>
```

## List / dedupe / delete sources
```
nlm source list "<nbid>"            # JSON array; count with grep -c '"id"'
nlm source delete <id1> <id2> --confirm   # needs --confirm AND all ids at once
```

## Gotchas
- `--length dynamic` unsupported for slides → use `default`.
- Foreground `--wait` per file is slow; for bulk, run uploads in a background
  terminal process and poll `nlm source list` count rather than blocking.
- Duplicate uploads happen if a foreground loop + background loop run the same
  files; dedupe by listing and deleting extras afterward.
