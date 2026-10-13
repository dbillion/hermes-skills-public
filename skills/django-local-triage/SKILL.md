---
name: django-local-triage
description: "Use when debugging Django projects locally."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [django, debugging, drf, channels, triage]
    related_skills: [systematic-debugging, test-driven-development]
---

# Django Local Triage

Companion to systematic-debugging Phase 1 for Django + DRF + Channels projects where the
failure is environmental (hangs, connection errors) or queryset-scoping rather than logic.

## 1. Hanging tests mean unreachable remote services until proven otherwise

When `pytest` stalls to timeout but code looks fine:

- Read settings for `DATABASES`, `CACHES`, `CHANNEL_LAYERS`, then read the active `.env`.
  A `DATABASE_URL` pointing at hosted Postgres and a `REDIS_URL` pointing at a docker
hostname or malformed hosted URL will hang local runs with no fast failure (health-check
`cache.get()` blocks).
- Build the tight loop on a local settings module: sqlite + locmem cache +
  `channels.layers.InMemoryChannelLayer`, e.g. `DJANGO_SETTINGS_MODULE=local_settings`.
- If that module lacks `TEMPLATES`, admin checks fail with `admin.E403` — copy the standard
  `TEMPLATES` block from main settings, one targeted addition, then re-run the loop.
- `No module named 'django_redis'` means a stale venv: reinstall requirements, re-run
  `manage.py check` until green (warnings only), then run the smallest test file.

Proven loop order: `manage.py check` -> smallest test module -> runserver -> curl `/api/health/`.

## 2. Confirm the canonical repo before Phase 1

When several checkouts exist, verify which repo + branch is live BEFORE investigating
(`gh repo list`, `git status` for ahead/behind and untracked env files). Starting on a stale
or skeleton copy wastes a full exploration cycle.

## 3. Scoped-queryset membership actions (diagnostic pattern, fix unverified)

Verified diagnosis from one session: a ViewSet whose `get_queryset()` returns only the
caller's own objects (e.g. `request.user.chat_rooms.all()`) combined with a membership action
(e.g. `join`) using `self.get_object()` can never succeed for non-members — it 404s
(`"No ChatRoom matches the given query."`) by construction. Sibling read actions using
unscoped querysets (e.g. `discovery`) keep working, which is the tell.

Suspected fix direction (NOT yet verified end-to-end): fetch the target unscoped inside the
action and enforce the real rule explicitly (auth + reject non-joinable types). Verify with
the token-based loop below before treating this as law.

## 4. Token-based role testing loop (DRF)

Mint tokens per role in the Django shell
(`rest_framework.authtoken.models.Token.get_or_create`), then curl each role against
profile/stats endpoints plus gated resources. 403 logged-out is correct behavior, not breakage.
Enumerate actual role values from the DB first — roles with zero users are a coverage gap no
endpoint test can catch without that step.
