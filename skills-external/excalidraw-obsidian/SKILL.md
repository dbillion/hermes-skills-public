---
name: excalidraw-obsidian
description: Professional Excalidraw diagram creation and editing for Obsidian using MCP server integration. Create beautiful hand-drawn style diagrams, architecture diagrams, flowcharts, mind maps, and visual notes directly in Obsidian vault.
---

# Excalidraw-Obsidian Skill

Create professional Excalidraw diagrams in Obsidian using MCP server integration. This skill provides token-efficient diagram generation with beautiful hand-drawn aesthetics.

## Quick Start

```bash
# 1. Install Excalidraw MCP server (if not already installed)
cd /path/to/excalidraw-mcp-app && npm install && npm run build

# 2. Add to MCP config (~/.config/Claude/claude_desktop_config.json)
{
  "mcpServers": {
    "excalidraw": {
      "command": "node",
      "args": ["/path/to/excalidraw-mcp-app/dist/index.js", "--stdio"]
    }
  }
}

# 3. Use the skill
# Invoke this skill and ask: "Create an architecture diagram for my microservices"
```

## Installation

### Option 1: Use Existing Excalidraw MCP App

```bash
# Clone and build
git clone https://github.com/antonpk1/excalidraw-mcp-app.git
cd excalidraw-mcp-app
pnpm install && pnpm run build

# Configure VSCode
./configure-vscode.sh

# Or configure Claude Desktop manually
# Add to ~/Library/Application Support/Claude/claude_desktop_config.json:
{
  "mcpServers": {
    "excalidraw": {
      "command": "node",
      "args": ["/absolute/path/to/excalidraw-mcp-app/dist/index.js", "--stdio"]
    }
  }
}
```

### Option 2: Use Alternative Excalidraw MCP Server

```bash
# Alternative: lesleslie/excalidraw-mcp (Python + Node.js)
git clone https://github.com/lesleslie/excalidraw-mcp.git
cd excalidraw-mcp
uv sync
npm install
npm run build

# Start server
uv run python excalidraw_mcp/server.py
```

### Option 3: Install from npm

```bash
# @yama662607/obsidian-excalidraw-mcp (Obsidian-specific)
npm install -g @yama662607/obsidian-excalidraw-mcp

# excalidraw-mcp-server (feature-rich)
npm install -g excalidraw-mcp-server
```

## Configuration

### MCP Config Location

| Platform | Config Path |
|----------|-------------|
| **Claude Desktop (Linux)** | `~/.config/Claude/claude_desktop_config.json` |
| **Claude Desktop (Mac)** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Desktop (Windows)** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **VSCode** | `.vscode/mcp.json` (workspace) or `~/Library/Application Support/Code/User/mcp.json` |
| **mcp-cli** | `~/.config/mcp-cli/mcp_servers.json` |

### Complete Configuration Example

```json
{
  "mcpServers": {
    "excalidraw": {
      "command": "node",
      "args": ["/home/deeone/picoclaw/excalidraw-mcp-app/excalidraw-mcp-app/dist/index.js", "--stdio"],
      "env": {
        "PORT": "3001",
        "HOST": "localhost",
        "DEBUG": "false"
      }
    },
    "obsidian": {
      "command": "obsidian",
      "args": []
    }
  }
}
```

## Available MCP Tools

### From excalidraw-mcp-app

| Tool | Description | Parameters |
|------|-------------|------------|
| `read_me` | Get element format reference | None |
| `create_view` | Render diagram with elements | `elements` (JSON array string) |
| `export_to_excalidraw` | Export to Excalidraw JSON | `json` (JSON string) |
| `save_checkpoint` | Save diagram state | `id`, `data` |
| `read_checkpoint` | Restore diagram state | `id` |

### From excalidraw-mcp-server

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_canvas_info` | Get canvas state | None |
| `generate_excalidraw` | Generate from prompt | `prompt` |
| `generate_excalidraw_from_graph` | Generate from graph | `graph` |
| `set_canvas_document` | Set document | `document` |
| `validate_excalidraw` | Validate JSON | `json` |

### From lesleslie/excalidraw-mcp

| Category | Tools |
|----------|-------|
| **Elements** | `create_element`, `update_element`, `delete_element`, `query_elements` |
| **Batch** | `batch_create_elements` |
| **Organization** | `group_elements`, `ungroup_elements`, `align_elements`, `distribute_elements` |
| **Locking** | `lock_elements`, `unlock_elements` |
| **Resources** | `get_resource` (scene, library, theme) |

## Usage Examples

### Example 1: Create Architecture Diagram

```bash
# Using mcp-cli
mcp-cli --config ~/.config/mcp-cli/mcp_servers.json \
  call excalidraw create_view \
  '{"elements": "[{\"type\":\"rectangle\",\"id\":\"api\",\"x\":100,\"y\":100,\"width\":200,\"height\":80,\"label\":{\"text\":\"API Gateway\"}},{\"type\":\"rectangle\",\"id\":\"db\",\"x\":400,\"y\":100,\"width\":200,\"height\":80,\"label\":{\"text\":\"Database\"}},{\"type\":\"arrow\",\"id\":\"a1\",\"x\":300,\"y\":140,\"width\":100,\"height\":0,\"points\":[[0,0],[100,0]],\"endArrowhead\":\"arrow\"}]"}'
```

### Example 2: Generate from Prompt

```bash
# Using generate_excalidraw tool
mcp-cli call excalidraw generate_excalidraw \
  '{"prompt": "Create a microservices architecture diagram showing: User -> Load Balancer -> API Gateway -> [Auth Service, User Service, Order Service] -> Database"}'
```

### Example 3: Create Flowchart

```python
# Python script for complex flowchart
import json
import subprocess

elements = [
    {"type": "rectangle", "id": "start", "x": 350, "y": 50, "width": 100, "height": 60, 
     "label": {"text": "Start", "fontSize": 16}, "backgroundColor": "#b2f2bb"},
    {"type": "diamond", "id": "decision", "x": 350, "y": 150, "width": 100, "height": 100,
     "label": {"text": "Valid?", "fontSize": 14}, "backgroundColor": "#fff3bf"},
    {"type": "rectangle", "id": "process", "x": 350, "y": 300, "width": 100, "height": 60,
     "label": {"text": "Process", "fontSize": 16}, "backgroundColor": "#a5d8ff"},
    {"type": "rectangle", "id": "error", "x": 500, "y": 170, "width": 100, "height": 60,
     "label": {"text": "Error", "fontSize": 14}, "backgroundColor": "#ffc9c9"},
    {"type": "arrow", "id": "a1", "x": 400, "y": 110, "width": 0, "height": 40,
     "points": [[0,0],[0,40]], "endArrowhead": "arrow"},
    {"type": "arrow", "id": "a2", "x": 400, "y": 250, "width": 0, "height": 50,
     "points": [[0,0],[0,50]], "endArrowhead": "arrow"},
    {"type": "arrow", "id": "a3", "x": 450, "y": 200, "width": 50, "height": 0,
     "points": [[0,0],[50,0]], "endArrowhead": "arrow"},
]

cmd = [
    "mcp-cli", "call", "excalidraw", "create_view",
    json.dumps({"elements": json.dumps(elements)})
]
subprocess.run(cmd)
```

### Example 4: Create Mind Map

```json
{
  "elements": [
    {"type": "ellipse", "id": "central", "x": 400, "y": 300, "width": 200, "height": 100,
     "label": {"text": "Central Topic", "fontSize": 20}, "backgroundColor": "#d0bfff"},
    {"type": "ellipse", "id": "branch1", "x": 100, "y": 150, "width": 150, "height": 80,
     "label": {"text": "Branch 1", "fontSize": 16}, "backgroundColor": "#a5d8ff"},
    {"type": "ellipse", "id": "branch2", "x": 700, "y": 150, "width": 150, "height": 80,
     "label": {"text": "Branch 2", "fontSize": 16}, "backgroundColor": "#b2f2bb"},
    {"type": "ellipse", "id": "branch3", "x": 400, "y": 500, "width": 150, "height": 80,
     "label": {"text": "Branch 3", "fontSize": 16}, "backgroundColor": "#ffd8a8"},
    {"type": "arrow", "id": "line1", "x": 400, "y": 300, "width": 0, "height": 0,
     "points": [[0,0],[-200,-100]], "strokeWidth": 3},
    {"type": "arrow", "id": "line2", "x": 400, "y": 300, "width": 0, "height": 0,
     "points": [[0,0],[200,-100]], "strokeWidth": 3},
    {"type": "arrow", "id": "line3", "x": 400, "y": 300, "width": 0, "height": 0,
     "points": [[0,0],[0,150]], "strokeWidth": 3}
  ]
}
```

### Example 5: Sequence Diagram

```json
{
  "elements": [
    {"type": "rectangle", "id": "user", "x": 50, "y": 80, "width": 100, "height": 40,
     "label": {"text": "User", "fontSize": 16}, "backgroundColor": "#a5d8ff"},
    {"type": "rectangle", "id": "api", "x": 250, "y": 80, "width": 120, "height": 40,
     "label": {"text": "API Gateway", "fontSize": 16}, "backgroundColor": "#ffd8a8"},
    {"type": "rectangle", "id": "service", "x": 450, "y": 80, "width": 120, "height": 40,
     "label": {"text": "Service", "fontSize": 16}, "backgroundColor": "#b2f2bb"},
    {"type": "rectangle", "id": "db", "x": 650, "y": 80, "width": 100, "height": 40,
     "label": {"text": "Database", "fontSize": 16}, "backgroundColor": "#ffc9c9"},
    {"type": "arrow", "id": "lifeline1", "x": 100, "y": 120, "width": 0, "height": 300,
     "points": [[0,0],[0,300]], "strokeStyle": "dashed"},
    {"type": "arrow", "id": "lifeline2", "x": 310, "y": 120, "width": 0, "height": 300,
     "points": [[0,0],[0,300]], "strokeStyle": "dashed"},
    {"type": "arrow", "id": "lifeline3", "x": 510, "y": 120, "width": 0, "height": 300,
     "points": [[0,0],[0,300]], "strokeStyle": "dashed"},
    {"type": "arrow", "id": "lifeline4", "x": 700, "y": 120, "width": 0, "height": 300,
     "points": [[0,0],[0,300]], "strokeStyle": "dashed"},
    {"type": "arrow", "id": "msg1", "x": 100, "y": 180, "width": 210, "height": 0,
     "points": [[0,0],[210,0]], "endArrowhead": "arrow",
     "label": {"text": "POST /users", "fontSize": 12}},
    {"type": "arrow", "id": "msg2", "x": 310, "y": 230, "width": 200, "height": 0,
     "points": [[0,0],[200,0]], "endArrowhead": "arrow",
     "label": {"text": "SELECT *", "fontSize": 12}},
    {"type": "arrow", "id": "msg3", "x": 700, "y": 280, "width": -390, "height": 0,
     "points": [[0,0],[-390,0]], "endArrowhead": "arrow", "strokeStyle": "dashed",
     "label": {"text": "results", "fontSize": 12}},
    {"type": "arrow", "id": "msg4", "x": 310, "y": 330, "width": -210, "height": 0,
     "points": [[0,0],[-210,0]], "endArrowhead": "arrow", "strokeStyle": "dashed",
     "label": {"text": "200 OK", "fontSize": 12}}
  ]
}
```

## Excalidraw Element Format

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Element type (rectangle, ellipse, diamond, arrow, text, line) |
| `id` | string | Unique identifier |
| `x` | number | X position (pixels) |
| `y` | number | Y position (pixels) |
| `width` | number | Width (pixels) |
| `height` | number | Height (pixels) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `backgroundColor` | string | `transparent` | Fill color (hex or preset) |
| `strokeColor` | string | `#1e1e1e` | Stroke color |
| `strokeWidth` | number | 2 | Stroke width (1-4) |
| `fillStyle` | string | `hachure` | `hachure`, `solid`, `cross-hatch` |
| `roughness` | number | 1 | Roughness (0-2) |
| `angle` | number | 0 | Rotation in radians |
| `label` | object | null | `{text: string, fontSize: number}` |
| `points` | array | null | Arrow control points `[[x1,y1],[x2,y2]]` |
| `endArrowhead` | string | `arrow` | `null`, `arrow`, `bar`, `dot`, `triangle` |
| `startArrowhead` | string | `null` | Same as endArrowhead |
| `strokeStyle` | string | `solid` | `solid`, `dashed`, `dotted` |
| `roundness` | object | null | `{type: 3}` for rounded corners |
| `opacity` | number | 100 | Opacity percentage |
| `fontSize` | number | 16 | Font size for text |
| `fontFamily` | number | 1 | 1=Sans, 2=Serif, 3=Monospace |
| `textAlign` | string | `left` | `left`, `center`, `right` |

### Color Palette

#### Primary Colors
| Name | Hex | Use |
|------|-----|-----|
| Blue | `#4a9eed` | Primary actions, links |
| Amber | `#f59e0b` | Warnings, highlights |
| Green | `#22c55e` | Success, positive |
| Red | `#ef4444` | Errors, negative |
| Purple | `#8b5cf6` | Accents, special items |
| Pink | `#ec4899` | Decorative |
| Cyan | `#06b6d4` | Info, secondary |
| Lime | `#84cc16` | Extra |

#### Excalidraw Fills (Pastel)
| Color | Hex | Good For |
|-------|-----|----------|
| Light Blue | `#a5d8ff` | Input, sources, primary nodes |
| Light Green | `#b2f2bb` | Success, output, completed |
| Light Orange | `#ffd8a8` | Warning, pending, external |
| Light Purple | `#d0bfff` | Processing, middleware |
| Light Red | `#ffc9c9` | Error, critical, alerts |
| Light Yellow | `#fff3bf` | Notes, decisions |
| Light Teal | `#c3fae8` | Storage, data, memory |
| Light Pink | `#eebefa` | Analytics, metrics |

## Obsidian Integration

### Creating Excalidraw Files

Excalidraw files in Obsidian use this format:

```markdown
---

excalidraw-plugin: parsed
tags: [excalidraw, diagram]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==


# Excalidraw Data

## Text Elements
%%
## Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [...],
  "appState": {"viewBackgroundColor": "#ffffff"}
}
```
%%
```

### Using Obsidian CLI with Excalidraw

```bash
# Create new Excalidraw note
obsidian create name="Architecture Diagram" \
  --template excalidraw \
  vault="My Vault"

# Search for Excalidraw files
obsidian search query="tag:excalidraw" vault="My Vault"

# Open Excalidraw file
obsidian open file="Architecture Diagram" vault="My Vault"
```

### Workflow: Create Diagram in Obsidian

1. **Generate diagram with MCP:**
   ```bash
   mcp-cli call excalidraw create_view '{"elements": "..."}'
   ```

2. **Get JSON output and format for Obsidian**

3. **Create Obsidian note:**
   ```bash
   obsidian create name="My Diagram" content="[Excalidraw markdown wrapper]"
   ```

4. **Open in Obsidian:**
   ```bash
   obsidian open file="My Diagram"
   ```

5. **Switch to Excalidraw View** in Obsidian

## Token-Saving Patterns

### Pattern 1: Use MCP Instead of AI CLI

```bash
# Bad: Costs tokens
# gemini "create a diagram showing microservices architecture"

# Good: Zero tokens to AI CLI
mcp-cli call excalidraw generate_excalidraw \
  '{"prompt": "microservices architecture"}'
```

### Pattern 2: Template Reuse

```bash
# Create template once
cat > /tmp/diagram-template.json << 'EOF'
{
  "elements": [
    {"type": "rectangle", "id": "box1", "x": 100, "y": 100, "width": 200, "height": 80}
  ]
}
EOF

# Reuse with modifications
python3 -c "
import json
with open('/tmp/diagram-template.json') as f:
    template = json.load(f)
# Modify positions, labels, etc.
# Call MCP with modified template
"
```

### Pattern 3: Batch Operations

```bash
# Create multiple diagrams in sequence
for diagram in architecture flowchart sequence; do
  mcp-cli call excalidraw generate_excalidraw \
    "{\"prompt\": \"$diagram for e-commerce\"}"
done
```

### Pattern 4: Checkpoint System

```bash
# Save state
mcp-cli call excalidraw save_checkpoint \
  '{"id": "diagram-v1", "data": "..."}'

# Later, restore and edit
mcp-cli call excalidraw read_checkpoint \
  '{"id": "diagram-v1"}'
```

## Best Practices

### 1. Drawing Order (CRITICAL for Streaming)

```json
[
  {"type": "cameraUpdate", "width": 800, "height": 600, "x": 0, "y": 0},
  {"type": "rectangle", "id": "bg", "x": 0, "y": 0, "width": 800, "height": 600},
  {"type": "rectangle", "id": "shape1", ...},
  {"type": "text", "id": "label1", ...},
  {"type": "arrow", "id": "connector1", ...},
  {"type": "rectangle", "id": "shape2", ...}
]
```

**Order matters:**
- Array order = z-order (first = back, last = front)
- Emit progressively: background → shapes → labels → arrows
- BAD: all rectangles → all texts → all arrows
- GOOD: bg → shape1 → text1 → arrow1 → shape2 → text2

### 2. Camera Updates for Animation

```json
[
  {"type": "cameraUpdate", "width": 600, "height": 450, "x": 0, "y": 0},
  {"type": "rectangle", "id": "r1", ...},
  {"type": "cameraUpdate", "width": 600, "height": 450, "x": 100, "y": 0},
  {"type": "rectangle", "id": "r2", ...},
  {"type": "cameraUpdate", "width": 800, "height": 600, "x": 0, "y": 0}
]
```

**Camera sizes (4:3 ratio):**
- 400×300, 600×450, 800×600, 1200×900, 1600×1200

### 3. Arrow Bindings

```json
{
  "type": "arrow",
  "id": "a1",
  "startBinding": {"elementId": "r1", "fixedPoint": [1, 0.5]},
  "endBinding": {"elementId": "r2", "fixedPoint": [0, 0.5]}
}
```

**Fixed points:**
- top: `[0.5, 0]`
- bottom: `[0.5, 1]`
- left: `[0, 0.5]`
- right: `[1, 0.5]`

### 4. Labeled Shapes (PREFERRED)

```json
{
  "type": "rectangle",
  "id": "r1",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 80,
  "label": {"text": "API Gateway", "fontSize": 18}
}
```

**Benefits:**
- Text auto-centers
- Container auto-resizes
- Saves tokens vs separate text element

### 5. Dark Mode

```json
{
  "elements": [
    {"type": "rectangle", "id": "darkbg", "x": -4000, "y": -3000,
     "width": 10000, "height": 7500, "backgroundColor": "#1e1e2e",
     "fillStyle": "solid", "strokeWidth": 0},
    ...other elements
  ]
}
```

## Common Diagram Templates

### UML Class Diagram

```json
{
  "elements": [
    {"type": "rectangle", "id": "class1", "x": 100, "y": 100, "width": 250, "height": 120,
     "backgroundColor": "#a5d8ff", "label": {"text": "<<Class>>\nClassName\n---\n+ field: type\n+ method(): return", "fontSize": 14}},
    {"type": "rectangle", "id": "class2", "x": 450, "y": 100, "width": 250, "height": 120,
     "backgroundColor": "#b2f2bb", "label": {"text": "<<Class>>\nOtherClass\n---\n- data: string\n+ process(): void", "fontSize": 14}},
    {"type": "arrow", "id": "inherit", "x": 350, "y": 160, "width": 100, "height": 0,
     "points": [[0,0],[100,0]], "endArrowhead": "triangle", "strokeWidth": 2}
  ]
}
```

### ERD Diagram

```json
{
  "elements": [
    {"type": "rectangle", "id": "users", "x": 100, "y": 100, "width": 200, "height": 100,
     "backgroundColor": "#d0bfff", "label": {"text": "USERS\n---\nPK id\nusername\nemail", "fontSize": 14}},
    {"type": "rectangle", "id": "orders", "x": 400, "y": 100, "width": 200, "height": 100,
     "backgroundColor": "#ffd8a8", "label": {"text": "ORDERS\n---\nPK id\nFK user_id\ntotal", "fontSize": 14}},
    {"type": "arrow", "id": "fk", "x": 300, "y": 150, "width": 100, "height": 0,
     "points": [[0,0],[100,0]], "endArrowhead": "arrow",
     "label": {"text": "1:N", "fontSize": 12}}
  ]
}
```

### Network Diagram

```json
{
  "elements": [
    {"type": "ellipse", "id": "internet", "x": 350, "y": 50, "width": 100, "height": 80,
     "backgroundColor": "#a5d8ff", "label": {"text": "Internet", "fontSize": 16}},
    {"type": "rectangle", "id": "firewall", "x": 350, "y": 180, "width": 100, "height": 60,
     "backgroundColor": "#ffc9c9", "label": {"text": "Firewall", "fontSize": 14}},
    {"type": "rectangle", "id": "router", "x": 350, "y": 290, "width": 100, "height": 60,
     "backgroundColor": "#ffd8a8", "label": {"text": "Router", "fontSize": 14}},
    {"type": "rectangle", "id": "switch", "x": 350, "y": 400, "width": 100, "height": 60,
     "backgroundColor": "#b2f2bb", "label": {"text": "Switch", "fontSize": 14}},
    {"type": "rectangle", "id": "server1", "x": 150, "y": 500, "width": 100, "height": 60,
     "backgroundColor": "#eebefa", "label": {"text": "Server 1", "fontSize": 14}},
    {"type": "rectangle", "id": "server2", "x": 550, "y": 500, "width": 100, "height": 60,
     "backgroundColor": "#eebefa", "label": {"text": "Server 2", "fontSize": 14}},
    {"type": "arrow", "id": "line1", "x": 400, "y": 130, "width": 0, "height": 50,
     "points": [[0,0],[0,50]], "endArrowhead": "arrow"},
    {"type": "arrow", "id": "line2", "x": 400, "y": 240, "width": 0, "height": 50,
     "points": [[0,0],[0,50]], "endArrowhead": "arrow"},
    {"type": "arrow", "id": "line3", "x": 400, "y": 350, "width": 0, "height": 50,
     "points": [[0,0],[0,50]], "endArrowhead": "arrow"},
    {"type": "arrow", "id": "line4", "x": 400, "y": 460, "width": 0, "height": 0,
     "points": [[0,0],[-150,40]], "endArrowhead": "arrow"},
    {"type": "arrow", "id": "line5", "x": 400, "y": 460, "width": 0, "height": 0,
     "points": [[0,0],[150,40]], "endArrowhead": "arrow"}
  ]
}
```

## Troubleshooting

### Server Not Starting

```bash
# Check Node version
node --version  # Should be 16+

# Check if port is in use
lsof -i :3001

# Kill existing process
kill -9 $(lsof -t -i :3001)

# Restart server
```

### Elements Not Appearing

```bash
# Validate JSON
python3 -c "import json; json.load(open('elements.json'))"

# Check element IDs are unique
# Check required fields: type, id, x, y, width, height
```

### Obsidian Not Rendering

```bash
# Check file has correct frontmatter
head -10 file.excalidraw.md

# Verify excalidraw-plugin: parsed is present
# Check JSON is in ```json block
# Switch to EXCALIDRAW VIEW in Obsidian
```

### MCP Tools Not Available

```bash
# List available tools
mcp-cli info excalidraw

# Check server is running
ps aux | grep excalidraw

# Restart MCP client
```

## Integration Examples

### With Repomix

```bash
# Pack codebase
repomix --compress -o codebase.md

# Add to NotebookLM
nlm source add --file codebase.md

# Query for architecture
nlm cross query "What's the system architecture?"

# Generate diagram from answer
mcp-cli call excalidraw generate_excalidraw \
  '{"prompt": "System architecture based on codebase analysis"}'
```

### With NLM Productivity

```bash
# Research topic
nlm notebook create "System Design"
nlm source add --url https://microservices.io/patterns

# Generate report
nlm report create -o architecture-patterns.md

# Create diagram from report
mcp-cli call excalidraw generate_excalidraw \
  '{"prompt": "Microservices patterns from research"}'
```

### With Obsidian CLI

```bash
# Create diagram
mcp-cli call excalidraw create_view '{"elements": "..."}' > diagram.json

# Format for Obsidian
python3 format-for-obsidian.py diagram.json > diagram.excalidraw.md

# Create note
obsidian create name="System Architecture" \
  content="$(cat diagram.excalidraw.md)"

# Open in Obsidian
obsidian open file="System Architecture"
```

## Performance Tips

1. **Use labeled shapes** instead of separate text elements
2. **Batch create** related elements together
3. **Use checkpoints** to avoid resending full diagram
4. **Camera updates** guide attention smoothly
5. **Unique IDs** - never reuse deleted element IDs
6. **Validate JSON** before sending to MCP

## Token Savings

| Task | AI CLI Cost | MCP Cost | Savings |
|------|-------------|----------|---------|
| Generate diagram | 5,000 tokens | 0 tokens | 100% |
| Edit diagram | 3,000 tokens | 0 tokens | 100% |
| Create flowchart | 4,000 tokens | 0 tokens | 100% |
| Architecture diagram | 8,000 tokens | 0 tokens | 100% |

## References

- [Excalidraw MCP App](https://github.com/antonpk1/excalidraw-mcp-app)
- [Excalidraw MCP Server](https://github.com/seneralkan/excalidraw-mcp-server)
- [Leslie Excalidraw MCP](https://github.com/lesleslie/excalidraw-mcp)
- [Obsidian Excalidraw MCP](https://www.npmjs.com/package/@yama662607/obsidian-excalidraw-mcp)
- [JSON Canvas Spec](https://jsoncanvas.org/spec/1.0/)
- [Excalidraw Element Format](https://github.com/zsviczian/obsidian-excalidraw-plugin)

## Version

Based on excalidraw-mcp-app v0.3.2, excalidraw-mcp-server v2.0.0
