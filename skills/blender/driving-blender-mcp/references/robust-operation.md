# Robust Blender-MCP Operation (recipes)

Companion to the "Session-lifecycle, multi-instance & long-run pitfalls" section.

## 1. Re-probe + relaunch when the port is dead
The addon auto-starts its server on `register()`; a fresh Blender launch restores 9876.

```bash
# probe
python3 -c "import socket;s=socket.socket();s.settimeout(1);s.connect(('127.0.0.1',9876));print('OPEN')"

# relaunch (background, tracked)
#   terminal(background=true, notify_on_complete=false): /usr/local/bin/blender
# wait for port (poll loop, up to ~60s)
for i in $(seq 1 20); do
  timeout 2 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/9876' 2>/dev/null && { echo "OPEN"; break; }
  sleep 3
done
```

## 2. Kill stray Blender instances safely (never pkill by name)
```bash
for pid in $(ps -eo pid,comm | awk '$2=="blender"{print $1}'); do kill -9 "$pid"; done
sleep 3
# confirm none remain, then relaunch a single instance
```

## 3. Run long build/render scripts in background
Foreground tool caps ~420s and SIGKILLs the *client*, leaving Blender busy.
```bash
# terminal(background=true, notify_on_complete=true):
#   cd /tmp && python3 build_duck.py > /tmp/build_duck.out 2>&1 ; echo "EXIT=$?"
```

## 4. Rendered-viewport screenshot = reliable "picture" (no bake)
Set shading to RENDERED via `execute_code`, then `get_viewport_screenshot`.
```python
import bpy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'RENDERED'
                space.shading.use_scene_lights = True
                space.shading.use_scene_world = True
bpy.context.view_layer.update()
```
Then: `send({"type":"get_viewport_screenshot","params":{"file_path":"/tmp/duck_render.png"}})`

## 5. Socket client that tolerates slow ops (read-until-close, long timeout)
```python
import socket, json, time
HOST, PORT, T = "127.0.0.1", 9876, 900.0   # T covers the slowest op
def send(payload, retries=2):
    last = None
    for _ in range(retries + 1):
        try:
            s = socket.create_connection((HOST, PORT), timeout=T); s.settimeout(T)
            s.sendall(json.dumps(payload).encode())
            buf = b""
            while True:
                try:
                    chunk = s.recv(65536)
                except socket.timeout:
                    break
                if not chunk:
                    break
                buf += chunk
            s.close()
            if not buf.strip():
                last = RuntimeError("empty response"); time.sleep(1.5); continue
            return json.loads(buf.decode())
        except (OSError, json.JSONDecodeError) as e:
            last = e; time.sleep(1.5)
    raise last
```

## 6. Version-robust engine / world setup
```python
try: scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception: scene.render.engine = 'BLENDER_EEVEE'
w = scene.world or bpy.data.worlds.new("DuckWorld"); scene.world = w
try: w.use_nodes = True
except Exception: pass   # Blender 5.0 removed World.use_nodes
```
