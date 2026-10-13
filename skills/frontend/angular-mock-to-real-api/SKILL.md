---
name: angular-mock-to-real-api
description: Rewrite an Angular app's mocked/in-memory services to call a real backend API (HttpClient). Covers the predictable breakage chain — DTO/property renames that ripple into templates, duplicate interceptor/service files that shadow the real implementation, and phantom TS errors from stale incremental build caches. Use when the user says "connect the frontend to the real API", "kill the mocks", or "wire services to the backend".
license: MIT
metadata:
  author: ks-knowledge-sharing project learnings
  version: '1.0'
---

# Angular: Mock -> Real API

Recurring task for this user (Angular 20 frontend over a NestJS API). The refactor is mechanical but the build breakage is a fixed set of traps — fix them all in one pass.

## Sequence
1. **Add an API config constant** (e.g. `src/app/core/config/api.config.ts` exporting `API_CONFIG.baseUrl = 'http://localhost:3000/api'`). Keep it out of components so you can swap to a deployed URL in one place.
2. **Inject `HttpClient`** into each service and replace mock `of([...])` / hardcoded arrays with real `http.get/post/patch`. Confirm `provideHttpClient()` is in `app.config.ts` (it usually is).
3. **Align DTOs to the real response shape.** Inspect the live endpoint first:
   `curl -s 'http://localhost:3000/api/articles?limit=1'` — note exact field names and types. The backend field names are authoritative; change the Angular interface to match, not the other way around.
4. **Map response -> component model** in the service (so components don't change), OR update components. Prefer mapping in the service to limit blast radius.

## Trap 1 — property rename ripples into templates
If the backend renames a field (e.g. `categoryId` -> `category`, or changes type from number to UUID string), every `.categoryId` property access breaks — including in `.html` templates and `formValue.categoryId` passed to create calls.
- Grep the whole `src` for the old name: `grep -rn "categoryId" src --include=*.ts --include=*.html`.
- Fix property *reads* (`article.categoryId` -> `article.category`). Leave reactive-form `formControlName="categoryId"` and `form.get('categoryId')` alone — those are control keys, not the article property.
- Templates: `<img [src]="getPlaceholderImage(article()!.categoryId)">` -> `article()!.category`.

## Trap 2 — duplicate interceptor/service shadows the real one
A project can have BOTH `auth.interceptor.ts` (Angular default, 444B, references a `refreshToken()` that no longer exists) AND `auth-interceptor.ts` (hyphen, the one `app.config.ts` actually imports). The unused one still gets compiled by `tsc` (`src/**/*.ts`) and throws a phantom error.
- Find duplicates: `find src -name "auth*.ts"`.
- Delete the dead duplicate (`rm` the hyphen file + its `.spec.ts`) if `app.config.ts` imports the other. The live error "Property 'refreshToken' does not exist" on a line number beyond the real file's length is the tell.

## Trap 3 — phantom TS errors from stale incremental cache
After fixing everything, `tsc --noEmit` / `ng build` may STILL report errors that reference lines you already edited (e.g. "categoryId does not exist" on a line now reading `category`). This is stale `.tsbuildinfo` / `.angular` cache.
- Nuclear clear: `find . -name "*.tsbuildinfo" -not -path "*/node_modules/*" -delete; rm -rf .angular node_modules/.cache; rm -rf dist`.
- Then rebuild. If `ng build --no-aot` still fails, run `npx tsc --noEmit -p tsconfig.app.json` to get the true error list (bypasses the bundler).
- A real syntax error (e.g. a dangling `)` left by a half-applied patch) will show as `TS1128`/`TS1005` at a specific line — read that file region, don't trust the earlier phantom lines.

## Verification
- `npx tsc --noEmit -p tsconfig.app.json` must be clean (empty output).
- `npx ng build --configuration development` must exit 0. Template *warnings* (e.g. `controlFlowPreventingContentProjection`) are non-blocking; only `error` lines block.
- Optional runtime check: serve the app (`ng serve`) and confirm a component fetches from the live API (Network tab / curl the served index). At minimum, confirm the service code references the real `API_CONFIG.baseUrl` + correct paths and the backend returns the expected shape.

## Commit each slice
Per the maker/checker loop: after a verified build, commit the frontend wiring as its own commit before moving to the next screen/feature. Don't batch unrelated slices.
