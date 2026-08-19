---
name: clerk-custom-auth
description: >-
  Wire Clerk authentication into NON-Next.js frontends (especially Angular SPA)
  and into backends with EXISTING custom auth (NestJS/Express JWT), as an SSO
  ADD-ON — without hardcoding keys. Covers the Angular package reality
  (@clerk/angular does NOT exist; use @clerk/clerk-js), the bun-installed
  `clerk` CLI location, and the gitignore + build-time-injector secret pattern.
  Use when the protected `clerk-setup` skill's Next.js/React-centric steps don't
  apply, or when adding Clerk alongside an existing auth system.
license: MIT
tags: [clerk, angular, nestjs, sso, secrets, auth]
globs:
  - "**/clerk.service.ts"
  - "**/auth/*.ts"
  - "**/inject-clerk-key.mjs"
---

# Clerk for Custom / Non-Next.js Auth (SSO Add-On)

This skill fills gaps the official `clerk-setup` skill leaves for Angular SPAs and
projects that already have their own auth. It is additive: Clerk is an SSO option,
not a replacement, unless the user explicitly wants a full swap.

## When to use
- Frontend is **Angular** (no `@clerk/angular` package exists — see below).
- Backend already has auth (NestJS `/api/auth/login` + JWT, Passport, etc.) and you
  want Clerk as an extra "Continue with Clerk" button.
- You need to inject Clerk keys into a build without committing them.

## CRITICAL: Angular package reality (2026)
`npm view @clerk/angular` and `@clerk/clerk-angular` both **404**. Clerk has no
dedicated Angular SDK. Use:
- **Client:** `@clerk/clerk-js` (vanilla SDK). Wrap in an Angular `ClerkService`
  (`providedIn: 'root'`). Drive imperatively — there is NO `ClerkProvider` component.
  ```ts
  import { Clerk } from '@clerk/clerk-js';
  this.clerk = new Clerk(environment.clerkPublishableKey);
  await this.clerk.load();
  this.clerk.mountSignIn(hostEl, { routing: 'virtual' });
  const token = await this.clerk.session.getToken();
  ```
- **Backend (NestJS/Express):** `@clerk/backend` (this one DOES exist —
  `npm view @clerk/backend version` returns a real version). Use
  `createClerkClient({ secretKey })` + `clerk.verifyToken(token)` in a guard.

## `clerk` CLI is installed via BUN, not npm
`npm i -g @clerk/cli` / `@clerk/clerk-cli` both 404. On this user's machine the CLI
is at `~/.bun/bin/clerk` (v2.2.0). Prepend to PATH:
```bash
export PATH="$HOME/.bun/bin:$PATH"
clerk whoami                       # email + linked app (linked:null if none)
clerk apps list --json             # pick app_id
clerk link --app app_xxx
clerk env pull                     # writes CLERK_PUBLISHABLE_KEY + CLERK_SECRET_KEY to .env.local
```
`clerk env pull` writes to the **current directory's** `.env.local` — `cd` into the
specific sub-project first, or keys land in the wrong folder.

## NEVER HARDCODE KEYS (user-corrected, hard rule)
Pasting even a publishable key as a literal into a tracked source file was explicitly
rejected ("why will you hard code it in 2026?"). Correct pattern for frontends that
can't natively read `.env.local` at build (Angular):
1. `clerk env pull` → gitignored `.env.local`.
2. Build-time injector script (run via `prebuild`) reads the key and writes the
   framework env file.
3. **Gitignore the generated env file** so the key can never commit.

See `scripts/inject-clerk-key.mjs` (template) and wire
`"prebuild": "node scripts/inject-clerk-key.mjs"` in package.json. Add both
`src/environments/environment.ts` and `.env.local` to `.gitignore`. Verify:
`git add -A --dry-run | grep environment.ts` must return nothing.
Secret (`CLERK_SECRET_KEY`) goes ONLY in the backend's gitignored `.env` (append,
never commit). The file-read tool refuses `.env*` by design — confirm presence with
`grep -oE "VARNAME="` (names only), never print values.

## SSO add-on bridge (keep existing auth)
1. Angular: "Continue with Clerk" button → `clerk.mountSignIn` → on success
   `clerk.session.getToken()`.
2. POST that token to `POST /api/auth/clerk` on the backend.
3. Backend: `clerk.verifyToken(token)` → find/create local user by clerkId/email →
   **issue your own JWT**. Existing JWT guard keeps working; Clerk is optional.

## Pitfalls
- Don't `npm i @clerk/angular` — it 404s. Use `@clerk/clerk-js`.
- Don't look for `ClerkProvider` in Angular — drive `@clerk/clerk-js` from a service.
- Don't hardcode keys in `environment.ts` — use the injector + gitignore.
- `clerk` CLI not on npm PATH — it's bun at `~/.bun/bin/clerk`.
- `clerk env pull` target dir = CWD; `cd` into the right sub-project first.

## See also
- `clerk-setup` (protected, hub-installed) — Next.js/React quickstarts, `clerk doctor`.
- `clerk-backend-api` — raw Clerk REST explorer.
- Memory rule: "Never hardcode/echo secrets" — this skill is the executable form.
