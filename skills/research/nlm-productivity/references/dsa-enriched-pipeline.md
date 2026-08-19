# DSA Enriched Teaching Pipeline (reproduce-with-modifications)

Verified workflow for turning DSA study files into a full teaching bundle
(slide decks, infographics, video, audio, report, flashcards, quiz) with
credible external sourcing and rich visuals. Derived from a real session where
the user wanted: Python idioms vs modern Java, hardware/compilation "why",
and the speed/space decision-table framing.

## Source files used (local, in /home/deeone/Desktop/jobhunting/dsa/)
- dsa-ultimate.md              — 20 algorithms + 40 LeetCode Q's + full roadmap tree
- Python_Tricks_Best_Practices.md — Python idioms
- DSA_Python_Reference.md / _Part2.md — runnable Python snippets per structure
- DSA_Interview_Questions_40_Java.md — 40 Java Q's
- DSA_Advanced_Gaps.md         — authored gap-filler (bit manipulation + matrix chain)
- DSA_Hardware_Compilation.md  — authored gap-filler (hardware/compilation "why")
- dsa_practice_snippets.py     — practice code (add as --text, .py is rejected)
- DSA_Test_Harness.py          — 13 passing pytest tests (proves snippets run)

NOTE: the two "authored gap-filler" files exist ONLY because `nlm research`
could not itself surface those exact topics. PREFER `nlm research` (see below)
over authoring — the user explicitly wants credible external sources, not
agent training data. Author only when research returns nothing usable.

## Correct ORDER (user-enforced)
1. Create notebook on a fresh profile.
2. Add all local files (+ --text for .py).
3. `nlm research start "<query>" --mode deep --notebook-id "$NB" --auto-import`
   then `nlm research import "$NB" <task-id>` and verify
   `nlm source list "$NB" --json | jq length` jumped (15 -> 141 in one run).
4. NOW generate artifacts.

## Multi-profile quota bypass (3 slide decks/day per profile)
The user keeps 8+ NLM profiles. Slide-deck cap is per-account, so spread
notebooks across profiles: mentora / trinity / glorious / oludayo35 /
adeoye55er / architect / abiodun / adeoye53. Use `nlm login switch <p>` then
operate. A profile can have VALID auth yet fail URL adds ("Could not add URL
sources") or artifact gen ("Could not retrieve notebook sources") — that is
account-specific; recreate the notebook on a DIFFERENT profile and move on
(abiodun exhibited this; oludayo35 worked fine).

## Generation targets that worked
- Slide deck academic:   `nlm slides create "$NB" --format detailed_deck --length default --confirm --focus "..."`
- Slide deck dark luxury: same + focus with obsidian/gold/emerald palette, Playfair+Inter
- Infographic (enriched): `nlm infographic create "$NB" --orientation landscape --style professional --confirm --focus "..."`
- Video capstone: `nlm video create "$NB" --format explainer --style classic --confirm --focus "algorithms solve SPEED (time) + SPACE (RAM) problems; decision table to pick the right one"`
- Audio deep dive: `nlm audio create "$NB" --format deep_dive --length long --confirm`
- Report: `nlm report create "$NB" --format "Study Guide" --confirm`
- Quiz / Flashcards / Mindmap: standard commands.

## Poller pattern (download as artifacts complete)
A background bash loop every 60s: for each profile/notebook, `nlm studio status
--json`, and for any artifact whose id is in a known map AND status=="completed"
AND output file not yet present, run `nlm download <subcmd> "$NB" --id <id>
--output <file>`. CRITICAL: subcommand is `slide-deck` (HYPHEN), not
`slide_deck`. Map artifact id -> "slide-deck:/path.pdf". If a stale wrong
version already exists, `rm` it first or the poller skips re-download.

## Rich visuals (user expectation)
NotebookLM PDFs are plain. For ANIME / KIDS / richer visuals, render via
HyperFrames + animejs (separate skill set): NLM = content layer, HyperFrames =
visual layer. Scaffold with `npx hyperframes init dsa-anime --example
kinetic-type --non-interactive`; author composition HTML with anime.js motion
registered on `window.__hfAnime`; `npx hyperframes render` to MP4.
