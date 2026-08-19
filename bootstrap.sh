#!/usr/bin/env bash
#
# bootstrap.sh — Reinstall the full Hermes Agent setup on a fresh machine.
#
# What it does:
#   1. Loads secret values from ./secrets.env (NOT committed — you supply it).
#   2. Instantiates config.yaml and mcp_servers.json from the *.template files
#      by substituting ${ENV:VAR} placeholders with values from the environment.
#   3. Reinstalls external tool CLIs (hermes, nlm, codegraph, mcp-cli, lightpanda, tgforwarder).
#   4. Copies user-authored skills and re-creates symlinks for external skill sources.
#
# SAFE: this script never prints secret values. It only reads them into the
# environment and writes them into local (gitignored) config files.
#
# Usage:
#   ./bootstrap.sh [--skip-tools] [--skip-skills]
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME:-/home/$(whoami)}"
HERMES_DIR="$HOME_DIR/.hermes"
SECRETS="$HERE/secrets.env"

# ---------- parse flags ----------
SKIP_TOOLS=0
SKIP_SKILLS=0
for a in "$@"; do
  case "$a" in
    --skip-tools) SKIP_TOOLS=1 ;;
    --skip-skills) SKIP_SKILLS=1 ;;
    *) echo "unknown arg: $a" >&2; exit 1 ;;
  esac
done

# ---------- 1. load secrets ----------
if [[ -f "$SECRETS" ]]; then
  echo "[bootstrap] loading secrets from secrets.env"
  set -a
  # shellcheck disable=SC1090
  source "$SECRETS"
  set +a
else
  echo "[bootstrap] WARNING: $SECRETS not found." >&2
  echo "              Copy secrets.example -> secrets.env and fill in values," >&2
  echo "              or export the variables into your shell before running." >&2
fi

# ---------- 2. instantiate config from template ----------
subst() {
  # $1 = input template, $2 = output file
  local in="$1" out="$2"
  local tmp; tmp="$(mktemp)"
  # Replace ${ENV:VAR} with the env value (empty if unset). Never echoes values.
  sed -E 's/\$\{ENV:([A-Za-z_][A-Za-z0-9_]*)\}/__SUBST_\1__/g' "$in" > "$tmp"
  while IFS= read -r line; do
    while [[ "$line" =~ __SUBST_([A-Za-z_][A-Za-z0-9_]*)__ ]]; do
      local var="${BASH_REMATCH[1]}"
      local val="${!var:-}"
      line="${line//__SUBST_${var}__/$val}"
    done
    printf '%s\n' "$line"
  done < "$tmp" > "$out"
  rm -f "$tmp"
}

echo "[bootstrap] writing $HERMES_DIR/config.yaml"
mkdir -p "$HERMES_DIR"
subst "$HERE/config.yaml.template" "$HERMES_DIR/config.yaml"

echo "[bootstrap] writing $HOME_DIR/.mcp_servers.json"
subst "$HERE/mcp_servers.json.template" "$HOME_DIR/.mcp_servers.json"

# ---------- 3. external tool CLIs ----------
if [[ "$SKIP_TOOLS" -eq 0 ]]; then
  echo "[bootstrap] installing external tool CLIs"
  export PATH="$HOME_DIR/.local/bin:$PATH"
  mkdir -p "$HOME_DIR/.local/bin"

  # uv (needed for hermes/nlm and many tools)
  if ! command -v uv >/dev/null 2>&1; then
    echo "  - installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi

  # Hermes Agent (installs its own venv + CLI)
  if ! command -v hermes >/dev/null 2>&1; then
    echo "  - installing hermes"
    curl -LsSf https://hermes-agent.nousresearch.com/install.sh | sh
  fi

  # nlm (NotebookLM MCP CLI) via uv tool
  if ! command -v nlm >/dev/null 2>&1; then
    echo "  - installing nlm (uv tool)"
    uv tool install notebooklm-mcp-cli || pip install --user notebooklm-mcp-cli
  fi

  # codegraph (binary release)
  if ! command -v codegraph >/dev/null 2>&1; then
    echo "  - installing codegraph"
    uv tool install codegraph 2>/dev/null || pip install --user codegraph
  fi

  # mcp-cli (binary release)
  if ! command -v mcp-cli >/dev/null 2>&1; then
    echo "  - installing mcp-cli"
    uv tool install mcp-cli 2>/dev/null || pip install --user mcp-cli
  fi

  # lightpanda headless browser (binary)
  if [[ ! -x "$HOME_DIR/bin/lightpanda" ]]; then
    echo "  - downloading lightpanda"
    mkdir -p "$HOME_DIR/bin"
    curl -LsSf https://cdn.lightpanda.io/latest/linux-x64/lightpanda -o "$HOME_DIR/bin/lightpanda"
    chmod +x "$HOME_DIR/bin/lightpanda"
  fi

  # tgforwarder (your Telegram MTProto forwarder)
  if ! command -v tgforwarder >/dev/null 2>&1 && [[ -d "$HOME_DIR/Documents/scraper/python-scraper/tgforwarder" ]]; then
    echo "  - installing tgforwarder (editable)"
    pip install --user -e "$HOME_DIR/Documents/scraper/python-scraper/tgforwarder"
  fi
else
  echo "[bootstrap] skipping tool install (--skip-tools)"
fi

# ---------- 4. skills ----------
if [[ "$SKIP_SKILLS" -eq 0 ]]; then
  echo "[bootstrap] installing skills"

  # 4a. User-authored skills -> ~/.hermes/skills
  SKILLS_DST="$HERMES_DIR/skills"
  mkdir -p "$SKILLS_DST"
  if [[ -d "$HERE/skills" ]]; then
    echo "  - copying user-authored skills -> $SKILLS_DST"
    cp -r "$HERE/skills/." "$SKILLS_DST/"
  fi

  # 4b. External (agent-runtime) skills -> ~/.agents/skills
  AGENTS_DST="$HOME_DIR/.agents/skills"
  mkdir -p "$AGENTS_DST"
  if [[ -d "$HERE/skills-external" ]]; then
    echo "  - copying external skills -> $AGENTS_DST"
    cp -r "$HERE/skills-external/." "$AGENTS_DST/"
  fi

  # 4c. Re-create symlinks back into ~/.hermes/skills for unified discovery
  for ext in "$AGENTS_DST" "$HOME_DIR/.claude/skills" "$HOME_DIR/.codegraph"; do
    if [[ -d "$ext" ]]; then
      echo "  - symlinking $ext into $SKILLS_DST"
      for d in "$ext"/*; do
        [[ -d "$d" ]] || continue
        name="$(basename "$d")"
        ln -sfn "$d" "$SKILLS_DST/$name"
      done
    fi
  done
else
  echo "[bootstrap] skipping skills (--skip-skills)"
fi

echo "[bootstrap] DONE. Restart Hermes / run 'hermes config get' to verify."
