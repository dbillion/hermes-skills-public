# Non-interactive Netlify deploy — verified recipe

## CLI discovery (same machine as user, but agent can't see it)
Netlify CLI may be installed via bun, not npm. Agent's default bash PATH
differs from user's interactive zsh. Check:
```bash
ls $HOME/.bun/bin | grep netlify
zsh -ic 'command -v netlify'          # user's real PATH
export PATH="$HOME/.bun/bin:$PATH"    # then it works
```
Verify: `netlify status` → shows user/team. "not linked" is OK.

## Deploy (one command, no prompts, no crash)
```bash
cd /path/to/site
export PATH="$HOME/.bun/bin:$PATH"
netlify deploy --create-site <site-name> --prod --dir .
```
- `--create-site` creates + links + deploys in one non-interactive call.
- Avoid `netlify link` / bare `netlify deploy` → interactive prompt + possible
  top-level-await crash under Node 25 + bun.
- `netlify link --team` is NOT a valid flag.

## Optimize heavy GIFs before deploy (run in background)
83×480p GIFs ≈ 184 MB. Shrink with ImageMagick:
```bash
mkdir -p $HOME/.trash/gifs-orig-$(date +%s) && cp gifs/*.gif $_
mogrify -strip -resize 380x -layers optimize -colors 128 gifs/*.gif
```
Run with background=true + notify_on_complete (exceeds 180s for 80+ files).

## Push to GitHub (if "its own repo" requested)
```bash
gh auth status                        # usually authed as user w/ repo scope
git init -q && git add -A && git -c user.email=dev@local -c user.name=hermes commit -q -m init
gh repo create <name> --public --source=. --remote=origin --push
```

## Verify (agent cannot run in-browser JS)
- `web_extract <production-url>` → HTML title/brand present.
- `web_extract <production-url>/media.js` → asset serves.
- State that live JS render path is unverified by agent.
