# Pitch Deck Video Creation with NLM CLI

## Overview

Create **3-minute pitch deck videos** using **Google NotebookLM** (`nlm` CLI) with a **narrative-first methodology**. This skill adapts the proven pitch-deck-nlm methodology for **video output** — showing screen progressions, product walkthroughs, and value demonstrations with professional narration.

**Key Principle:** Script before screens, story before video, meaning before visuals.

---

## ⚠️ CRITICAL: The 30-Second Test

**Most Important Check:** If you stop the video at 30 seconds, does an investor/viewer understand:
1. What problem you're solving
2. Who it affects
3. Why it matters

If not, rewrite the script.

---

## Six Thinking Hats Committee (Autonomous Question Generation)

Same as pitch-deck-nlm. Generate 60-80 questions across all 6 hats:

| Hat | Role | Video Focus |
|-----|------|-------------|
| **⚪ White** | Facts & Data | Metrics to show on screen, traction numbers |
| **🔴 Red** | Emotions & Story | Hook that makes viewers care in first 5 seconds |
| **⚫ Black** | Caution & Risk | What kills the company, how video addresses skepticism |
| **🟡 Yellow** | Optimism & Value | The "aha" moment, why this is exciting |
| **🟢 Green** | Creativity & Alternatives | Non-obvious angles, unique differentiators |
| **🔵 Blue** | Process & Control | Video structure, pacing, what to show when |

---

## 6-Phase Creation Process (Adapted for Video)

| Phase | Name | Output | Time |
|-------|------|--------|------|
| 0 | Six Hats Interview | Q&A transcript | 15 min |
| 1 | Foundation | Business audit + value proposition | 10 min |
| 2 | Video Script | Timed narration with screen cues | 15 min |
| 3 | Objections | Burning questions + video responses | 10 min |
| 4 | Screen Flow Brief | Screenshot-to-timestamp mapping | 10 min |
| 5 | NLM Video | Generated video via `nlm video create` | 5-10 min |

---

## Phase 0: Six Hats Interview

Same as pitch-deck-nlm. Create or use existing notebook, generate questions, get founder answers.

```bash
# If starting fresh:
nlm notebook create "Six Hats Interview - {Product Name}"

# Query for Six Hats questions:
nlm notebook query <notebook_id> "Generate 60-80 questions across all 6 Thinking Hats for a product pitch video. Focus on what should be shown on screen and what should be narrated."
```

---

## Phase 1: Foundation

Query notebook for business audit tailored to video:

```bash
nlm notebook query <notebook_id> "Act as a product video strategist.

Create a foundation document with:

**1. Core Value Proposition** (1 sentence)
What does this product do and for whom?

**2. The Pain Point** (what viewers should feel)
What's the daily frustration or cost of not having this?

**3. The Transformation** (before → after)
What changes when someone uses this product?

**4. Proof Points** (evidence to show on screen)
- Metrics, user count, growth
- Specific features that prove the claim
- Screenshots/demos that validate

**5. Target Viewer**
Who is this video for? What do they care about most?

Output: Structured foundation document for video script development."
```

---

## Phase 2: Video Script (Timed Narration)

**This is the core phase.** Unlike slides (which have headlines), videos have **timed script segments** mapped to visual moments.

```bash
nlm notebook query <notebook_id> "Act as a video scriptwriter creating a 3-minute product pitch video.

Create a TIMED video script with the following structure:

**TIMING BREAKDOWN (180 seconds total):**

| Section | Duration | Purpose |
|---------|----------|---------|
| Hook | 0-15s | Grab attention, state the problem |
| Problem | 15-35s | Show the pain (before state) |
| Solution Reveal | 35-55s | Introduce the product |
| Screen Walkthrough | 55-120s | Show key screens/features (3-5 screens) |
| Value/Proof | 120-150s | Metrics, results, social proof |
| Vision | 150-165s | Where this is going |
| Call to Action | 165-180s | What viewer should do next |

**Script Format (REQUIRED):**

### HOOK (0-15s)
**Narration:** [exact words to be spoken]
**Visual:** [what's on screen — screenshot, animation, text overlay]

### PROBLEM (15-35s)
**Narration:** [...]
**Visual:** [...]

### SOLUTION REVEAL (35-55s)
**Narration:** [...]
**Visual:** [...]

### SCREEN WALKTHROUGH (55-120s)
**Screen 1:** [name] — [duration]
  Narration: [...]
  Visual: [screenshot path or description, what to highlight]
  
**Screen 2:** [name] — [duration]
  Narration: [...]
  Visual: [...]

[Continue for 3-5 screens]

### VALUE/PROOF (120-150s)
**Narration:** [...]
**Visual:** [metrics, numbers on screen, testimonials]

### VISION (150-165s)
**Narration:** [...]
**Visual:** [...]

### CALL TO ACTION (165-180s)
**Narration:** [...]
**Visual:** [...]

**Script Rules:**
1. Narration should be ~2.5 words per second (natural pace)
2. Each section must have BOTH narration AND visual description
3. Screen walkthrough sections must reference ACTUAL screenshots
4. Show, don't tell — if claiming "fast grading", SHOW the grading screen
5. One message per section — don't cram multiple points together

Output: Complete timed video script with narration and visual cues."
```

---

## Phase 3: Objections (Video Stress-Test)

Same as pitch-deck-nlm but adapted for video flow:

```bash
nlm notebook query <notebook_id> "Act as a skeptical viewer watching this 3-minute pitch video.

Generate the top 10 burning questions and check if the video answers them:

For each question:
1. What would a skeptical viewer ask?
2. Does the current script answer it? (Yes/No)
3. If No, which section should address it and how?

Focus on:
- Does the Hook grab attention? (or is it generic?)
- Does the walkthrough show real value or just features?
- Are claims backed by visible proof?
- Is the CTA clear?

Output: Gap analysis with recommended script additions."
```

---

## Phase 4: Screen Flow Brief

**Unique to video.** Maps screenshots to video timestamps with specific instructions.

```bash
nlm notebook query <notebook_id> "Act as a video editor creating a screen flow plan.

Create a screen flow brief mapping screenshots to video timestamps:

**For Each Screen:**

| # | Screen Name | Timestamp | Duration | Visual Focus | Zoom/Highlight |
|---|-------------|-----------|----------|--------------|----------------|
| 1 | Login | 0:35-0:40 | 5s | Clean UI | Center on form |
| 2 | Dashboard | 0:40-0:50 | 10s | Key metrics | Zoom on stat cards |
| ... | ... | ... | ... | ... | ... |

**Screen Selection Rules:**
1. Maximum 5-7 screens in 65 seconds (walkthrough section)
2. Each screen must demonstrate a CLEAR value proposition
3. Order should follow natural user workflow
4. Skip screens that look similar or don't add new information
5. For each screen, identify 1-2 UI elements to highlight/zoom on

**Visual Consistency:**
- All screens should have consistent sizing
- Smooth transitions (fade or slide)
- Brief pause (0.5s) on each screen before narration starts
- Text callouts for key features (max 6 words each)

Output: Screen flow brief with timestamp mapping and visual instructions."
```

---

## Phase 5: NLM Video Generation

### Step 1: Prepare Notebook

Ensure all sources are added (PDF with screens, design docs, script, screen flow brief):

```bash
# Add script as source
nlm source add <notebook_id> --text "[paste the complete video script from Phase 2]"

# Add screen flow brief as source
nlm source add <notebook_id> --text "[paste the screen flow brief from Phase 4]"

# If not already added, add the PDF/screenshots
nlm source add <notebook_id> --file /path/to/screens.pdf
```

### Step 2: Generate Video

```bash
nlm video create <notebook_id> \
  --format explainer \
  --style auto_select \
  --focus "[PASTE THE PROMPT BELOW]" \
  --confirm
```

**Video Generation Prompt Template:**

```
Create a 3-minute pitch video for {Product Name}:

**PRODUCT:** [one-liner]

**NARRATIVE:** [30-second summary]

**KEY SCREENS TO SHOW (in order):**
1. [Screen name] — demonstrates [value]
2. [Screen name] — demonstrates [value]
3. [Screen name] — demonstrates [value]
[... up to 7 screens]

**VIDEO STRUCTURE:**
- 0-15s: Hook — [hook statement]
- 15-35s: Problem — [pain description]
- 35-55s: Solution — [solution reveal]
- 55-120s: Walkthrough — show screens demonstrating workflow
- 120-150s: Proof — [metrics, results]
- 150-165s: Vision — [future outlook]
- 165-180s: CTA — [what to do next]

**STYLE REQUIREments:**
- Each screen should be clearly visible with enough time to read
- Smooth transitions between screens
- Professional, modern aesthetic
- Text overlays for key metrics (big, bold numbers)
- Focus on demonstrating value, not just showing features

Generate a video that an investor or buyer would watch fully without skipping.
```

### Step 3: Download

```bash
nlm download video <notebook_id> -o pitch_video.mp4
```

---

## Anti-BS Enforcement (Video-Specific)

1. ❌ **No feature dumps** — Every screen shown must demonstrate a CLEAR value
2. ❌ **No vague claims without proof** — "Save hours" → show the screen where hours are saved
3. ❌ **No generic hooks** — First 5 seconds must be specific and attention-grabbing
4. ❌ **No screens without narration** — Every visual moment should advance the story
5. ❌ **No metric claims without visible numbers** — If saying "10K users," show it on screen
6. ❌ **No jargon** — Explain concepts a non-technical viewer understands
7. ❌ **No rushed walkthroughs** — Each screen gets minimum 8-10 seconds
8. ❌ **No generic CTAs** — Specific next step, not "learn more"
9. ❌ **No music-only sections** — Narration drives the story throughout
10. ❌ **No logo parade** — Don't waste time showing logos, show real work

---

## Quality Checklist

Before delivering the video, verify:

**30-Second Test:**
- [ ] First 30 seconds clearly state problem and why it matters

**Screen Coverage:**
- [ ] Each screen shown has a clear value demonstration
- [ ] Screens follow natural workflow order
- [ ] No redundant or similar-looking screens

**Narration Quality:**
- [ ] ~2.5 words per second pace (natural speaking)
- [ ] Every section has both narration AND visual description
- [ ] Claims are backed by visible proof on screen

**Video Structure:**
- [ ] Hook → Problem → Solution → Walkthrough → Proof → Vision → CTA
- [ ] Total duration 2:45-3:15 (acceptable range)
- [ ] Smooth transitions between sections

**Anti-BS Check:**
- [ ] No feature dumps without value context
- [ ] No vague claims without proof
- [ ] Metrics shown, not just stated

---

## Integration with Pitch-Deck-NLM Skill

This skill works alongside:
- **pitch-deck-nlm**: Use that for slide decks (PPTX/PDF), use this for videos
- **anime-slidedecks**: For kid-friendly anime video styles (set `--style anime`)
- **nlm-productivity**: Base skill for nlm CLI commands

**When to use which:**
- **Investor meeting tomorrow?** → pitch-deck-nlm (slides)
- **Social media/product launch?** → pitch-deck-video-nlm (video)
- **Both?** → Do slides first, then create video from the same notebook

---

**Skill Version**: 1.0
**Dependencies**: nlm CLI v0.4.8+, authenticated Google NotebookLM account
**Output Format**: MP4 video (2:45-3:15 duration)
**Methodology**: Narrative-first, Six Thinking Hats, Screen Flow mapping, Anti-BS enforcement
**Target Audience**: Investors, buyers, stakeholders, product launch viewers
