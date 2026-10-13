# Role / ownership verification recipe (ks-knowledge-sharing)

Verified live-curl sequence to prove the social-media role model end-to-end.
Run against the booted API (`npx nest start`, port 3000). Requires `DATABASE_URL`
in env (the API loads `.env` via `ConfigModule`; the seed script does NOT — export
`DATABASE_URL` from `.env` before `node scripts/seed.mjs`).

## Seed an admin
```
export DATABASE_URL="$(grep '^DATABASE_URL=' .env | head -1 | cut -d= -f2-)"
node scripts/seed.mjs
# -> Users: 3 (1 admin + 2 authors)
```

## Live proof checklist (curl)
```
B=http://localhost:3000/api
# 1. Register -> expect role=author (NOT viewer)
curl -s -X POST $B/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"u@test.dev","username":"u","password":"password123","firstName":"U","lastName":"Ser"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['user']['role'])"

# 2. Login -> token + role
TOK=$(curl -s -X POST $B/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"ada@ks.dev","password":"password123"}' \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['access_token'])")

# 3. Create with a REAL category UUID (GET /api/categories returns them)
CAT=$(curl -s $B/categories | python3 -c "import sys,json;print(json.load(sys.stdin)['data'][0]['id'])")
AID=$(curl -s -X POST $B/articles -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' \
  -d "{\"title\":\"T\",\"content\":\"C\",\"categoryId\":\"$CAT\",\"isPublished\":true}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['id'])")

# 4. Different author edits -> 403 ; owner edits -> 200 ; admin edits -> 200
#    (login as alan, try PATCH $B/articles/$AID -> expect 403)
#    (PATCH with owner TOK -> 200 ; with admin TOK -> 200)
```

## Ownership enforcement pattern (service layer)
```ts
async update(id: string, user: { id: string; role: string }, dto: UpdateArticleDto) {
  const article = await this.findOne(id);
  if (user.role !== 'admin' && article.authorId !== user.id)
    throw new ForbiddenException('You can only modify your own articles');
  return this.articleRepo.save({ ...article, ...dto });
}
```
Guard the route with `@UseGuards(JwtAuthGuard)` and read `req.user`
(populated by the JWT strategy) — NOT a custom `@User()` decorator.

## Create endpoint must set authorId + map categoryId
```ts
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
async create(@Req() req: Request, @Body() dto: CreateArticleDto) {
  const user = req.user as { id: string; role: string };
  const article = await this.articlesService.create({
    ...dto,
    category: dto.categoryId,   // entity stores it in `category`
    authorId: user.id,          // never trust client-supplied author
  });
  return { message: 'Article created successfully', data: article };
}
```

## Verified results (this session, 2026-07-19)
register->author | ada create 201 | alan edit/delete others 403 | ada edit own 200 |
admin override 200 | admin seeded (role=admin). nest build + ng build clean.
