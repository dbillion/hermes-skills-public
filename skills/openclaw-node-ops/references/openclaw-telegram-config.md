# OpenClaw Telegram config — schema + safe token write

## Schema differs per host — ALWAYS inspect first
```bash
ssh champion 'python3 -c "import json;d=json.load(open(\"/home/champion/.openclaw/openclaw.json\"));print(list(d.keys()))"'
```
- This host (openclaw.json): top-level `telegram.botToken`.
- champion node (openclaw.json): `channels.telegram.botToken`, with siblings
  `enabled`, `groups`, `dmPolicy`, `groupPolicy`.
  Drill: `d["channels"]["telegram"]`.
- Writing to the wrong path = dead key (config present but never read).

## Safe token write (no echo, no CLI arg, 600 temp file)
On THIS host:
```bash
python3 -c "import os;p='/tmp/bot_token.txt';fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600);open(fd,'w').write('6574...:AA...');os.chmod(p,0o600)"
```
Ship to node + apply (guard verifies prefix so a wrong token can't be written):
```bash
scp /tmp/bot_token.txt champion:/tmp/bot_token.txt
ssh champion 'chmod 600 /tmp/bot_token.txt
python3 - <<PY
import json,os
tok=open("/tmp/bot_token.txt").read().strip()
assert tok.startswith("6574"), "token guard failed"
cfg="/home/champion/.openclaw/openclaw.json"
d=json.load(open(cfg))
d["channels"]["telegram"]["botToken"]=tok
d["channels"]["telegram"]["enabled"]=True
json.dump(d,open(cfg,"w"),indent=2)
os.remove("/tmp/bot_token.txt")
print("wrote botToken, removed temp")
PY'
rm -f /tmp/bot_token.txt
```
Verify without printing the token:
```bash
ssh champion 'python3 -c "import json;d=json.load(open(\"/home/champion/.openclaw/openclaw.json\"));t=d[\"channels\"][\"telegram\"];print(\"enabled=\",t[\"enabled\"],\"| set=\",bool(t.get(\"botToken\")),\"| starts=\",str(t.get(\"botToken\",\"\")).startswith(\"6574\"))"'
```

## Tip: a pasted `ssh-ed25519 ...` key is PUBLIC — safe to log. Only `~/.ssh/id_ed25519` is secret.
