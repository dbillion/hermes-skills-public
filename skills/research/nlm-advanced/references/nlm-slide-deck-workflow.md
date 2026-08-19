# NLM Slide Deck Workflow — Session Notes

## Profile Authentication
```bash
# Always use -p flag for profile targeting
nlm login -p <profile-name>          # login
nlm notebook list                    # list notebooks under profile
nlm studio status <notebook-id>     # check generation status
nlm download slide-deck <notebook-id> --id <studio-id> -o <output-path>
```

## Slide Deck Generation Sequence (verified)
1. `nlm login -p <profile>` — authenticate
2. `sleep 300` — MANDATORY 5-min wait before `slides create` to avoid RESOURCE_EXHAUSTED
3. `nlm slides create <notebook-id> --format detailed_deck --length default --confirm --focus "..."`
4. Poll with `nlm studio status <notebook-id>` until status = `completed`
5. `nlm download slide-deck <notebook-id> --id <artifact-id> -o <path>`

## Known Completed Artifacts (DSA SOLID Patterns notebook — ca2aa234)
| Artifact ID | Type | Status |
|---|---|---|
| 17fe1f89-6126-4b07-9353-c2bfb8fb09b4 | slide_deck | completed |
| 98fa17c8-48d5-4c63-bbad-40a3a026ccdd | slide_deck (McKinsey visual wonder) | completed |
| 4d4bf052-bcc1-4f81-a775-b97fac0b8e5c | slide_deck (academic) | completed |
| 35300d33-c6c8-4390-9c30-bb1e608ae4bb | report | completed |

## Rate Limit Behavior
- Slide deck creation = heaviest rate limit; first attempt always fails
- Retry after 5 min with same profile works
- Profile switching alone does NOT bypass the wait; still need sleep
- `studio status` may return "Could not retrieve" temporarily — retry after short delay

## Download Command Nuances
- notebook_id is POSITIONAL (not --notebook-id)
- --id specifies the studio artifact ID (from `nlm studio status`)
- No --profile flag on download — must auth via `nlm login -p` first
- Wrong artifact ID → "Download failed for slide_deck"