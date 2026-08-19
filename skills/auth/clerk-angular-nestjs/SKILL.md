---
name: clerk-angular-nestjs
description: >-
  Add Clerk authentication to an Angular (SPA) front end + NestJS (or any
  Node) back end. Covers the REAL package layout (there is NO @clerk/angular
  SDK — use @clerk/clerk-js on the client and @clerk/backend on the server),
  the clerk CLI location, the additive-SSO "bridge" pattern, and the
  mandatory no-hardcode-key rule. Use when a project pairs Angular + NestJS
  and the user says "add Clerk" / "Clerk SSO" / "sign in with Clerk".
license: MIT
metadata:
  author: dbillion
  version: "1.0.0"
tags: [clerk, angular, nestjs, sso, auth]
globs:
  - "**/auth*.ts"
  - "**/*clerk*.ts"
  - "**/auth/**"
---

# Clerk for Angular (SPA) + NestJS (API)

`clerk-setup` covers Next/React/Vue/etc. but is MISSING the Angular path.
This skill fills that gap. It was written after a real integration where
`@clerk/angular` returned 404 on npm and the agent initially hardcoded the
publishable key (user rejected that hard).

## Critical fact: there is NO @clerk/angular package

As of Clerk Core 2, the dedicated Angular SDK was dropped. Verify before
assuming:
```
npm view @clerk/angular version      # -> 404 (does not exist)
npm view @clerk/clerk-angular version # -> 404 (does not exist)
npm view @clerk/clerk-js version     # -> 6.x (USE THIS on the client)
npm view @clerk/backend version      # -> 3.x (USE THIS on the server)
```
- **Client (Angular):** `@clerk/clerk-js` (the vanilla JS SDK). Wrap it in
  an Angular `ClerkService` (`providedIn: 'root'`) that calls `new Clerk(pk)`
  then `clerk.load()`, `clerk.mountSignIn(host)`, `clerk.session.getToken()`.
- **Server (NestJS):** `@clerk/backend` → `createClerkClient({ secretKey })`.
  Use `clerk.verifyToken(token)` to validate a session token.

## The clerk CLI is NOT on npm here

`npm i -g @clerk/cli` and `@clerk/clerk-cli` both 404. The CLI is installed
via **bun** at `~/.bun/bin/clerk` (v2.2.0 observed). Add to PATH:
```
export PATH="$HOME/.bun/bin:$PATH"
clerk --version
```
Flow that works:
```
clerk whoami                      # shows logged-in email + linked app
clerk apps list --json            # pick the app_id to link
clerk link --app app_xxx          # links project, writes .env.local via pull
clerk env pull                    # writes CLERK_PUBLISHABLE_KEY + CLERK_SECRET_KEY
```
`clerk env pull` writes to the **current dir's** `.env.local` (e.g.
`knowledge-sharing-app/.env.local`). The secret key there is then copied
(server-only) into the API's gitignored `.env`.

## HARD RULE — never hardcode the publishable key (user correction, 2026)

Even though `pk_test_...` is client-safe, do NOT paste it as a literal into a
committed source file. The user said: *"why will you hard code it in 2026?
thats stupid, dont you read from your security instructions about hardcoding
keys."* Correct pattern:
1. `clerk env pull` writes keys into a **gitignored** `.env.local`.
2. Add a build-time inject step (npm `prebuild` script) that reads the key
   from `.env.local` and writes it into the Angular environment file.
3. **Gitignore the generated environment file** so the key is never committed.
4. Verify before pushing: `git grep -l "pk_test" HEAD` must return NOTHING.

Example `scripts/inject-clerk-key.mjs`:
```js
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
const env = existsSync('.env.local') ? readFileSync('.env.local','utf8') : '';
const m = env.match(/CLERK_PUBLISHABLE_KEY=([^\s]+)/);
const key = m ? m[1] : '';
writeFileSync('src/environments/environment.ts',
  `export const environment = { production: false, clerkPublishableKey: ${key ? `'${key}'` : "''"} };\n`);
```
Wire it: `"prebuild": "node scripts/inject-clerk-key.mjs"` in package.json,
and `.gitignore`: `src/environments/environment.ts` + `/.env.local`.
NOTE: inside an app-dir `.gitignore`, the path must be `src/environments/...`
NOT `/environments/...` (leading `/` anchors wrong → file still gets committed
with the key). See Pitfalls.

## Additive SSO bridge (Clerk is an ADD-ON, not a replacement)

User guidance: *"clerk works for single sign-on, its an addition, it doesnt
replace it."* So keep the existing local auth (email/password + our JWT) and
add Clerk as a second path:
1. Angular login page: keep the local form; ADD a "Continue with Clerk SSO"
   button + a `<div #clerkSignIn>` host. On Clerk success, read
   `clerk.session.getToken()` and POST it to the backend bridge.
2. NestJS: add `POST /api/auth/clerk` that verifies the Clerk token with
   `@clerk/backend`, then **find-or-create** a local user (match by `clerkId`
   or email) and issues OUR OWN JWT (same shape as local login). Add a
   nullable `clerkId` column to the User entity for linking.
3. Now the rest of the API is unchanged — it still validates our JWT via the
   existing `JwtAuthGuard`. Clerk only brokers the initial identity.

Bridge service sketch (NestJS):
```ts
const claims = await this.clerk.verifyToken(token, { secretKey });
let user = await repo.findOne({ where: [{ clerkId: claims.sub }, { email: claims.email }] });
if (!user) { user = repo.create({ clerkId: claims.sub, email: claims.email ?? `${claims.sub}@clerk.local`, ... }); await repo.save(user); }
const access_token = this.jwtService.sign({ sub: user.id, email: user.email, role: user.role });
return { access_token, refresh_token, user };
```
Pitfall: wrap `clerk.verifyToken` in try/catch and rethrow
`UnauthorizedException('Invalid Clerk token')` — otherwise a bad token bubbles
as HTTP 500 instead of 401.

## Pitfalls

| Issue | Fix |
|-------|-----|
| `@clerk/angular` 404 on npm | Use `@clerk/clerk-js` directly in an Angular service |
| `clerk` CLI not found via npm | It's at `~/.bun/bin/clerk`; `export PATH="$HOME/.bun/bin:$PATH"` |
| Publishable key hardcoded in committed file | Inject from gitignored `.env.local` at build; gitignore the output file |
| gitignore `/environments/environment.ts` doesn't ignore | Inside app-dir .gitignore use `src/environments/environment.ts` (no leading `/`) |
| Bad Clerk token → HTTP 500 | Catch `verifyToken` error, throw `UnauthorizedException` (→ 401) |
| `clerk.mountSignIn(host, {routing:'virtual'})` type error | Call `clerk.mountSignIn(hostDiv)` with no props; listen via `clerk.addListener` |
| `mountSignIn` wants `HTMLDivElement` not `HTMLElement` | Pass `viewChild<ElementRef<HTMLDivElement>>` `.nativeElement` |
| Secret key leaked to client | Only `pk_*` goes to the SPA; `sk_*` stays in server `.env` |

## Verify before claiming done
- `ng build` (or `nest build`) EXIT=0.
- `git grep -l "pk_test" HEAD` → empty.
- `curl -X POST /api/auth/clerk -d '{"token":"bad"}'` → HTTP 401 (not 404/500).
- Swagger (`/api/docs-json`) lists `auth/clerk`.
