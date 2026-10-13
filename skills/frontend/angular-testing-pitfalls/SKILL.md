---
name: angular-testing-pitfalls
description: Pitfalls and run-gotchas for Angular component/spec testing with Jasmine+Karma or Vitest — computed() not tracking FormGroup, zoneless fakeAsync breakage, spying on signal-typed service fields, and Karma suite-compile failures from one corrupted spec. Use when a button stays disabled despite a valid form, a test throws "zone-testing.js is needed", or `ng test` fails to compile. Complements (does not replace) angular-testing.
---

# Angular Testing Pitfalls

Concrete failure modes encountered while testing Angular v20+ signal + zoneless + ReactiveForms
components with Jasmine/Karma (and applicable to Vitest). Each has a verified fix.

## 1. computed() does NOT track a plain ReactiveForms FormGroup
A submit button gated by `canSubmit = computed(() => this.form.get('x')?.valid && ...)` never
re-evaluates when the user types, because `computed` only reacts to **signals**, and a plain
`FormGroup` is not one. Symptom: button stays `disabled` forever even with a valid form.
**Fix:** make it a method — `canSubmit(): boolean { return ...; }` — and bind
`[disabled]="!canSubmit()"`. Template method calls re-run on every change detection.
(If you use `@angular/forms/signals` form-control signals, `computed` IS fine because those are
real signals. The trap is mixing `computed` with a `FormGroup`.)

## 2. Zoneless app: fakeAsync throws "zone-testing.js is needed"
With `provideZonelessChangeDetection()`, `fakeAsync`/`tick` fail unless `zone.js/testing` is
imported in test setup. **Fix for synchronous mocks** (`of(...)`): drop `fakeAsync`/`tick`,
call the action, then `fixture.detectChanges()`, then assert. Reserve `fakeAsync` for real
timers/debounce.

## 3. Spying on a signal-typed service property
`jasmine.createSpyObj('Svc', ['m'], { isLoading: <signal> })` enforces the declared
`WritableSignal` type and rejects a plain function; `Object.defineProperty` over it throws
`TypeError: Cannot redefine property: isLoading`. **Fix:** build the spy with only real methods,
then assign the field via a cast: `(authService as any).isLoading = () => false;` — the
component calls `this.isLoading()`, so a plain function returning the value works.

## 4. One corrupted spec breaks the WHOLE Karma compile
`ng test --include='**/x.spec.ts'` still type-checks **all** `*.spec.ts` in the project. A single
broken spec (commonly an auto-generated stub with the garbage line `import { *Component } from
'./x';`) fails the entire build. **Fix:** `grep -rln "import { \*Component }" src/`, then rewrite
each (correct `ComponentFixture, TestBed` import + real class) or quarantine them aside so your
target spec compiles.

## 5. CHROME_BIN must be a real launchable binary
Karma's `ChromeHeadless` launcher reads `process.env.CHROME_BIN`. If unset or pointing at a
missing wrapper, it errors `Cannot find the binary /usr/bin/google-chrome`. **Fix:** export it
inline in the same command (a prior `export` may not reach the karma child):
`CHROME_BIN=/usr/bin/google-chrome-stable npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox --include='**/x.spec.ts'`.
(On Arch, `/usr/bin/google-chrome-stable` and `/usr/bin/chromium` exist; the plain
`/usr/bin/google-chrome` symlink may not.)

## Worked example: register form spec (button-enable + submit)
```typescript
authService = jasmine.createSpyObj<AuthService>('AuthService', ['register', 'getDefaultRouteForRole']);
(authService as any).isLoading = () => false;
authService.getDefaultRouteForRole.and.returnValue('/knowledge');

it('enables submit only after valid form + accepted terms', () => {
  component.registerForm.setValue({ firstName:'Jane', lastName:'Doe', username:'jane',
    email:'j@e.com', password:'password123', confirmPassword:'password123', acceptTerms:false });
  expect(component.canSubmit()).toBeFalse();
  component.registerForm.patchValue({ acceptTerms: true });
  expect(component.canSubmit()).toBeTrue();
});

it('submit calls register and navigates', () => {
  authService.register.and.returnValue(of({ access_token:'t', refresh_token:'r',
    user:{ id:'1', firstName:'Jane', email:'j@e.com', role:'viewer' } } as any));
  component.onSubmit();
  fixture.detectChanges();
  expect(authService.register).toHaveBeenCalledTimes(1);
  expect(router.navigate).toHaveBeenCalledWith(['/knowledge']);
});
```

See [references/karma-jasmine-gotchas.md](references/karma-jasmine-gotchas.md) for the full
run-time error transcripts and quarantine recipe.
