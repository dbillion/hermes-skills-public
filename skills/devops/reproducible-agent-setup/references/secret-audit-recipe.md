# Secret Audit Recipe (run BEFORE commit)

Goal: prove the staged tree contains NO real secret values. Run from the setup repo root.

## 1. No live secret/config files staged
```bash
git diff --cached --name-only \
  | grep -E '(\.env$|secrets\.env$|^config\.yaml$|^mcp_servers\.json$|auth\.json|nous_auth|\.db$|tgforwarder/|lightpanda$)' \
  && echo "LEAK: live secret file staged" || echo "OK: no live secret files"
```
Expect: OK.

## 2. No real credential strings anywhere in staged files
Scan staged files for actual credential shapes (not doc mentions):
```bash
git diff --cached --name-only -z \
  | xargs -0 grep -IliE '(sk-[a-z0-9]{20,}|ghp_[a-z0-9]{20,}|xox[baprs]-|ya29\.|AIza[0-9A-Za-z_-]{20,}|cf_clearance=|AWSALB|substack\.sid=s%)' 2>/dev/null \
  || echo "OK: no credential patterns"
```
NOTE: some skill docs legitimately MENTION these patterns as examples (e.g. a
credential-hygiene skill, an auth-workflow doc with truncated `eyJ1c2…` tokens).
If the grep prints files, open them and confirm they are truncated examples, not
real values. Real secrets are long, complete tokens — examples are `…`, `<...>`,
or obviously truncated.

Better (no shell pipe; use the search tool / search_files instead of xargs):
- Search the committed tree for `cf_clearance=|AWSALBTG=|substack\.sid=s%|sk-[A-Za-z0-9]{20}|ghp_...|xox[baprs]-...|ya29\.` — expect 0 real hits.

## 3. Templates are valid YAML/JSON
```bash
python3 -c "import yaml; yaml.safe_load(open('config.yaml.template')); print('config OK')"
python3 -c "import json; json.load(open('mcp_servers.json.template')); print('mcp OK')"
```

## 4. Placeholders present where secrets were
```bash
grep -o '\${ENV:[A-Z_0-9]*}' config.yaml.template | sort -u
grep -o '\${ENV:[A-Z_0-9]*}' mcp_servers.json.template | sort -u
```
Expect: the masked secret names (e.g. SUBSTACK_SESSION_TOKEN, ZAPIER_YOUTUBE_TOKEN, GITHUB_PERSONAL_ACCESS_TOKEN, …).

## 5. No binary blobs staged
```bash
git diff --cached --name-only | grep -E '\.(png|jpg|jpeg|bin|mp4|zip|gguf|pt|onnx|glb|wav|mp3|pdf|pptx|docx|xlsx)$' \
  && echo "LEAK: binary blob" || echo "OK: no blobs"
```

## 6. Nested .git dirs resolved (no submodules)
```bash
git submodule status | grep -q . && echo "LEAK: submodule" || echo "OK: no submodules"
find skills -name '.git' -type d && echo "LEAK: nested .git" || echo "OK: no nested .git"
```
If a skill copied with its own `.git`, move it to ~/.local/share/Trash/ (recoverable),
then `git rm --cached <skill>` and re-`git add` so it tracks as plain files.
