---
name: nextjs-django-compose
description: Docker compose for Next.js + Django full-stack apps.
---

# Next.js + Django full-stack docker compose

## Compose topology
- `postgres` (postgres:16-alpine; healthcheck `pg_isready -U <user> -d <db>`).
- `redis` (redis:7-alpine; healthcheck `redis-cli ping`).
- `backend` (build ./backend; `command: ["sh","startup.sh"]`). Do NOT rely on the Dockerfile's bare
  `gunicorn` CMD — `startup.sh` waits for redis/db, runs `migrate`, `collectstatic`, creates a
  superuser. Reuse the project's existing `startup.sh`; just add `mkdir -p media/temp` if
  `settings.FILE_UPLOAD_TEMP_DIR` points at `media/temp`.
- `frontend` (build ./harvestconnect; multi-stage `output: 'standalone'`).

## Critical pitfalls (this is where stacks silently fail)
1. **Never pipe `docker compose up --build` to `tail`/`head`.** Docker's progress output buffers
   through the pipe and the command appears to hang — zero output, no containers, process "running"
   forever. **Redirect to a log file and poll it:**
   `docker compose up -d --build > /tmp/compose.log 2>&1` then `tail -f /tmp/compose.log`.
2. **Postgres + dj_database_url:** settings often do
   `dj_database_url.config(default=DATABASE_URL, ssl_require=True)`. For local postgres append
   `?sslmode=disable` to `DATABASE_URL` (`postgres://user:pass@postgres:5432/db?sslmode=disable`) or
   the connection forces SSL and fails.
3. **NEXT_PUBLIC_API_URL must be host-mapped, NOT the service name.** The browser runs on the host,
   so set it to `http://localhost:8000/api` (Docker maps backend `8000:8000`). `http://backend:8000`
   is unreachable from the browser. Pass it as a build ARG on the frontend service.
4. **Redis deps are often missing from requirements.txt.** If `settings.py` imports `django_redis`
   (CACHES) and `channels_redis` (CHANNEL_LAYERS), requirements MUST list `django-redis`,
   `channels-redis`, `redis` — else the container crashes at settings import. Add them.
5. **CORS dev ports:** the browser origin you serve the frontend on (e.g. `http://localhost:3000`)
   must be in `CORS_ALLOWED_ORIGINS`. Add every port you actually use.
6. **Port conflicts:** a host port may be held by an unrelated process (e.g. `linkedin-scrape` on
   3000). Do NOT kill unrelated processes — map to a free host port (`3001:3000`) and keep it in the
   CORS list.

## Launch sequence
```bash
# 1. Kill the running host backend/frontend (your tracked procs) — not unrelated services.
# 2. Build + start (log, not pipe):
docker compose up -d --build > /tmp/compose.log 2>&1
# 3. Wait for healthy:
docker compose ps            # backend/frontend "healthy"/"running"
# 4. Seed (after up):
docker compose exec backend python manage.py seed_data
# 5. Tests:
docker compose exec backend python -m pytest tests/ -v     # backend (pytest-django)
node node_modules/.bin/playwright test --reporter=line     # frontend E2E (from host, vs localhost:<port>)
```

## Pre-launch review (user-required)
Before containerizing, verify: (a) every nav `href`/`router.push` maps to a real `page.tsx`
(no dead links — e.g. a "Forgot Password" link with no route); (b) pages over ~200 lines are
refactored into single-responsibility components (modularity / SOLID — the user explicitly requires
this and pushes back on 100+ line monoliths).

## Verify
- `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/` → 200.
- Frontend reachable on its mapped port; login with a seeded account works (no CORS error).
- Both test suites green.

## References
- `references/working-compose.md` — a known-good `docker-compose.yml`, the `startup.sh` `mkdir` patch,
  and the `requirements.txt` additions for this stack (copy and adapt).
