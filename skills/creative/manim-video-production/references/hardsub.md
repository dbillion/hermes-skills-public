# Hardsubbing captions into a Manim video

Manim's `self.add_subcaption(text)` writes a `.srt` SIDE CAR next to the rendered
`.mp4` — it does NOT burn text into the video. Players that don't load the .srt show
no captions. Burn them in with ffmpeg.

## Step 1: render (each scene emits its own .srt)
```
manim -ql script.py SceneName
# -> media/videos/script/480p15/SceneName.mp4  + SceneName.srt
```

## Step 2: if multiple scenes, merge with cumulative offsets
Get each scene duration:
```
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 media/videos/script/480p15/S1.mp4
```
Then shift each scene's `.srt` timestamps by the sum of prior scene durations and
concatenate into `merged.srt`. (A tiny python script does this: parse `HH:MM:SS,mmm -->
HH:MM:SS,mmm` blocks, add offset seconds, re-emit.)

## Step 3: burn in
```
ffmpeg -i in.mp4 -vf "subtitles=merged.srt:force_style='FontSize=18,PrimaryColour=&H00FFFF00&,OutlineColour=&H00000000&,BorderStyle=1,Outline=2'" -c:a copy out.mp4
```
- `PrimaryColour`/`OutlineColour` are little-endian BGR hex (e.g. `&H00FFFF00` = yellow).
- If fonts look wrong, add `:fontsdir=/path` or set `FontName=`.

Deliverable = `out.mp4` (the hardsubbed file), not the raw render.
