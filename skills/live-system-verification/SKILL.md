---
name: live-system-verification
description: "Use when verifying a running multi-service system."
---

# Live System Verification

Verifying a RUNNING system (frontend + backend + services) is a different class from checking a code tree. Probe the live processes; never assume they serve your edited tree.

## 1. Confirm which code each process serves

When multiple checkouts, containers, or build copies exist, a probe result is meaningless until you know WHAT code answered it. Before trusting any result against a live server:

```bash
ss -ltnp | grep <port>          # find the pid holding the port
readlink /proc/<pid>/cwd        # which checkout the process runs from
```

If the server runs from a different copy than the one being edited, restart or re-point it before drawing conclusions.

## 2. Separate environment mismatch from code bugs

When a client shows empty/error but the API returns good data when probed directly, probe the exact URL the client uses before touching code. `curl` exit 7 (connection refused) against that URL proves an environment/config mismatch, not a code bug.

Do NOT 'fix' tracked config to suit an ad-hoc local setup when the supported deployment needs the committed value (e.g. frontend `NEXT_PUBLIC_*` vars bake in at build time, so a container deployment needs its committed URL even if bare-metal dev ports differ). Document the required env override instead of editing the file.

## 3. Triage dead routes by inbound links

A 404 on a route is only a bug if something links to it. Before treating it as a defect, search all `href`, `Link`, `router.push`, and API-call targets for references. Routes with zero inbound links (index roots, legacy paths, partial segments like `/checkout` when only `/checkout/success` is linked) are non-issues — record and move on.

## 4. Diagnose client-rendered empty states

A page can return SSR 200 with correct shell HTML yet render 'no data' after hydration. The triage chain is: (a) confirm the API has data via direct probe, (b) read the page's fetch code for filters and base URL, (c) check the base URL resolves from the browser's environment. An aggressive default filter or a dead base URL are the two usual causes; both are verified without editing code.

## 5. Stop verifiers whose question is already answered

When parallel checkers thrash on wrong paths while first-hand evidence already covers their goal, stop or redirect them rather than letting them burn budget. If their answer would add no new information, end the task.
