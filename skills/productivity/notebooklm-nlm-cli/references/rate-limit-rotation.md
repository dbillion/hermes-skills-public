# Multi-profile rate-limit rotation for NotebookLM (nlm)

NotebookLM applies tight per-account quota to uploads and studio generation.
Symptoms: `429` / rate-limit errors after a handful of `source add` or
`slides create` calls. Fix: spread the work across all your configured
profiles by inviting them as editors and rotating `--profile` per call.

## Step 1 — enumerate profiles + emails
```
ls -1 ~/.notebooklm-mcp-cli/profiles/
# each dir is a profile handle
grep -rhoE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" \
  ~/.notebooklm-mcp-cli/profiles/<handle>/ 2>/dev/null
```
Alternatively `nlm doctor` lists profiles with health; `nlm config` shows
the active one. Emails are NOT printed by `nlm` directly — read the
credential dirs.

## Step 2 — invite each as editor (run from main profile)
```
for email in <YOUR_EMAIL> <COLLABORATOR_EMAIL> ...; do
  nlm share invite "<nbid>" "$email" --role editor --profile <main>
done
```

## Step 3 — rotation loop in any script / subagent
Maintain an ordered list, e.g.:
```
PROFILES=(oludayo35 dayozoe dayo4ai oludayoadeoyeabiodun \
          adeoyeoludayo53 adeoye55er architectlead7 dayoglorious mentoratechies)
p=0
for f in *.pdf; do
  prof=${PROFILES[p % ${#PROFILES[@]}]}
  out=$(nlm source add "<nbid>" --file "$f" --title "$f" --profile "$prof" --wait --json)
  if echo "$out" | grep -qiE "429|rate.?limit"; then
    # advance one and retry THIS file only
    p=$((p+1)); prof=${PROFILES[p % ${#PROFILES[@]}]}
    nlm source add "<nbid>" --file "$f" --title "$f" --profile "$prof" --wait --json
  else
    p=$((p+1))
  fi
done
```

## Notes
- This is the user's own pattern (emerged this session). It lets 80+ uploads
  or many deck generations complete by borrowing quota from N editor accounts.
- Subagents inherit the same profile list; pass it explicitly in their context.
- `delegation.max_concurrent_children` caps at 3 — dispatch DSA-style fan-outs
  in waves of 3, each wave rotating profiles internally.
- Editor invites are one-time per notebook; once invited, the profiles can be
  used for `--profile` on that notebook indefinitely.
