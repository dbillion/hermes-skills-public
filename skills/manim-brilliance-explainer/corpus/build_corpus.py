import json
import re
from pathlib import Path

REPOS = [
    "grant-manim",
    "community-manim",
]

SCENE_RE = re.compile(r"class\s+(\w+)\(([^)]*)\)")
PLAY_RE = re.compile(r"self\.play\(")
TRANSFORM_RE = re.compile(
    r"Transform|ReplacementTransform|TransformMatchingShapes|TransformMatchingTex"
)
VALUE_TRACKER_RE = re.compile(r"ValueTracker|always_redraw|add_updater")
CAMERA_RE = re.compile(r"camera\.frame|MovingCameraScene|set_camera_orientation")
TRACED_RE = re.compile(r"TracedPath|TracingTail")

results = []

for repo in REPOS:
    root = Path(repo)
    if not root.exists():
        continue

    for path in root.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        scenes = SCENE_RE.findall(text)

        results.append(
            {
                "repo": repo,
                "file": str(path),
                "scenes": [{"name": name, "bases": bases} for name, bases in scenes],
                "play_calls": len(PLAY_RE.findall(text)),
                "transform_patterns": len(TRANSFORM_RE.findall(text)),
                "dynamic_patterns": len(VALUE_TRACKER_RE.findall(text)),
                "camera_patterns": len(CAMERA_RE.findall(text)),
                "traced_patterns": len(TRACED_RE.findall(text)),
            }
        )

out = Path("corpus/manim_corpus.json")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(results, indent=2), encoding="utf-8")

print(f"Wrote {len(results)} files to {out}")
