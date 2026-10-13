---
name: angular-debug-patterns
description: Angular debug/fix patterns for ks-knowledge-sharing (dbillion). Covers form traps, routerLink gotchas, Material→SpartAN migration, API wiring, and headless browser verification.
trigger: "Angular app maintenance, form debugging, guard issues, or Material→SpartAN migration on ks-knowledge-sharing"
---

# Angular Debug & Fix Patterns

Class-level Angular patterns for this user's projects (ks-knowledge-sharing / dbillion).

## Forms

### `canSubmit` must be a method, not a computed signal
Angular `computed()` only tracks signal inputs. `FormGroup` is NOT a signal.
```ts
// WRONG — never updates after user types
readonly canSubmit = computed(() => this.articleForm.valid);

// RIGHT — recomputes on every call
canSubmit(): boolean {
  return this.articleForm.valid;
}
```
Always verify with a headless Playwright test: fill form, assert button state flips correctly.

### Form double-submit prevention
Never put both `type="submit"` AND `(click)="handler()"` AND `(ngSubmit)="handler()"` on the same button/form combo. Pick one:
- `(ngSubmit)` on `<form>` + `type="submit"` on button (Angular-native)
- OR `(click)="handler()" type="button"` on button (no ngSubmit on form)
Always verify which actually fires with a headless browser before declaring a form "working."

## Router Links

### `routerLink` on `<button>` does NOT work
Angular router ignores `routerLink` on native `<button>` elements. Fix:
```html
<!-- WRONG — no-op -->
<button routerLink="/knowledge/create">New Article</button>

<!-- RIGHT -->
<a hlmBtn routerLink="/knowledge/create">New Article</a>
```
This affects header logos and any nav buttons. Always verify with a headless click test.

## Guards & Roles

### Role guard widening
Seeded users (e.g. role=`author`) are often blocked by `roleGuard` that only allows `admin|editor`.
```ts
// app.routes.ts — add the actual role
{ path: 'knowledge/create', component: ArticleCreateComponent,
  data: { roles: ['admin', 'editor', 'author'] }  // added 'author'
```
Always verify with a headless login as that role + navigate to the protected route.

## Material → SpartAN Migration

### `mat-form-field must contain a MatFormFieldControl` (runtime)
When `<mat-form-field>` wraps a non-Material control (e.g. `hlmInput`, native `<input>`), Angular throws at runtime. The build passes (AOT doesn't catch it) but runtime crashes.
```html
<!-- WRONG — crashes at runtime -->
<mat-form-field appearance="outline">
  <input hlmInput formControlName="title" />
</mat-form-field>

<!-- RIGHT — no mat-form-field wrapper -->
<div>
  <label hlmLabel for="title">Title</label>
  <input hlmInput id="title" formControlName="title" />
</div>
```
Rule: if a component has been migrated to SpartAN, remove ALL `mat-form-field` wrappers around it. Keep `MatTooltipModule` for tooltips only.

### Category select / tags input migration
```html
<!-- category — use native select with hlmInput -->
<label hlmLabel for="categoryId">Category</label>
<select hlmInput id="categoryId" formControlName="categoryId">
  <option value="">Select category</option>
  <option *ngFor="let c of categories" [value]="c.id">{{ c.name }}</option>
</select>

<!-- tags — native input, Enter to add -->
<input hlmInput id="tagInput" (keydown.enter)="addTag($event)" />
```

## API Wiring

### Never leave mutations stubbed
Frontend `knowledgeService.createArticle()` was throwing `not implemented`. Backend `POST /api/articles` existed and worked. Always implement mutations before declaring a flow "done." The pattern:
```ts
createArticle(data: CreateArticleDto): Observable<Article> {
  return this.http.post<{data: Article}>(`${API_CONFIG.baseUrl}/articles`, data, this.authHeader())
    .pipe(map(res => res.data));
}
```

### Categories service — don't use mocks with fake IDs
`CategoryService.getActiveCategories()` was returning `cat1..cat5` (non-UUID) IDs. Backend `CreateArticleDto` validates `@IsUUID()` on `categoryId`. Form always posted fake IDs → HTTP 400 `categoryId must be a UUID`. Replace mocks with real API calls immediately. The ncdu scan found `cat1` IDs were the culprit in the 400 error.

## Headless Browser Verification

Always use Playwright for form + navigation verification:
```js
// Inject auth token directly (faster than UI login)
await p.evaluate((token) => {
  localStorage.setItem('access_token', token);
  localStorage.setItem('currentUser', JSON.stringify({ role: 'author' }));
}, TOKEN);

// Intercept requests to see body + status
await p.route('**/api/articles', async (route) => {
  const req = route.request();
  console.log('REQ_BODY:', req.postData());
  const resp = await route.fetch();
  console.log('RESP_STATUS:', resp.status());
  await route.fulfill({ response: resp });
});
```

## Disk Diagnosis (ncdu pattern)

Use `ncdu -o file` to scan without hanging on large filesystems:
```bash
ncdu -o /tmp/ncdu.txt -x /home/deeone
# then read /tmp/ncdu.txt with read_file
```
`du -sh /home/deeone` hangs on large filesystems. `ncdu` with `-o` export is the reliable alternative.