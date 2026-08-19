#!/usr/bin/env python3
"""
Generate redacted *.template files from a live Hermes config WITHOUT ever
copying secret VALUES. Only ${ENV:VAR} placeholders are written.

Inputs (read-only, never printed):
  ~/.hermes/config.yaml
  ~/.mcp_servers.json
  ~/.env

Outputs (safe to commit):
  config.yaml.template          - full config, secrets -> ${ENV:VAR}
  mcp_servers.json.template     - all MCP servers, env tokens -> ${ENV:VAR}
  secrets.example               - list of required env var NAMES only (no values)

Usage:  python3 mask_secrets.py <outdir>

PITFALL this handles (see references/secret-redaction-pitfalls.md):
  Multi-line secret values inside `env:` blocks (e.g. Substack session cookies)
  span lines with NO colon, so a per-line `key: val` regex misses them and they
  leak. We intercept env-block lines BEFORE the main parse so continuation lines
  are blanked.
"""
import json, os, re, sys

HOME = os.path.expanduser("~")
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

SECRET_KEYS = {
    "api_key", "token", "secret", "password", "session_token",
    "password_hash", "access_token", "private_key", "bearer",
    "client_secret", "refresh_token", "session_string",
}

def is_placeholder(v: str) -> bool:
    v = v.strip()
    return v.startswith("$") or v.startswith("${") or v in (
        "", "{}", "[]", '""', "''", "null", "~", "None")

# ---------- config.yaml ----------
parent_provider = None
cfg_in = f"{HOME}/.hermes/config.yaml"
cfg_lines = []
in_env_block = False
env_indent = 0

with open(cfg_in) as f:
    for raw in f:
        line = raw.rstrip("\n")

        # ---- env: block handling (also catches continuation lines w/o a colon) ----
        if in_env_block:
            ind = len(line) - len(line.lstrip(" "))
            # line at indent <= env_indent (that isn't the "env:" key) ends the block
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
                        cfg_lines.append(
                            f"{nk.group(0).split(':',1)[0]}: ${{ENV:{envname}}}\n")
                    else:
                        cfg_lines.append("\n")
                    continue
                else:
                    cfg_lines.append("\n")  # drop multi-line value continuation
                    continue

        m = re.match(r"^(\s*)(-\s*)?([A-Za-z_][A-Za-z0-9_ -]*?):\s*(.*)$", line)
        if m:
            indent, dash, key, val = m.group(1), m.group(2) or "", m.group(3), m.group(4)
            base = key.strip().rstrip(":").split()[-1]

            # Plain secret-bearing top-level keys
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

            # Enter an env: mapping block
            if base == "env" and val == "":
                in_env_block = True
                env_indent = len(indent)
            elif in_env_block and len(indent) <= env_indent:
                in_env_block = False

            # zapier-style url with ?token= -> mask the token value
            if base == "url" and "token=" in val:
                prefix = val.split("token=", 1)[0]
                line = f"{indent}{dash}{key}: {prefix}token=${{ENV:ZAPIER_YOUTUBE_TOKEN}}"

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
cfg_env_refs = set()
with open(cfg_in) as f:
    for line in f:
        mm = re.search(r"(key_env|access_token_env|token_env|secret_env)\s*:\s*([A-Za-z0-9_]+)", line)
        if mm:
            cfg_env_refs.add(mm.group(2))
        for e in re.findall(r"\$\{ENV:([A-Za-z0-9_]+)\}", line):
            cfg_env_refs.add(e)

dotenv_keys = set()
dotenv_path = f"{HOME}/.env"
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            mm = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
            if mm:
                dotenv_keys.add(mm.group(1))

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
