---
name: linkedin-cli
description: "A bird-like LinkedIn CLI for searching profiles, checking messages, and summarizing your feed using session cookies."
homepage: https://github.com/clawdbot/linkedin-cli
metadata: {"clawdbot":{"emoji":"💼","requires":{"bins":["python3"],"env":["LINKEDIN_LI_AT","LINKEDIN_JSESSIONID"]}}}
---

# LinkedIn CLI (lk)

A witty, punchy LinkedIn CLI inspired by the `bird` CLI. It uses session cookies for authentication, allowing for automated profile scouting, feed summaries, and message checks without a browser.

## Setup

1.  **Extract Cookies**: Open LinkedIn in Chrome/Firefox.
2.  Go to **DevTools (F12)** -> **Application** -> **Cookies** -> `www.linkedin.com`.
3.  Copy the values for `li_at` and `JSESSIONID`.
4.  Set them in your environment:
    ```bash
    export LINKEDIN_LI_AT="your_li_at_value"
    export LINKEDIN_JSESSIONID="your_jsessionid_value"
    ```

## Dependencies

Requires the `linkedin-api` Python package. Install into the Hermes venv:

```bash
/home/deeone/.hermes/venv/bin/pip install --no-deps linkedin-api
/home/deeone/.hermes/venv/bin/pip install --no-deps beautifulsoup4
/home/deeone/.hermes/venv/bin/pip install --no-deps soupsieve
```

**Note:** The system Python (3.14) already has `lxml` installed. The venv cannot build `lxml` from source, so `--no-deps` is required to avoid the build failure. The `linkedin-api` library works with the system `lxml`.

**Important:** Run the script with the venv Python, not system Python:
```bash
/home/deeone/.hermes/venv/bin/python /home/deeone/.hermes/skills/openclaw-imports/linkedin-cli/scripts/lk.py whoami
```

## Usage

- `lk whoami`: Display your current profile details.
- `lk search "query"`: Search for people by keywords.
- `lk profile <public_id>`: Get a detailed summary of a specific profile.
- `lk feed -n 10`: Summarize the top N posts from your timeline.
- `lk messages`: Quick peek at your recent conversations.
- `lk check`: Combined whoami and messages check.

## Troubleshooting

### "ModuleNotFoundError: No module named 'linkedin_api'"
The script must be run with the Hermes venv Python (`/home/deeone/.hermes/venv/bin/python`), not the system `python3`.

### "dict object has no attribute 'extract_cookies'" or empty profile returns
The `li_at` cookie may be expired. LinkedIn session cookies expire. Re-extract fresh cookies from your browser.

### Infinite redirects / login page redirect
The `li_at` cookie is expired or invalid. The `linkedin-api` library cannot refresh cookies — you must provide fresh ones.
## Alternative: Browser-based LinkedIn Access

If cookies don't work, use Lightpanda browser with CDP to access LinkedIn:
1. Start Lightpanda CDP: `lightpanda serve --host 127.0.0.1 --port 9222`
2. Configure Hermes: `hermes config set browser.engine lightpanda` and `hermes config set browser.cdp_url http://127.0.0.1:9222`
3. **Cookie injection via `document.cookie` does NOT work for LinkedIn** — LinkedIn requires full auth flow with email/password
4. For authenticated LinkedIn access, use a dedicated bot (e.g., LinkedIn-AI-Job-Applier-Ultimate) that handles the login form

**Pitfall from 2026-05-27 session:** Injecting `li_at` cookie via CDP eval (`document.cookie = '...'`) doesn't work because LinkedIn's auth involves multiple secure cookies across domains (`li_at`, `JSESSIONID`, `bcookie`, `li_gc`, `li_rm`, etc.) that can't be set via JavaScript. The browser's native cookie store must be used, which requires a full login flow. Use the dedicated job applier bot with email/password authentication instead.

## Known Limitations (2026-05-26)

The `linkedin-api` library (v2.3.1) has broken endpoints for social features:
- ✅ `whoami` — works, returns profile info
- ✅ `profile` — works for viewing other profiles
- ❌ `feed` — returns empty list (LinkedIn API changed)
- ❌ `search` — returns empty list (LinkedIn API changed)
- ❌ `messages` — returns empty dict (LinkedIn API changed)

For full LinkedIn interaction (feed, search, messages, job applications), use browser automation (Lightpanda/CDP with a dedicated bot) instead of this CLI.

## Authors
- Built by Fido 🐶