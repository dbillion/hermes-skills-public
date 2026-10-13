---
name: angular-nestjs-fullstack-debugging
description: >-
  Debugging patterns for Angular (SpartAN/Material) frontends wired to a NestJS +
  TypeORM backend. Covers the three highest-frequency failure modes seen in this
  class of app: (1) dead routerLink paths silently swallowed by the `**` catch-all,
  (2) role/ownership mismatches between frontend guards and backend enforcement,
  (3) phantom LSP "Cannot find module" errors that are NOT real build failures.
  Use whenever a click does nothing, a route 404s, a guard blocks the wrong user,
  or an edit "didn't take" — and you must verify against the REAL running app, not
  guess. Pair with angular-best-practices / angular-best-practices-spartan for
  component-level guidance.
license: MIT
tags: [angular, nestjs, typeorm, debugging, routing, auth, ownership]
globs:
  - "**/app.routes.ts"
  - "**/*.controller.ts"
  - "**/*.service.ts"
  - "**/*.component.ts"
  - "**/*.html"
---

# Angular + NestJS Fullstack Debugging

Recurring, high-signal failure modes when an Angular SPA fronts a NestJS/TypeORM API.
Each pattern below is a *verified* debugging recipe — run the checks, don't assume.

## Pattern 1 — "Clickable" element does nothing (dead routerLink)

**Symptom:** A card/button with `[routerLink]` or `router.navigate([...])` appears
interactive but lands you on the home page (or nowhere). No console error.

**Root cause:** The target path has **no matching route**. Angular's catch-all
`{ path: '**', redirectTo: '/' }` silently swallows unknown paths, so the navigation
"works" but redirects to home. The link was built against a route name that was
renamed (e.g. `articles/:id` → `knowledge/:id`) but the link literals were never
updated.

**Debug recipe (deterministic):**
1. Find the route table: `app.routes.ts`. List every registered `path` (including
   nested `children`). Note the REAL path for the target (e.g. `knowledge/:id`,
   `knowledge/edit/:id`).
2. Grep the whole frontend for the stale literal:
   `search_files` pattern `['/articles'|routerLink.*articles|navigate\(\['/articles`
   across `src/`. Cover BOTH forms:
   - Template: `[routerLink]="['/articles', article.id]"`
   - TS: `this.router.navigate(['/articles', id])`, and string-built URLs in
     `shareArticle`/clipboard fallbacks (`` `/articles/${id}` ``).
3. Replace every stale literal with the real route from step 1.
4. **Verify in the BUILT bundle**, not just source: after `ng build`, grep
   `dist/**/*.js` for the stale path. Confirm it's gone (backend `/api/articles`
   URLs are fine — those are API calls, not router paths).

**Gotcha:** The same bug often hides in MANY places at once (search cards, edit
post-save redirect, footer links, share URLs). Fix all of them in one pass or the
user will hit the next dead link five minutes later.

## Pattern 2 — Role / ownership mismatch (frontend guard vs backend)

**Symptom:** A user is blocked who shouldn't be, or can edit/delete something they
shouldn't. Or "regular user can't create" / "viewer can do anything".

**Debug recipe (verify against the LIVE API with curl, never by reading code alone):**
1. Note the role enum on BOTH sides. Frontend `UserRole` enum and backend
   `UserRole` enum (often a `simple-enum` DB column) MUST list the same values.
   A role string the backend doesn't recognize → registration/seed fails or silently
   defaults to the enum's fallback (e.g. `VIEWER`).
2. Default-role trap: `auth.service.register` often does
   `role: role || UserRole.VIEWER`. If self-registration sends no role, users become
   read-only viewers. Change the default to the intended role (e.g. `AUTHOR`) when the
   product wants "any signed-up user can post".
3. End-to-end ownership test against the running API (copy this shape):
   ```
   B=http://localhost:3000/api
   # register -> check role
   curl -s -X POST $B/auth/register -H 'Content-Type: application/json' \
     -d '{"email":"u@t.dev","username":"u","password":"password123","firstName":"N","lastName":"U"}' \
     | python3 -c "import sys,json;u=json.load(sys.stdin)['user'];print(u['role'])"
   # login as A, create article
   TA=$(curl -s -X POST $B/auth/login -H 'Content-Type: application/json' -d '{"email":"a@t.dev","password":"password123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
   ART=$(curl -s -X POST $B/articles -H "Authorization: Bearer $TA" -H 'Content-Type: application/json' -d '{"title":"t","content":"c","categoryId":"<UUID>","isPublished":true}' | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['id'])")
   # login as B (different author), attempt edit -> expect 403
   TB=$(curl -s -X POST $B/auth/login -H 'Content-Type: application/json' -d '{"email":"b@t.dev","password":"password123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
   curl -s -o /dev/null -w "edit-others: %{http_code}\n" -X PATCH $B/articles/$ART -H "Authorization: Bearer $TB" -H 'Content-Type: application/json' -d '{"title":"x"}'
   # owner edit -> expect 200 ; admin edit -> expect 200
   ```
   Expected social-media model: author edits/deletes OWN only (403 on others'),
   admin overrides all (200). Enforce in the **service** (not just the controller),
   returning `ForbiddenException` when `user.id !== article.authorId && user.role !== 'admin'`.
4. Seeding an admin: add the admin user to the seed script (role `admin`) so it
   exists without manual DB edits. The seed script reads `DATABASE_URL` from env —
   export it from `.env` before running: `export DATABASE_URL="$(grep '^DATABASE_URL=' .env | head -1 | cut -d= -f2-)"`.

## Pattern 3 — Phantom LSP errors (don't trust them)

**Symptom:** After editing a `.ts` file, the LSP reports a wall of
`Cannot find module '@angular/core/primitives/di'` / `@angular/common/http` /
`@spartan-ng/helm/button` with `moduleResolution` hints, plus `Property 'x' does not
exist on type 'unknown'`.

**Root cause:** The standalone LSP client uses the wrong `moduleResolution` and cannot
resolve the project's Angular/SpartAN type packages. These are NOT real errors.

**Discipline:**
- Treat LSP diagnostics as unreliable for this stack. The source of truth is the
  real compiler: `npx ng build --configuration development` (frontend) and
  `npx nest build` (backend). If those pass, the edit is good.
- When a "real" error like `Cannot find name 'ApiBearerAuth'` appears, first confirm
  the import is actually missing in the file (read the import block) before adding it
  — don't blindly trust the diagnostic line number.
- A patch is "clean" when `ng build` / `nest build` exit 0, regardless of lingering
  LSP noise.

## Cross-cutting rules

- **Read before you edit.** Trace the full chain (template link → route table →
  component → service → HTTP call → backend controller → service → DB) before
  changing anything. Editing one layer while guessing about another produces
  duplicate decorators, wrong field mappings, and rework.
- **Verify, don't label.** After a fix, prove it with a real build + (for API
  changes) a real curl against the running server. "It compiles" is necessary but not
  sufficient for behavior claims.
- **Boot-crash fix shape:** if the API won't start, read the module that fails to
  inject its repository — almost always a missing `TypeOrmModule.forFeature([Entity])`
  in the `*module.ts`. Add it, rebuild, restart.
- **Commit a tested state** before moving to the next unrelated change so you can
  revert a slice cleanly.

## references/
- `references/route-mismatch-checklist.md` — copy-paste grep + bundle-verify commands
  for Pattern 1.
- `references/ownership-curl-suite.md` — full ready-to-run curl suite for Pattern 2.
