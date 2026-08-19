# Route-Mismatch Checklist (Pattern 1)

When a clickable element "does nothing" or bounces to home, run this in order.

## 1. Find the real route
Read `app.routes.ts`. Record the actual path for the target component, e.g.:
- article detail → `knowledge/:id`
- article edit   → `knowledge/edit/:id`
- list           → `knowledge`

Note whether the route is lazy (`loadComponent`) and whether it has `canActivate`
guards (authGuard / roleGuard) — if guarded, an unauthenticated click redirects to
login, which can look like "nothing happened."

## 2. Grep for stale literals (template + TS + string-built URLs)
```
cd <frontend-root>/src
# template routerLink
grep -rn "routerLink.*'/articles" .
# TS navigate / createUrlTree
grep -rn "navigate(\['/articles" .
grep -rn "createUrlTree(\['/articles" .
# string-built share/clipboard URLs
grep -rn "'/articles/\${" .
grep -rn '`/articles/' .
```
Replace every match with the real route from step 1.

## 3. Verify in the BUILT bundle (decisive)
```
npx ng build --configuration development
grep -rn "/articles'" dist/**/*.js      # should return NOTHING (router paths)
grep -rn "/api/articles" dist/**/*.js    # OK — these are backend API URLs
```
If the stale literal is gone from the bundle and only `/api/articles` (API calls)
remain, the fix is complete.

## 4. Don't forget the siblings
The same rename bug usually lives in several files at once:
- search result cards + "Read More" button
- article-edit post-save redirect, preview, cancel, delete
- footer / header nav links
- share / clipboard URL builders
Fix all in one pass.
