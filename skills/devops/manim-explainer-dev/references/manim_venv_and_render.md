# Manim uv venv: syntax-check, render, verify on disk

## The venv path
`manim` is installed as the `uv tool manim` venv. The default Python the agent
loads does NOT have `manim`, so `from manim import *` and every manim symbol raise
false "unresolved / not defined" LSP errors. They are NOT real errors.

```
MANIM_PY="$HOME/.local/share/uv/tools/manim/bin/python"
MANIM_BIN="$HOME/.local/bin/manim"   # or same dir as above bin/
export PATH="$HOME/.local/share/uv/tools/manim/bin:$PATH"
```

## Syntax-check (the fix for the false LSP errors)
```
"$MANIM_PY" -c "import ast,glob; [ast.parse(open(f).read()) for f in ['improved_dsa_style.py','demo_kadane_v2.py','demo_merge_sort_v2.py']]; print('AST OK')"
"$MANIM_PY" -c "import manim; print(manim.__version__)"   # 0.20.1
```

## Render + verify on DISK (not just exit 0)
3D cairo renders are slow (~5-8 min for a ~30s 3D scene at -ql). ALWAYS background:
```
terminal(background=true, notify_on_complete=true):
  cd /home/deeone/<name>-v2
  export PATH="$HOME/.local/share/uv/tools/manim/bin:$PATH"
  export JAVA_HOME="$HOME/.sdkman/candidates/java/17.0.12-graal"
  manim -q low --resolution 480,480 -pql demo_kadane_v2.py KadaneV2
```
Then verify the artifact exists (skill rule: verify from disk, not memory):
```
ls -la media/videos/demo_kadane_v2/480p15/KadaneV2.mp4
ffprobe -v error -show_entries format=duration <file>   # expect ~34s
```

## Pitfalls
- Foreground render of a 3D scene exceeds the 60s foreground cap -> it gets killed.
- `find . -name '*.mp4'` while rendering prints partial_movie_files and can exit 1
  on stderr even though it "worked" — check the final `KadaneV2.mp4` directly.
- Cairo renderer is the right one for these scenes (no OpenGL needed).
