---
name: ks-knowledge-sharing-debugging
description: >-
  Debugging and safe-editing playbook for the ks-knowledge-sharing repo (Angular 20
  Spartan/Tailwind v4 frontend + NestJS/TypeORM/Neon backend, owner dbillion). Covers the
  FE<->BE wire (API_CONFIG -> service -> guard -> route -> component), the repo's known
  silent-mock/stub anti-patterns, the social-media role model (viewer/author/admin), and a
  live-curl verification recipe. Load this BEFORE editing any file in this repo.
user-invocable: false
---

# ks-knowledge-sharing — debugging & safe-editing playbook

Repo: `git@github.com:dbillion/ks-knowledge-sharing.git`. Two packages at the repo root:
`knowledge-sharing-app/` (Angular, SpartAN UI, `ng build`) and `knowledge-sharing-api/`
(NestJS, `nest build`). Branch in active use: `tailwind-spartan`.

## RULE ZERO — trace the wire before you edit

The user explicitly corrected jumping straight into edits: "before editing, read about the
frontend and backend and see how they link, then based on the task." Editing a controller,
service, or component without first mapping the call chain corrupts files (e.g. a duplicate
`@Post()` decorator or a phantom import). Always do this first:

1. Find the frontend entry point: grep the component for the service call
   (`knowledgeService.createArticle`), then open that service method.
2. Read `core/config/api.config.ts` — `baseUrl` (e.g. `http://localhost:3000/api`) tells you
   the real backend path (`/articles` -> `POST /api/articles`).
3. Open the matching backend controller + service. Confirm the DTO shape the frontend sends
   (`categoryId`) matches what the backend expects (it may store it as `category`).
4. Read the guards on the route: `authGuard` (frontend-only, checks localStorage signal —
   does NOT hit the API) and `roleGuard` (reads `route.data.roles` vs `currentUser.role`).
5. Confirm the backend method has `@UseGuards(JwtAuthGuard)` if it needs the user, and reads
   `req.user` (set by the JWT strategy), not a custom `@User()` decorator.

Only after steps 1-5 should you patch. Re-read the WHOLE file (not a paginated slice) before
overwriting or patching a large block — the LSP may show phantom "Cannot find name" errors for
imports that ARE present (e.g. `ApiBearerAuth` from `@nestjs/swagger`); trust `nest build`
over the LSP.

## Known repo anti-patterns (verify, don't trust)

This repo ships SILENT mocks/stubs that look finished but aren't. Always prove the real path:

| Symptom | What's actually stubbed | Real fix |
| --- | --- | --- |
| Create article posts `categoryId: "cat1"` -> backend 400 "must be a UUID" | `CategoryService.getActiveCategories()` returned mock `cat1..cat5` IDs | Make it call live `/api/categories`; backend `/api/categories` GET was itself a stub returning `[]` -> implement `CategoriesService.findAll()` (real TypeORM) + wire controller |
| "New Article" button does nothing / 404 | `<button routerLink>` is a no-op; footer linked `/articles/new` (no route) | Use `<a hlmBtn routerLink>`; point to the real route (`/knowledge/create`) |
| Create article throws `mat-form-field must contain a MatFormFieldControl` | Leftover Angular Material in a SpartAN-rewritten page | Replace `<mat-select>`/`<mat-form-field>` with native `<select hlmInput>`/`<input hlmInput>` |
| API won't boot (process exits on start, `nest build` was fine) | A module provides a service that injects a repository but the module lacks `TypeOrmModule.forFeature([Entity])` | Add `TypeOrmModule.forFeature([Entity])` to that module's `imports` |
| Self-registered user can't create/edit | `auth.service.register` does `role: role || UserRole.VIEWER` (or other read-only default) and register sends no role | Default register role to the working role, e.g. `UserRole.AUTHOR`; the DB `simple-enum` column must list that value |

## Social-media role model (verified working state)

- **viewer** = not logged in. Public GET endpoints work; create/edit/delete/publish require
  JWT and are blocked. No DB row — just absence of a token.
- **author** = any self-registered user (`role` defaults to `author`). CRUD on OWN articles,
  can read everyone's. CANNOT touch others'.
- **admin** = seeded via `scripts/seed.mjs` (`admin@ks.dev`, `role: 'admin'`). Full override:
  edit/delete ANY article + category-management route (admin-only in `app.routes.ts`).

Ownership enforcement lives in the service:
```ts
if (user.role !== 'admin' && article.authorId !== user.id)
  throw new ForbiddenException('You can only modify your own articles');
```
The create endpoint MUST set `authorId` from `req.user.id` (never trust a client-supplied id)
and map `categoryId` -> the `category` column if the entity stores it there.

Frontend `canEdit`/`canDelete` must mirror this: `user.role === 'admin' || article.authorId === user.id`.
(Legacy code had `canDelete = user?.role === 'admin'` only — that wrongly blocked authors from
deleting their own posts.)

## Live verification recipe (the proof, not a claim)

See `references/role-ownership-recipe.md` — seed an admin, then curl-verify:
register->author, ada create->201, different author edit/delete->403, owner edit->200,
admin override->200. `nest build` + `ng build` must both be clean first.

## Build & run

- Backend: `cd knowledge-sharing-api && npx nest build && npx nest start` (port 3000).
  The API loads `.env` via `ConfigModule` automatically.
- Frontend: `cd knowledge-sharing-app && npx ng build --configuration development`.
- Seed: `export DATABASE_URL="$(grep '^DATABASE_URL=' .env | head -1 | cut -d= -f2-)" && node scripts/seed.mjs`
  (the seed script does NOT auto-load `.env`; the shell must export it).
- Git push from this host is BLOCKED (GitHub pack upload stalls) — use `git bundle` and push
  from the egress machine. Commit locally on `tailwind-spartan` with `scripts/committer` if
  present, else `git add -A && git commit`.
