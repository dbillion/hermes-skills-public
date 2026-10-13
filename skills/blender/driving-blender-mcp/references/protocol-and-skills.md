# Blender MCP — Protocol Reference & Skill Packs

## Addon wire protocol (from `Vertiiii/blender-mcp` `addon.py`, verified)
- TCP server, default `127.0.0.1:9876`, `SO_REUSEADDR`, `listen(1)`.
- One client per connection; accepts one JSON object, parses with `json.loads(buffer)`, executes in Blender's main thread via `bpy.app.timers.register`, then `client.sendall(json.dumps(response).encode())`.
- Response envelope: `{"status": "success", "result": <any>}` or `{"status": "error", "message": <str>}`.
- No length prefix, no newline delimiter.

### Command types (always available)
| type | params | result |
|---|---|---|
| `get_scene_info` | none | `{name, object_count, objects:[{name,type,location}], materials_count}` |
| `get_object_info` | `{"name":"Cube"}` | location/rotation/scale/visible/materials/world_bounding_box/mesh{vertices,edges,polygons} |
| `get_viewport_screenshot` | `{"filepath":"/tmp/x.png","format":"png","max_size":800}` | `{success,width,height,filepath}` |
| `execute_code` | `{"code":"import bpy; ..."}` | `{executed:true, result:<captured stdout>}` — runs `exec(code, {"bpy":bpy})` |

Conditional handlers (only registered if scene flag enabled): Poly Haven (`get_polyhaven_categories`, `search_polyhaven_assets`, `download_polyhaven_asset`, `set_texture`), Hyper3D Rodin (`create_rodin_job`, `poll_rodin_job_status`, `import_generated_asset`), Sketchfab (`search_sketchfab_models`, `download_sketchfab_model`).

`execute_code` is the universal escape hatch — anything `bpy` can do. It is destructive; wrap in read-only-first + named cleanup guidance.

## Native MCP server package
- PyPI: `blender-mcp` (Siddharth Ahuja, current ~1.8.x). Entry point `blender_mcp.server:main`, provides `mcp[cli]`.
- Run as stdio MCP server: `uvx blender-mcp`. NOT `npx blender-mcp` (wrong ecosystem).

## Curated skill packs (github.com/topics/blender-mcp)
Each reduces to the operations above. Useful ones to adapt for Hermes:
- `arjun988/blender-skills` — 94 specialist skills (modeling, materials, archviz, animation, lighting, camera, rendering, export) as `.claude/skills/*/SKILL.md`.
- `RobLe3/cc-blender-skill` — 10 chain-loadable skills (modeling, materials, lighting, cameras, rendering, animation, export, wireframe-to-3d, pro-workflow).
- `CheshireJCat/create-3d-model-skill` — codex-native modeling skill with scene safety + visual validation.
- `jithinolickal/blender` — agent skill for Claude Code/Codex/ChatGPT.
- `youichi-uda/blender-mcp-pro` — 100+ tools variant.
- `Vertiiii/blender-mcp` — the original addon + server this protocol describes.

## Mock scene-graph vs screenshot truth check
`execute_code` with `json.dumps({o.name for o in bpy.data.objects})` is the authoritative inventory. Use it whenever a screenshot/vision read and the scene graph disagree.
