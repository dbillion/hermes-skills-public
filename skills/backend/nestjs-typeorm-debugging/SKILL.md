---
name: nestjs-typeorm-debugging
description: >-
  Debugging NestJS + TypeORM + Postgres auth/entity failures: the "register returns 500 /
  EntityMetadataNotFoundError: No metadata for X" / null value in column Y violates not-null
  class of bugs. Covers entity-vs-DB schema mismatch, snake_case naming strategy, legacy vs
  active entity collision, and response-shape mismatch with the frontend. Use when a NestJS
  endpoint 500s on DB write, login/register silently fails, or the frontend auth call returns
  an error with no obvious cause.
user-invocable: false
---

# NestJS + TypeORM + Postgres debugging

A 500 on a DB-backed endpoint is almost never "the database is down". It is a schema/entity
mismatch. This skill records the root-cause chain seen repeatedly in Angular+NestJS+Neon apps.

## Symptom → root cause map

| Symptom (API log or curl) | Root cause | Fix |
| --- | --- | --- |
| `500 Internal Server Error` on POST /auth/register, no clear message | Entity column names don't match the provisioned DB table (camelCase entity vs snake_case DB, or entity has columns the table lacks) | Align entity to DB: add `@Column({ name: 'password_hash' })` etc., or drop extra fields; ensure `SnakeNamingStrategy` maps the rest |
| `EntityMetadataNotFoundError: No metadata for "User" was found` | The entity used by a module is NOT in the TypeORM `entities` glob, OR it imports a legacy skeleton entity not loaded | Point the module at the entity actually wired into `entities: [...]`; don't load two entities with the same `@Entity('users')` table name |
| `error: 23502 null value in column "password_hash" violates not-null constraint` | Service sets `password: hashed` but the entity property is `passwordHash` (so the hash lands in a non-existent `password` col and `password_hash` stays null) | Set the correct property: `passwordHash: hashedPassword`; also `bcrypt.compare(pw, user.passwordHash)` |
| Frontend: "Registration failed" but API 500s | Same as above — frontend shows generic error; the real cause is server-side | Read the API process stderr, not just the HTTP status |
| `duplicate entity` / "Entity with name X already exists" | Two entity files (e.g. `modules/users/user.entity.ts` AND `database/entities/user.entity.ts`) both declare `@Entity('users')` and both are in the `entities` glob | Load ONLY the active one; exclude legacy skeletons from the glob |
| `EntityMetadataNotFoundError: No metadata for "User"` even after adding the entity to the glob | You broadened `entities` to `database/entities/*.entity.ts` to fix the metadata error, but that dir ALSO holds legacy skeletons (`article.entity`, `category.entity`) that collide (same `@Entity('articles')`/`@Entity('categories')`) with the `modules/**` ones → duplicate-entity failure | Do NOT broaden the glob. Instead point the importing module at the entity already in the glob (e.g. change the import in `auth.module.ts` from `../../database/entities/user.entity` to `../users/user.entity`). Keep `entities: [__dirname + '/../modules/**/*.entity{.ts,.js}']` |
| Frontend: login works but register navigates to a blank/`/dashboard` that 404s | `register` returned `{message, user}` but frontend `AuthResponse` expects `{access_token, refresh_token, user}`; OR success route doesn't exist | Make `register` return the same JWT shape as `login`; navigate to a real route (e.g. role-based default) |

## The "register not working / is the frontend connected?" diagnostic

1. Confirm the frontend calls the real backend. Check `api.config.ts` `baseUrl` — if it is an
   ABSOLUTE url (`http://localhost:3000/api`), the browser hits the API directly (CORS must allow
   the origin). If it is a RELATIVE `/api`, the Angular dev server must have a `proxy.conf` for
   `/api` → `http://localhost:3000`, otherwise the call 404s against :4200.
2. Reproduce the call with curl against the API directly to isolate backend vs frontend:
   `curl -s -X POST http://localhost:3000/api/auth/register -H 'Content-Type: application/json' -d '{"email":...,"username":...,"password":...}'`
   - 500 → backend entity/schema bug (see table). Read `node dist/main.js` stderr for the PG error.
   - 200 with tokens → backend fine; the problem is frontend (route, response shape, or the dev
     server proxy).
3. Check the actual DB columns vs the entity:
   `psql "$DATABASE_URL" -c "\d users"` and compare to the entity's `@Column` names. The
   `SnakeNamingStrategy.columnName()` maps camelCase→snake_case, but ONLY for properties WITHOUT an
   explicit `name:`; if the DB column is `password_hash` the entity must say
   `@Column({ name: 'password_hash' }) passwordHash`.
4. Check WHICH entity the module loads. `TypeOrmModule.forFeature([User])` must reference the same
   `User` class that is in the global `entities` array. A mismatch (module imports
   `database/entities/user.entity` while the glob loads `modules/users/user.entity`) produces
   "No metadata for User" at runtime even though it compiles.

## Minimal fix checklist for a broken auth module

- Module + service + clerk.service all import the SAME `User` entity (the one in `entities` glob).
- Entity columns match the DB exactly (use `name:` for snake_case cols like `password_hash`).
- `register` returns `{ access_token, refresh_token, user }` (mirror `login`).
- `register` sets `passwordHash: await bcrypt.hash(...)`; `login` compares against `user.passwordHash`.
- Remove/destructure `passwordHash` (never `password`) when stripping the hash from responses.
- Success navigation target is a real route.

## Verify

After fixes: `npx nest build` clean; restart `node dist/main.js`; then:
- `curl` login → `access_token` present.
- `curl` register (new user) → `access_token` present.
- `curl` register (same user) → `409`.
If all three pass, the frontend "Create account" will work (it already called the right URL).
