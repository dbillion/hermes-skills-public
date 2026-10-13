#!/usr/bin/env python3
"""
Generate redacted *.template files from live Hermes config WITHOUT ever
copying secret VALUES. Only ${ENV:VAR} placeholders are written.

Inputs (read-only, never printed):
  /home/deeone/.hermes/config.yaml
  /home/deeone/.mcp_servers.json
  /home/deeone/.env

Outputs (safe to commit):
  config.yaml.template
  mcp_servers.json.template
  secrets.example
"""
import json, os, re, sys

HOME = "/home/deeone"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

SECRET_KEYS = {
    "api_key", "token", "secret", "password", "session_token",
    "password_hash", "access_token", "private_key", "bearer",
    "client_secret", "refresh_token", "session_string",
}

def is_placeholder(v: str) -> bool:
    v = v.strip()
    return v.startswith("$") or v.startswith("${") or v in ("", "{}", "[]", '""', "''", "null", "~", "None")

# ---------- config.yaml ----------
parent_provider = None
cfg_in = f"{HOME}/.hermes/config.yaml"
cfg_lines = []
in_env_block = False          # inside an `env:` mapping block
env_indent = 0
with open(cfg_in) as f:
    for raw in f:
        line = raw.rstrip("\n")

        # ---- env: block handling (works even for continuation lines w/o a colon) ----
        if in_env_block:
            ind = len(line) - len(line.lstrip(" "))
            # A line at indent <= env_indent (that isn't the "env:" key itself)
            # ends the env block -> fall through to normal processing.
            if ind <= env_indent and not re.match(r"^\s*env:\s*$", line):
                in_env_block = False
            else:
                if re.match(r"^\s*env:\s*$", line):
                    cfg_lines.append(line + "\n")  # keep literal "env:" key
                    continue
                elif re.match(r"^\s+([\w-]+):\s*(.*)$", line):
                    nk = re.match(r"^\s+([\w-]+):\s*(.*)$", line)
                    if nk:
                        envname = nk.group(1).upper().replace(" ", "_")
                        cfg_lines.append(f"{nk.group(0).split(':',1)[0]}: ${{ENV:{envname}}}\n")
                    else:
                        cfg_lines.append("\n")
                    continue
                else:
                    # multi-line value continuation -> drop (never write secrets)
                    cfg_lines.append("\n")
                    continue

        m = re.match(r"^(\s*)(-\s*)?([A-Za-z_][A-Za-z0-9_ -]*?):\s*(.*)$", line)
        if m:
            indent, dash, key, val = m.group(1), m.group(2) or "", m.group(3), m.group(4)
            base = key.strip().rstrip(":").split()[-1]

            # Plain secret-bearing top-level keys (e.g. api_key, password, session_token)
            if base in SECRET_KEYS and not is_placeholder(val):
                if base == "api_key":
                    env = f"{parent_provider or 'PROVIDER'}_API_KEY".upper()
                elif base == "password":
                    env = "HERMES_PASSWORD"
                elif base == "session_token":
                    env = "SUBSTACK_SESSION_TOKEN"
                else:
                    env = key.strip().upper().replace(" ", "_")
                line = f"{indent}{dash}{key}: ${{ENV:{env}}}"

            # Detect entry/exit of an `env:` mapping block (by keyword + indent)
            if base == "env" and val == "":
                in_env_block = True
                env_indent = len(indent)
            elif in_env_block and len(indent) <= env_indent:
                in_env_block = False

            # zapier-style url with ?token= -> mask the token value
            if base == "url" and "token=" in val:
                prefix = val.split("token=", 1)[0]
                line = f"{indent}{dash}{key}: {prefix}token=${{ENV:ZAPIER_YOUTUBE_TOKEN}}"

            # capture top-level provider name for api_key mapping
            if re.match(r"^\s*[A-Za-z0-9_]+:\s*$", line) and indent == "":
                parent_provider = key.strip().rstrip(":")
        cfg_lines.append(line + "\n")

with open(f"{OUT}/config.yaml.template", "w") as f:
    f.writelines(cfg_lines)

# ---------- mcp_servers.json ----------
mcp_in = f"{HOME}/.mcp_servers.json"
with open(mcp_in) as f:
    mcp = json.load(f)

env_var_names = set()
for name, srv in mcp.get("mcpServers", {}).items():
    if "env" in srv and isinstance(srv["env"], dict):
        for k, v in srv["env"].items():
            env_var_names.add(k)
            srv["env"][k] = f"${{ENV:{k}}}"

with open(f"{OUT}/mcp_servers.json.template", "w") as f:
    json.dump(mcp, f, indent=2)
    f.write("\n")

# ---------- secrets.example (names only, no values) ----------
# Config key_env / *_env references + any ${ENV:...} names produced by masking
cfg_env_refs = set()
with open(cfg_in) as f:
    for line in f:
        m = re.search(r"(key_env|access_token_env|token_env|secret_env)\s*:\s*([A-Za-z0-9_]+)", line)
        if m:
            cfg_env_refs.add(m.group(2))
        for e in re.findall(r"\$\{ENV:([A-Za-z0-9_]+)\}", line):
            cfg_env_refs.add(e)

# .env keys
dotenv_keys = set()
dotenv_path = f"{HOME}/.env"
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
            if m:
                dotenv_keys.add(m.group(1))

# currently exported relevant env (names only)
import subprocess
exported = set()
try:
    out = subprocess.run(["env"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if "=" in line:
            k = line.split("=", 1)[0]
            if re.search(r"(KEY|TOKEN|SECRET|PASS|API|TG_|TELEGRAM|NIM|BWS|NOTION|GUMROAD|NANOBANANA|SERPER|GOOGLE|CEREBRAS|GROQ|DEEPGRAM|DISCORD|STITCH|TINKER|WANDB|APIFY|LIGHTPANDA)", k):
                exported.add(k)
except Exception:
    pass

all_vars = sorted(env_var_names | cfg_env_refs | dotenv_keys | exported)
with open(f"{OUT}/secrets.example", "w") as f:
    f.write("# Copy to secrets.env and fill in real values. NEVER commit secrets.env.\n")
    f.write("# These are fed to Hermes at runtime via environment / .env.\n\n")
    for v in all_vars:
        f.write(f"{v}=\n")

print(f"config.yaml.template lines: {len(cfg_lines)}")
print(f"mcp servers templated: {len(mcp.get('mcpServers', {}))}")
print(f"secret env var names catalogued: {len(all_vars)}")
print("Wrote: config.yaml.template, mcp_servers.json.template, secrets.example")
