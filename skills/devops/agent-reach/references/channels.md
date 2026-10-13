# Channels — interpreting doctor output & command groups

## doctor output legend (Chinese UI)
- ✅ 可用        = available / works now
- [!] 已装但需配置/登录 = installed but needs config/login
- [X] 未安装    = not installed

Run `agent-reach doctor --json` for machine-readable per-platform:
  status, name, message, active_backend, tier

## Channel command groups (from the agent skill routing table)
| Intent | Reference file |
| Web / code search | search.md |
| XiaoHongShu/Twitter/Bilibili/V2EX/Reddit/Facebook/Instagram | social.md |
| Jobs / LinkedIn | career.md |
| GitHub / code | dev.md |
| Web pages / articles / RSS | web.md |
| YouTube / Bilibili / podcast transcripts | video.md |

These live under the installed skill dir:
  ~/.agents/skills/agent-reach/references/<file>.md

## Quick zero-config commands
```bash
# Exa web search (after mcporter config add exa ...)
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'

# Read any web page
curl -s "https://r.jina.ai/URL"

# GitHub search
gh search repos "query" --sort stars --limit 10

# YouTube subtitles (NEVER use yt-dlp for Bilibili)
yt-dlp --write-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX hot topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# Bilibili search
bili search "query" --type video -n 5
```

## Gated platforms (need login/cookie/key — not zero-config)
- Twitter/X: OpenCLI preferred; or Cookie-Editor export -> set
  TWITTER_AUTH_TOKEN + TWITTER_CT0 in the env before invoking `twitter`.
- XiaoHongShu: OpenCLI preferred (needs xsec_token flow).
- Xueqiu, Xiaoyuzhou: separate setup (Xiaoyuzhou = Whisper transcription via
  groq/openai key).

## Standing rules (from the agent skill)
1. Health-check before acting on login-backed platforms: run
   `agent-reach doctor --json`, pick the command group matching the
   platform's `active_backend`.
2. Announce what you use: "using agent-reach, platform X via backend Y".
3. On failure, follow the retry chains in the reference files — never guess.
4. For broad research, combine Exa (web) + Twitter/Reddit (discussion) +
   XiaoHongShu/Bilibili (Chinese perspectives).
5. After a substantial multi-platform task, run `agent-reach check-update`.
