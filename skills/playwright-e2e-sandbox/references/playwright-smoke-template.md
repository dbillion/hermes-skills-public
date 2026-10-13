# Playwright smoke spec — Next.js + Django REST (copy & adapt)

## playwright.config.ts
```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3100',
    headless: true,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
```

## e2e/smoke.spec.ts
```ts
import { test, expect } from '@playwright/test';

const FARMER = { email: 'farmer@harvestconnect.local', password: 'PracticePassword123' };

test.describe('frontend smoke', () => {
  test('homepage renders hero + CTA + featured products', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: /Connecting Faith/i })).toBeVisible();
    await expect(page.getByText(/Featured Products/i)).toBeVisible();
  });

  test('membership page renders all pricing tiers', async ({ page }) => {
    await page.goto('/membership');
    // scope by heading to avoid strict-mode clash with the CTA button of same text
    await expect(page.getByRole('heading', { name: 'Free Account' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Community Member' })).toBeVisible();
  });

  test('login with seeded account reaches dashboard', async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[type="email"]', FARMER.email);
    await page.fill('input[type="password"]', FARMER.password);
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/dashboard**', { timeout: 20000 });
    await expect(page).toHaveURL(/dashboard/);
  });

  test('auth gate: /products/new redirects anon to login', async ({ page, context }) => {
    await context.clearCookies();           // avoid JWT pollution from the login test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.goto('/products/new');
    await page.waitForURL('**/auth/login**', { timeout: 20000 });
    await expect(page).toHaveURL(/auth\/login/);
  });
});
```

## Notes
- Run with `node node_modules/.bin/playwright test --reporter=line` (never `npx playwright` — see
  the `rtk` wrapper caveat in the SKILL.md).
- If login passes via curl but fails here with "Invalid email or password", the frontend origin is
  NOT in the backend `CORS_ALLOWED_ORIGINS`. Add it (e.g. `localhost:3100`).
- Deliver screenshots to the user as `MEDIA:` files — they asked for them explicitly.
