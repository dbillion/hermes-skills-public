---
name: playwright-e2e-sandbox
description: Playwright E2E for web frontends in this sandbox.
---

# Playwright E2E in this sandbox

Playwright is the correct tool for **web** frontend E2E. Appium is mobile-only (not needed for web).
Mocha/Vitest are unit runners (Vitest is usually already present for component/unit). Pytest covers
the backend. Don't install Appium for a web app.

## Setup (sandbox-specific — read before running)
The global `rtk` binary at `~/.local/bin/rtk` wraps `npm`/`npx`/`playwright` and breaks them
(`"All parsing tiers failed"`, or `"two different versions of @playwright/test"`). **Never** call
`npx playwright` or bare `playwright`. Install self-contained in the project and invoke by path:

```bash
cd <frontend-dir>
npm install -D @playwright/test@1.58.2 playwright-core@1.58.2
node node_modules/.bin/playwright install chromium chromium-headless-shell
# run:
node node_modules/.bin/playwright test
```

If you still hit `"two different versions of @playwright/test"` / a stack mentioning
`playwright/lib/common/testType.js`, the global `/home/deeone/node_modules/playwright` is shadowing
the local copy. The local install above fixes it because `node_modules/.bin/playwright` resolves to
the project-local `@playwright/test`. Do NOT use `npx` (it re-resolves to the wrapped global).

## Spec + config
- `playwright.config.ts`: `testDir: './e2e'`, one chromium project, and `use: { baseURL: process.env.BASE_URL ?? 'http://localhost:3100' }`. Pass the URL via config/env — **not** the CLI `--base-url` flag (unsupported and errors).
- Selectors: prefer `getByRole` / `getByText`.
  - **Invalid:** `getByRole('button', { type: 'submit' })` (no `type` option) → use `locator('button[type="submit"]')`.
  - Avoid `getByText('X')` when X appears as both a heading and a button (strict-mode violation). Scope with `getByRole('heading', { name: 'X' })`.

## Auth / CORS pitfalls (the usual silent failures)
- The browser **origin** must be in the backend `CORS_ALLOWED_ORIGINS`. If login works via `curl`
  but fails in-browser with a misleading `"Invalid email or password"`, it is **CORS blocking the
  authenticated request** from a non-allowed origin — add the dev port to CORS (e.g. `localhost:3100`,
  `127.0.0.1:3100`).
- Test pollution: a test that logs in leaves a JWT in `localStorage`; a later auth-gate test then sees
  an authenticated user and the redirect never happens. Clear state at the start of the auth-gate test:
  ```ts
  await context.clearCookies();
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
  ```

## Verify
Run `node node_modules/.bin/playwright test --reporter=line`. Expect green. **Deliver screenshots of
key pages to the user as MEDIA: files** — rendering them internally is not enough; the user wants the
actual image files. (This is an explicit, repeated user requirement: "why are you not sending me
screenshots".)

## References
- `references/playwright-smoke-template.md` — copy-ready smoke spec (homepage, pricing/membership,
  login→dashboard, auth-gate redirect) plus a config snippet for a Next.js + DRF app.
