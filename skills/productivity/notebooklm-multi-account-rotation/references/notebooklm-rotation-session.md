# NotebookLM rotation session notes

## Collaborator email list (from account switcher)
- <COLLABORATOR_EMAIL>
- <COLLABORATOR_EMAIL>
- <COLLABORATOR_EMAIL>
- <COLLABORATOR_EMAIL>
- <COLLABORATOR_EMAIL>
- <COLLABORATOR_EMAIL>
- <COLLABORATOR_EMAIL>

## Observed errors
- `Rate limited — API error (code 8)` when generating artifacts on owner account
- `Could not retrieve notebook sources` when non‑owner accounts lack edit access
- `PERMISSION_DENIED` when trying to invite on a notebook not owned by current profile
- `nlm share batch` with comma list returned `INVALID_ARGUMENT` — per‑email invites worked

## Invite pattern (per email)
```
nlm share invite <notebook_id> <email> --role editor
```

## Verification
```
nlm share status <notebook_id>
```
