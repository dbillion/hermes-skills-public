# Probe Recipes

Copy-paste, fill the env var, run. These are the exact probes that diagnosed the
two failures in the 2026-08-14 session (Groq STT model drift + GA4/GSC 403).

## 1. Groq — list live transcription models (find dead entries in a hardcoded list)
```bash
KEY=$(grep -E '^GROQ_API_KEY=' ~/.hermes/.env | head -1 | cut -d= -f2-)
curl -s -H "Authorization: Bearer $KEY" https://api.groq.com/openai/v1/models \
  | python3 -c "import sys,json; d=json.load(sys.stdin); ms=[m['id'] for m in d.get('data',[])]; a=[m for m in ms if any(k in m.lower() for k in ['whisper','distil','transcribe','audio','scribe'])]; print('AUDIO MODELS:'); [print('  -',m) for m in sorted(a)]"
```
Keep only the printed ids in any GROQ_MODELS allow-list. Anything else (e.g.
`distil-whisper-large-v3-en`) returns 400 "has been decommissioned".

## 2. GA4/GSC — prove auth works but property ACL is missing (the 403 trap)
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/home/deeone/kings-sales-key.json
ga4 gsc sitemaps list --site sc-domain:kings-sales.com
# Expect one of:
#   403 Forbidden ... does not have sufficient permission for site ...   <- identity valid, not a property user
#   a sitemap table                                                   <- fixed (see below)
```
Fix recipe (requires the user's Google login — agent cannot do it):
- search.google.com/search-console → property → Settings → Users and permissions → Add user
- email: the service-account client_email from the credentials JSON (e.g. kings-sales-agent@future-abode-338616.iam.gserviceaccount.com)
- permission: Owner
Re-run the probe; a non-403 response means the blocker is resolved.

## 3. PATH check (binary exists under a different name / only in interactive shell)
```bash
zsh -ic 'command -v ga4 && ga4 --version'     # real interactive shell the user runs
bash -c 'export PATH="$HOME/go/bin:$PATH"; command -v ga4'   # non-interactive fallback
```
If `command not found`, symlink the real binary (`ga4-manager`) as `ga4` inside a
PATH dir and add that dir to both ~/.zshrc and ~/.bashrc.
