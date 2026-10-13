# Hardsub captions (Manim only writes .srt sidecars)

Manim `add_subcaption()` emits a sidecar `CollectionsExplainer.srt` — it does NOT
burn visible text into the MP4. Viewers with no SRT loader see NOTHING. So after
rendering, merge per-scene SRTs (offset by each scene's start time) and hardsub.

## Merge multiple scene SRTs into one timeline
Per-scene durations from `ffprobe`:
`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 media/videos/script/480p15/S1.mp4`
A small python (merge_srt.py pattern) shifts each scene's cues by the cumulative
offset and concatenates them into `merged.srt`. (For a single-scene render, just
`cp media/.../X.srt merged.srt`.)

## Burn in with ffmpeg
```bash
ffmpeg -y -i final.mp4 -vf "subtitles=merged.srt:force_style='FontSize=18,PrimaryColour=&H00FFFF00&,OutlineColour=&H00000000&,BorderStyle=1,Outline=2'" -c:a copy final_subbed.mp4
```
Yellow text (`&H00FFFF00&` = BGR for yellow), black outline, readable on dark BG.
Deliverable is `final_subbed.mp4` (captions visible on any player).
