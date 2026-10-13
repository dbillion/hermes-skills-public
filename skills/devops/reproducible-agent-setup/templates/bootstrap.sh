#!/usr/bin/env bash
# bootstrap.sh — reinstall a captured agent setup on a fresh machine.
# SAFE: never prints secret values; reads them from ./secrets.env into the env.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME:-/home/$(whoami)}"
HERMES_DIR="$HOME_DIR/.hermes"
SECRETS="$HERE/secrets.env"

SKIP_TOOLS=0; SKIP_SKILLS=0
for a in "$@"; do
  case "$a" in
    --skip-tools) SKIP_TOOLS=1 ;;
    --skip-skills) SKIP_SKILLS=1 ;;
    *) echo "unknown arg: $a" >&2; exit 1 ;;
  esac
done

if [[ -f "$SECRETS" ]]; then
  echo "[bootstrap] loading secrets from secrets.env"
  set -a; source "$SECRETS"; set +a
else
  echo "[bootstrap] WARNING: $SECRETS not found; export vars or fill it in." >&2
fi

# Substitute ${ENV:VAR} in a template -> output file (never echoes values).
subst() {
  local in="$1" out="$2" tmp; tmp="$(mktemp)"
  sed -E 's/\$\{ENV:([A-Za-z_][A-Za-z0-9_]*)\}/__SUBST_\1__/g' "$in" > "$tmp"
  while IFS= read -r line; do
    while [[ "$line" =~ __SUBST_([A-Za-z_][A-Za-z0-9_]*)__ ]]; do
      v="${BASH_REMATCH[1]}"; line="${line//__SUBST_${v}__/${!v:-}}"
    done
    printf '%s\n' "$line"
  done < "$tmp" > "$out"; rm -f "$tmp"
}

echo "[bootstrap] writing $HERMES_DIR/config.yaml"
mkdir -p "$HERMES_DIR"
subst "$HERE/config.yaml.template" "$HERMES_DIR/config.yaml"
echo "[bootstrap] writing $HOME_DIR/.mcp_servers.json"
subst "$HERE/mcp_servers.json.template" "$HOME_DIR/.mcp_servers.json"

if [[ "$SKIP_TOOLS" -eq 0 ]]; then
  echo "[bootstrap] installing external tool CLIs"
  export PATH="$HOME_DIR/.local/bin:$PATH"; mkdir -p "$HOME_DIR/.local/bin"
  command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
  command -v hermes >/dev/null 2>&1 || curl -LsSf https://hermes-agent.nousresearch.com/install.sh | sh
  command -v nlm >/dev/null 2>&1 || uv tool install notebooklm-mcp-cli 2>/dev/null || pip install --user notebooklm-mcp-cli
  command -v codegraph >/dev/null 2>&1 || uv tool install codegraph 2>/dev/null || pip install --user codegraph
  command -v mcp-cli >/dev/null 2>&1 || uv tool install mcp-cli 2>/dev/null || pip install --user mcp-cli
  [[ -x "$HOME_DIR/bin/lightpanda" ]] || { mkdir -p "$HOME_DIR/bin"; curl -LsSf https://cdn.lightpanda.io/latest/linux-x64/lightpanda -o "$HOME_DIR/bin/lightpanda"; chmod +x "$HOME_DIR/bin/lightpanda"; }
  [[ -d "$HOME_DIR/Documents/scraper/python-scraper/tgforwarder" ]] && command -v tgforwarder >/dev/null 2>&1 || pip install --user -e "$HOME_DIR/Documents/scraper/python-scraper/tgforwarder"
fi

if [[ "$SKIP_SKILLS" -eq 0 ]]; then
  echo "[bootstrap] installing skills"
  SKILLS_DST="$HERMES_DIR/skills"; mkdir -p "$SKILLS_DST"
  [[ -d "$HERE/skills" ]] && cp -r "$HERE/skills/." "$SKILLS_DST/"
  for ext in "$HOME_DIR/.agents/skills" "$HOME_DIR/.claude/skills" "$HOME_DIR/.codegraph"; do
    [[ -d "$ext" ]] || continue
    for d in "$ext"/*; do [[ -d "$d" ]] || continue; ln -sfn "$d" "$SKILLS_DST/$(basename "$d")"; done
  done
fi
echo "[bootstrap] DONE. Restart the agent / run 'hermes config get' to verify."
