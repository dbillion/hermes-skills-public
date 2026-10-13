# requests
_Python HTTP library for humans_

## 1. Overview
- Wraps urllib3 to make HTTP calls read like plain Python.
- Handles sessions, redirects, cookies, and JSON encoding for you.
- One function per HTTP verb: get, post, put, delete, etc.

> **Analogy:** Think of it like a phone: you dial a number (URL) and say what you want (verb), and it hands back whatever the other side says.

## 2. Core Components
| Name | Purpose | Example |
|---|---|---|
| Session | Persist cookies/headers across calls | `s = requests.Session()` |
| Response | Holds status, headers, body | `r.status_code, r.json()` |
| adapters | Control retries/connection pooling | `HTTPAdapter(max_retries=3)` |

## 3. Code Examples
**GET request**
```
import requests
r = requests.get('https://api.github.com')
print(r.status_code)
```
**POST with JSON**
```
r = requests.post(url, json={'a': 1})
```
**Custom headers**
```
r = requests.get(url, headers={'Authorization': 'Bearer TOKEN'})
```
## 4. Conventions
| Pattern | Example |
|---|---|
| Import alias | import requests as req (rare, usually unaliased) |
| Session reuse | with requests.Session() as s: ... |

## 5. Setup
```
pip install requests
```

## 6. How It Resolves Things
1. Explicit function args (headers=, params=)
2. Session-level defaults
3. Environment variables (e.g. proxies)

## 7. Best Practices
- Always set a timeout - requests never times out by default.
- Reuse a Session for multiple calls to the same host.
- Check r.raise_for_status() instead of manually checking status codes.

## 8. Common Errors & Solutions
| Error | Cause | Fix |
|---|---|---|
| ConnectionError | No network / wrong host | Check URL and network access |
| Hangs forever | No timeout set | Pass timeout=5 |
| JSONDecodeError | Response body isn't JSON | Check r.text before calling r.json() |

## 9. Quick Revision Checklist
- [ ] requests.get/post/put/delete for HTTP verbs
- [ ] r.status_code, r.json(), r.text on the response
- [ ] Use Session() to persist cookies/headers
- [ ] Always set timeout=
- [ ] raise_for_status() to fail fast on errors