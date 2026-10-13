# Ownership / Role Curl Suite (Pattern 2)

Run against the LIVE API. Assumes it's started (`npx nest start`) and `DATABASE_URL`
is reachable. Paste a real category UUID from `GET /categories` into CAT.

```bash
B=http://localhost:3000/api
CAT=$(curl -s "$B/categories" | python3 -c "import sys,json;print(json.load(sys.stdin)['data'][0]['id'])")
echo "category=$CAT"

# 1. Self-register -> should default to author (not viewer)
curl -s -X POST $B/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"new@t.dev","username":"new","password":"password123","firstName":"N","lastName":"U"}' \
  | python3 -c "import sys,json;u=json.load(sys.stdin)['user'];print('registered role =',u['role'])"

# 2. Author A logs in, creates an article
TA=$(curl -s -X POST $B/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"ada@ks.dev","password":"password123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
ART=$(curl -s -X POST $B/articles -H "Authorization: Bearer $TA" -H 'Content-Type: application/json' \
  -d "{\"title\":\"Ada article\",\"content\":\"ownership test\",\"categoryId\":\"$CAT\",\"isPublished\":true}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['id'])")
echo "article=$ART"

# 3. Author B (different) tries edit/delete -> expect 403
TB=$(curl -s -X POST $B/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"alan@ks.dev","password":"password123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -o /dev/null -w "B edit A's article:   HTTP %{http_code}\n" -X PATCH $B/articles/$ART -H "Authorization: Bearer $TB" -H 'Content-Type: application/json' -d '{"title":"x"}'
curl -s -o /dev/null -w "B delete A's article: HTTP %{http_code}\n" -X DELETE $B/articles/$ART -H "Authorization: Bearer $TB"

# 4. Owner A edits own -> expect 200
curl -s -o /dev/null -w "A edit own article:   HTTP %{http_code}\n" -X PATCH $B/articles/$ART -H "Authorization: Bearer $TA" -H 'Content-Type: application/json' -d '{"title":"fixed"}'

# 5. Admin overrides -> expect 200
TADM=$(curl -s -X POST $B/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"admin@ks.dev","password":"password123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -o /dev/null -w "admin edit any:        HTTP %{http_code}\n" -X PATCH $B/articles/$ART -H "Authorization: Bearer $TADM" -H 'Content-Type: application/json' -d '{"title":"admin"}'

# cleanup
curl -s -X DELETE $B/articles/$ART -H "Authorization: Bearer $TADM" -o /dev/null -w "cleanup delete:      HTTP %{http_code}\n"
```

## Expected (social-media model)
- registered role = `author`
- B edit/delete A's = **403**
- A edit own = **200**
- admin edit any = **200**

## Enforcement location
Put ownership logic in the **service** (`articles.service.ts`), not just the controller:
```ts
if (user.id !== article.authorId && user.role !== 'admin') {
  throw new ForbiddenException('You can only modify your own articles');
}
```
Controller methods that mutate must take `@Req() req: Request` and read
`req.user` (populated by `JwtAuthGuard` + JWT strategy returning the full user).
Create endpoint must set `authorId: user.id` from the token and map the frontend's
`categoryId` field onto the entity's `category` column.
