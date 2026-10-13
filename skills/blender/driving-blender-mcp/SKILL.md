---
name: driving-blender-mcp
description: Use when driving Blender via Blender MCP addon or server.
---

# Driving Blender via MCP

## Overview
Blender's "Blender MCP" addon exposes the running Blender instance over a **local TCP socket** (default `127.0.0.1:9876`). An agent can send one JSON command per connection and receive a JSON result executed on Blender's main thread. This lets an agent model, shade, light, render, and export without a native MCP client — and it is the fallback that proves the link before wiring a real MCP server.

## When to Use
- User says "Blender MCP is connected", "drive Blender", "test these blender skills", or references `blender-mcp` / `BlenderMCP`.
- You need to create/modify/inspect a 3D scene from an agent.
- You must verify a Blender MCP link is actually live (port scan + round-trip), not assume it.
- Wiring or fixing a `blender` MCP server entry in Hermes config.

**When NOT to use:** Blender is not installed/running, or the addon is not enabled (panel does not say "Running on port 9876").

## Core Protocol (the fallback that always works)
The addon is a plain TCP JSON-RPC server. Connect, send ONE JSON object `{"type": "...", "params": {...}}`, read the JSON response. No length prefix, no newline.

Always-available command types:
- `get_scene_info` → `{name, object_count, objects[], materials_count}`
- `get_object_info` (params `{"name": "Cube"}`) → location/rotation/scale/materials/mesh verts/edges/polygons/AABB
- `get_viewport_screenshot` (params `{"filepath": "/tmp/x.png", "format": "png", "max_size": 800}`) → writes a PNG
- `execute_code` (params `{"code": "..."}`) → runs arbitrary `bpy` Python in `{"bpy": bpy}` namespace, returns captured stdout; **powerful and destructive**

Conditional handlers (only if enabled in the scene flags): Poly Haven, Hyper3D Rodin, Sketchfab.

Reusable client: `scripts/bmcp.py` — `python3 bmcp.py '{"type":"get_scene_info"}'`. Full command/param reference and the curated skill-pack repo list: `references/protocol-and-skills.md`.

## Verification Discipline (MANDATORY before claiming success)
1. **Probe the port** before trusting any "it's connected" claim:
   `python3 -c "import socket;s=socket.socket();s.settimeout(1);s.connect(('127.0.0.1',9876));print('OPEN')"`
2. **Read-only proof first:** `get_scene_info` must return real scene data.
3. **Write → verify → cleanup:** create an object with a unique name (e.g. `HermesTestSphere`), confirm `object_count` changed via `get_scene_info`, then delete it and re-confirm the count returned to baseline. Leave the user's scene exactly as found.
4. **Scene graph beats screenshots.** If a rendered image or vision read contradicts `get_scene_info`/`bpy.data.objects`, trust the scene graph — a vision model mis-saw a phantom pyramid in a viewport screenshot during testing; the scene graph proved the scene was clean. Recover ground truth programmatically, never from an image.
5. **Backup & restore transforms** you mutate (camera location/rotation) so the live scene is untouched.

## Wiring a native MCP client (Hermes)
- `blender-mcp` is a **PyPI Python package**, NOT npm. Run it with `uvx blender-mcp` (stdio MCP server). The wrong form `npx -y blender-mcp` fails (wrong ecosystem).
- **npm imposter warning:** the npm package `blender-mcp@1.0.1` is a BROKEN imposter (its bin is an invalid Node script). Never use `npx blender-mcp`. The canonical `ahujasid/blender-mcp` is Python and runs via `uvx`.
- Config: add to `~/.mcp_servers.json`:
  `"blender": {"type": "stdio", "command": "uvx", "args": ["blender-mcp"]}`
  (or under `mcp_servers:` in `~/.hermes/config.yaml`).
- After editing, Hermes must **reload MCP servers** to expose `blender_*` tools.

### Using the bridge with mcp-cli
- List servers / tools: `mcp-cli info blender`
- Call a tool: `mcp-cli call blender <tool> '<json-params>'`
- **New-protocol gotcha:** `get_scene_info` and similar now REQUIRE a `user_prompt` param. `mcp-cli call blender get_scene_info '{}'` fails; use `mcp-cli call blender get_scene_info '{"user_prompt":"list the current scene"}'`.

### STALE-ADDON TIMEOUT (critical pitfall)
Even with `uvx blender-mcp` wired correctly, every command can hang with
`Error [SERVER_CONNECTION_FAILED]: MCP error -32001: Request timed out`
while the bridge log says `Connected to Blender at localhost:9876`. The cause:
the **addon.py inside Blender is an OLDER protocol than the `blender-mcp` server expects**
(the bridge prints `WARNING - Blender MCP addon on disk is outdated (expected protocol 4)`).
The download/import handlers then never answer. Fix:
1. `uvx blender-mcp install-addon`   (updates addon.py on disk)
2. In Blender: Edit → Preferences → Add-ons → disable **Interface: Blender MCP** → re-enable it
3. In the 3D viewport sidebar (N-panel) click **Start MCP Server** again.
After that, `mcp-cli call blender ...` responds and Poly Haven / Sketchfab tools become usable.

### Flag-gated asset providers (Poly Haven / Sketchfab)
These handlers only register when the matching scene flag is ON; otherwise commands
silently time out / are not offered:
- Poly Haven: `bpy.context.scene.blendermcp_use_polyhaven = True` enables
  `get_polyhaven_categories`, `search_polyhaven_assets`, `download_polyhaven_asset`, `set_texture`.
  No API key needed. Toggle in the sidebar panel "Use assets from Poly Haven".
- Sketchfab: `bpy.context.scene.blendermcp_use_sketchfab = True` AND a valid
  `bpy.context.scene.blendermcp_sketchfab_api_key` are both required for
  `search_sketchfab_models`, `download_sketchfab_model`. Set the key in the sidebar panel.
- If `get_polyhaven_status` / `get_sketchfab_status` show `enabled: false`, flip the flag
  (via `execute_code` or the panel) before relying on the download calls.

### Second registerable server: ellmos-blender-use-mcp
A separate, add-on-free MCP server that shells out to `blender` on PATH for headless
FBX reimport verification and background script runs (`blender_run_script`, `blender_verify_fbx_reimport`).
- `npx -y ellmos-blender-use-mcp` exits 0 immediately and does NOT start the server (the
  `import.meta.url === pathToFileURL(process.argv[1])` bootstrap check is defeated by npx's shim).
- **Fix:** install it to a stable path (npx cache is prunable) and invoke `node` on the script directly:
  `npm install ellmos-blender-use-mcp` then config
  `"blender-ellmos": {"type": "stdio", "command": "node", "args": ["/stable/path/node_modules/ellmos-blender-use-mcp/src/index.js"]}`.
- Requires `blender` on PATH (it spawns it for real work).

## Common Mistakes
- **Trusting a screenshot over the scene graph.** Vision/read of a PNG is unreliable for "is object X present"; always resolve against `get_scene_info` / `bpy.data.objects`.
- **`npx blender-mcp`.** Wrong runtime; use `uvx blender-mcp`.
- **Assuming the link works.** Port scan + read-only round-trip first; the addon must be running in Blender (panel: "Running on port 9876").
- **Leaving test geometry behind.** Always name test objects uniquely and delete them; confirm with a final `get_scene_info`.
- **Rendering a blank frame.** A wrong camera transform yields a gray empty render even when the scene is fine — frame the camera on the target (use `to_track_quat`) and re-verify the render image actually shows geometry.

## Real-World Impact
Verified end-to-end on a live Blender 5.x + Blender MCP addon: read scene, spawn Suzanne/Torus, apply PBR material, add light, reposition camera, viewport screenshot, Cycles render (cube visible & shaded), glTF export — then fully restored to the original 3-object scene. The `uvx` wiring fix and the direct TCP client both confirmed working.
