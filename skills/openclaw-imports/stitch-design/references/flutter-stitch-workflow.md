# Flutter + Stitch End-to-End Workflow

## Pattern: Stitch Design → Flutter Build → Visual Verification

Built from the TargetRun courier driver goal calculator session.

---

## Phase 1: Stitch Design Generation

### Direct HTTP MCP (when mcp-cli fails)

mcp-cli can fail on Stitch schema refs (ScreenInstance). Use direct JSON-RPC.

### Tool sequence

1. create_project(title) -> get projects/<id>
2. generate_screen_from_text(projectId=<numeric_id>, prompt, deviceType=MOBILE)
   -> Parse screen ID from response: re.search(r'screens/([a-f0-9]+)', text)
3. get_screen(name=projects/<pid>/screens/<sid>, projectId=<pid>, screenId=<sid>)
   -> structuredContent.screenshot.downloadUrl -> full PNG
   -> structuredContent.htmlCode.downloadUrl -> HTML export

### Gotchas

- generate_screen_from_text takes 2-3 min. Use timeout=180.
- list_screens returns empty immediately after generation.
- get_screen requires ALL THREE fields despite two being deprecated.
- No download_screen_image/download_screen_html tools. Use get_screen URLs.
- projectId param = numeric only (e.g. 5830850240073423544). name field = full resource path.
- create_project must be called via tools/call, NOT as direct method.

---

## Phase 2: Flutter Build

### Setup

    export PATH="/path/to/flutter/bin:$PATH"
    flutter create project_name
    flutter pub add sqflite shared_preferences path_provider path fl_chart http intl

### Design system verification

    grep -rn "0xFF1F6FEB|0xFF0B1F3A|0xFFEAF2FF|0xFF12B76A|0xFFF79009" lib/

Use .withValues(alpha: ...) NOT .withOpacity() (deprecated in Flutter 3.45+).

### Screenshot verification

    flutter build web --release
    cd build/web && python3 -m http.server 8085
    chromium --headless --disable-gpu \
      --screenshot=/tmp/mobile.png --window-size=390,844 \
      --virtual-time-budget=10000 http://localhost:8085/index.html

Flutter WASM needs --virtual-time-budget >= 10000. Lightpanda cannot render it.

---

## Phase 3: Persistence

Dual-layer: SQLite (mobile/desktop) + SharedPreferences (web fallback).
Add actualHours/actualEarnings to Goal model. Use onUpgrade for schema migrations.
Always save to both layers; catch SQLite errors on web.

---

## Phase 4: Charts (fl_chart)

- LineChart: Earnings over time (actual vs target dashed line)
- BarChart: Daily completion rate (green >= 100%, amber >= 50%, red < 50%)
- LineChart: Planned vs actual hours

---

## Phase 5: Weather (Open-Meteo)

Free, no API key needed.
WMO codes: 0=clear, 1-3=cloudy, 51-55=drizzle, 61-65=rain, 71-75=snow, 80-82=showers, 95+=thunderstorm.