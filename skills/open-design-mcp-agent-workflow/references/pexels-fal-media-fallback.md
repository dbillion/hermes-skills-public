# Pexels ↔ fal.ai media fallback (verified this session)

## fal.ai was LOCKED
- Key format seen: `KEYID:KEYSECRET` (e.g. `16c709d7-...:719be588...`).
- A real API call returns **HTTP 403** with body `{"error":{"code":"provider_access_denied","reason":"TOP_UP"}}`.
  This means the account needs a top-up; image/video generation (`fal-generate`,
  `fal-kling-o3`, `fal-video-edit`, `fal-3d`, etc.) will NOT work until paid.
- Auth headers tried (all 403): `Key <id:secret>`, `Bearer <secret>`, `Basic base64(id:secret)`.
  The lock is account-level, not auth-format. Don't waste time rotating headers.
- The Open Design `start_run` for `fal-*` skills also fails for the same reason.

## Pexels is the working fallback (free API key)
- Get a free key at https://www.pexels.com/api/ (instant). It is a real key, not a placeholder.
- Video search: `GET https://api.pexels.com/v1/videos/search?query=waterfall&per_page=5`
  Header: `Authorization: <PEXELS_KEY>`. Returns JSON with `videos[].video_files[].link`
  (pick `height>=1080` / `1080p` link).
- Picture search: `GET https://api.pexels.com/v1/search?query=resort&per_page=5`.
- Download the `.mp4`/`.jpg` directly with the link (no auth needed for the CDN link, but
  keep the search call authed).
- In our run we fetched `victoria-falls.mp4` (21M) and `canada-waterfall.mp4` (25M), both 1080p.

## Wiring footage into a carousel
- Videos don't autoplay in a headless screenshot. Put a `poster=` still on the `<video>`:
  `ffmpeg -y -ss 00:00:02 -i clip.mp4 -frames:v 1 -q:v 2 poster.jpg`
- Use `<video autoplay muted loop playsinline poster="poster.jpg"><source src="clip.mp4"></video>`.

## Note on keys
- Pexels key and fal.ai key were provided by the user mid-session. Treat them as user-owned
  secrets; never echo them. This file documents the *behavior* (lock + fallback), not the values.
