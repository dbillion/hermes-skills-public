---
name: stitch-design-pipeline
description: >
  End-to-end design pipeline using Google Stitch MCP for UI generation, taste-skill for
  design system quality, and Serper for design inspiration. Use when the user wants to
  generate UI designs, create design systems, produce landing pages or app screens, or
  convert design intent into production HTML. Covers the full flow: inspiration →
  DESIGN.md → Stitch project → screen generation → asset download → taste implementation.
triggers:
  - design pipeline
  - generate screens
  - stitch generation
  - landing page design
  - UI design system
  - design to code
  - generate landing page
  - generate app screens
---

# Stitch Design Pipeline

End-to-end pipeline for generating production UI designs using Google Stitch MCP,
taste-skill quality enforcement, and Serper design inspiration search.

## Pipeline Overview

```
Inspiration → DESIGN.md → Stitch Project + Design System → Screen Generation → Download HTML/PNG → Taste Implementation
```

## Phase 1: Design Inspiration

Use Serper API (via design-inspiration MCP or direct curl) to find reference designs:

```bash
curl -s -X POST "https://google.serper.dev/images" \
  -H "X-API-KEY: $SERPER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q": "CRM landing page design site:dribbble.com", "num": 10}'
```

**Key design platforms to reference:** Dribbble, Behance, Awwwards, SaaS landing page galleries.

**Extract tokens from live sites:**
```bash
curl -s -X POST "https://google.serper.dev/scrape" \
  -H "X-API-KEY: $SERPER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://close.com", "include": "colors,fonts,layout"}'
```

## Phase 2: DESIGN.md Creation

Create a taste-informed DESIGN.md with these required sections:

1. **Visual Theme & Atmosphere** - Mood, density (1-10), variance (1-10), motion (1-10)
2. **Color Palette & Roles** - Primary foundation, accent (max 1), functional states, with hex codes
3. **Typography Rules** - Font families, hierarchy, banned fonts (Inter for premium, generic serifs)
4. **Component Stylings** - Buttons, cards, inputs, loaders, empty states
5. **Layout Principles** - Grid, max-width, responsive strategy, spacing scale
6. **Motion & Interaction** - Spring physics, stagger rules, performance constraints
7. **Anti-Patterns** - Explicit banned list (emojis, Inter, pure black, neon glows, 3-column equal cards)

**Banned patterns (taste-skill enforced):**
- No emojis, no Inter font, no pure black (#000000), no neon/outer glows
- No purple/blue neon gradients, no 3-column equal feature cards
- No generic placeholder names ("John Doe", "Acme")
- No AI copywriting cliches ("Elevate", "Seamless", "Unleash")
- No scroll cues, no decorative status dots, no version labels

## Phase 3: Stitch MCP Setup

### API Configuration

Stitch exposes an HTTP MCP server. All calls are POST to a single endpoint:

```
POST https://stitch.googleapis.com/mcp
Headers: X-Goog-Api-Key: <key>, Content-Type: application/json
Format: JSON-RPC 2.0 (method: "tools/call")
```

### Tool Call Pattern

```bash
# Write payload to temp file to avoid shell escaping issues
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"<tool>","arguments":{...}}}' > /tmp/stitch_req.json

curl -s -X POST "https://stitch.googleapis.com/mcp" \
  -H "X-Goog-Api-Key: $STITCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/stitch_req.json
```

### Workflow Steps

1. **Create project:** `{"name":"create_project","arguments":{"title":"Project Name"}}`
   - Returns: `{"name":"projects/12345",...}`

2. **Upload DESIGN.md:** `{"name":"upload_design_md","arguments":{"projectId":"projects/...","designMdBase64":"<b64>"}}`
   - Returns: `{"id":"...","sourceScreen":"projects/.../screens/..."}`

3. **Create design system:** `{"name":"create_design_system_from_design_md","arguments":{"projectId":"...","selectedScreenInstance":{"id":"<id>","sourceScreen":"projects/.../screens/..."}}}`
   - Returns: `{"assetId":"<uuid>"}` — use as `designSystem` in generation

4. **Generate screens:** `{"name":"generate_screen_from_text","arguments":{"projectId":"...","designSystem":"assets/<uuid>","deviceType":"DESKTOP","prompt":"..."}}`
   - Takes 60-120 seconds per call
   - Generate sequentially, not in parallel

5. **Parse response:** JSON string in `result.content[0].text` → parse → `outputComponents[0].design.screens[0].screenshot.downloadUrl` and `.htmlCode.downloadUrl`

## Phase 4: Screen Generation Prompts

### Landing Page Template
```
[Product Name] landing page - [descriptor]

Inspired by [reference site 1]'s [element], [reference site 2]'s [element].

PLATFORM: Web, Desktop-first

PAGE STRUCTURE:
1. Sticky Navigation: Logo left, nav center, CTA right
2. Hero Section: [Asymmetric/Left-aligned per taste variance > 4], eyebrow label, headline, subtext, primary CTA, [product preview/mockup]
3. Social Proof Bar: [Logo wordmarks, no labels]
4. Features Section: [Asymmetric grid, never 3-equal-cards]
5. How It Works: [Numbered steps with connecting lines]
6. Metrics Section: [Bold numbers in mono]
7. Pricing Section: [Plan cards, one elevated with accent]
8. CTA Section: [Clean, single primary CTA]
9. Footer: [4 columns]
```

### App Screen Template
```
[App Name] [screen name] page. Left sidebar with [item] active. Main area: [top bar actions]. Below: [data layout with specific columns and components]. [Additional details].
```

**Critical:** Never include hex codes, font names, or color roles in generation prompts — the design system handles all visual styling.

## Phase 5: Download & Implementation

```bash
# Download generated assets
curl -sL -o ".stitch/designs/{name}.png" "$SCREENSHOT_URL"
curl -sL -o ".stitch/designs/{name}.html" "$HTML_URL"
```

Typical file sizes: PNG 35-65KB, HTML 20-28KB per screen.

## Phase 6: Mermaid Diagram Rendering

For design docs (ER diagrams, BPMN flows, C4 architecture):

```bash
# Install mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Render diagrams to PNG
mmdc -i diagram.mmd -o diagram.png -b white -w 1600 -s 2
```

## Common Pitfalls

1. **Shell escaping:** Always write JSON payload to temp file (`> /tmp/stitch_req.json`) then `curl -d @/tmp/stitch_req.json`
2. **Timing:** Each generation takes 60-120s. Use timeout=180. Sequential only.
3. **DESIGN.md size:** Keep under ~10KB for base64 upload. Truncate if needed.
4. **Response parsing:** The text field contains a JSON string that needs double-parsing (first the RPC response, then the text content).
5. **Port conflicts:** When running local dev alongside other Docker containers, check port availability before assigning.
6. **Kamal accessories:** For production, use Kamal's accessory system for DB/Redis, not docker-compose. docker-compose is for local dev only.
7. **Design before code:** Always complete C4 diagrams, ER diagrams, and BPMN flows before writing any application code.
