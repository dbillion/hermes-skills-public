# Karma / Jasmine Run Gotchas — error transcripts & recipes

## Corrupted spec symptom (blocks whole suite)
```
✘ [ERROR] TS1434: Unexpected keyword or identifier.
    src/app/features/search/search-interface/search-interface.spec.ts:3:22:
      3 │ import { *Component } from './search-interface';
✘ [ERROR] TS2304: Cannot find name 'from'.
```
`import { *Component }` is garbage (the `*` should not be there). It spreads across several
auto-generated stubs at once.
```bash
grep -rln "import { \*Component }" src/
# rewrite each: replace first two lines with
#   import { ComponentFixture, TestBed } from '@angular/core/testing';
#   import { XxxComponent } from './xxx';
# OR quarantine: mkdir -p /tmp/broken-specs && mv <file> /tmp/broken-specs/
```

## CHROME_BIN missing binary
```
ERROR [launcher]: Cannot start ChromeHeadless
	Can not find the binary /usr/bin/google-chrome
```
```bash
# verify a working binary
/usr/bin/google-chrome-stable --version   # works on Arch
/usr/bin/chromium --version               # also works
# run with it inline (env must be in same command as npx)
CHROME_BIN=/usr/bin/google-chrome-stable npx ng test --watch=false \
  --browsers=ChromeHeadlessNoSandbox --include='**/register.spec.ts'
```

## Zoneless + fakeAsync
```
Error: zone-testing.js is needed for the fakeAsync() test helper but could not be found.
```
Fix: remove `fakeAsync`/`tick`; use synchronous `of()` + `fixture.detectChanges()`.

## Spy on signal-typed field
```
TypeError: Cannot redefine property: isLoading
    at Object.defineProperty (...)
    at src/.../xxx.spec.ts:49:12
```
Fix:
```typescript
authService = jasmine.createSpyObj<AuthService>('AuthService', ['register']);
(authService as any).isLoading = () => false;
```

## computed() not tracking FormGroup (the disabled-button trap)
Symptom in browser/Playwright: even a fully valid form leaves the submit button `disabled`.
Root cause: `canSubmit = computed(() => this.form.get('x')?.valid && ...)` only re-runs on
signal changes; `FormGroup` is not a signal. Fix: convert to a method `canSubmit(): boolean`.
Verify in browser with Playwright:
```js
const disabled = await page.locator('button[type=submit]').isDisabled();
// after fill + check terms -> expect false
```
