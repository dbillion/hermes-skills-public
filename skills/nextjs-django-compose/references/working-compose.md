# Known-good docker-compose stack (adapt paths/names)

## docker-compose.yml (repo root)
```yaml
services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: harvest
      POSTGRES_PASSWORD: harvestpass
      POSTGRES_DB: harvestconnect
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U harvest -d harvestconnect"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

  backend:
    build: { context: ./backend }
    restart: unless-stopped
    command: ["sh", "startup.sh"]
    environment:
      DJANGO_SETTINGS_MODULE: harvestconnect.settings
      DJANGO_SECRET_KEY: dev-secret-key-change-me
      DEBUG: "True"
      ALLOWED_HOSTS: "localhost,127.0.0.1,0.0.0.0,backend"
      # ?sslmode=disable REQUIRED for local postgres (dj_database_url ssl_require=True)
      DATABASE_URL: "postgres://harvest:harvestpass@postgres:5432/harvestconnect?sslmode=disable"
      REDIS_URL: "redis://redis:6379"
      PORT: "8000"
      CORS_ALLOWED_ORIGINS: "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3100,http://127.0.0.1:3100"
    ports:
      - "8000:8000"
    depends_on:
      postgres: { condition: service_healthy }
      redis:    { condition: service_healthy }

  frontend:
    build:
      context: ./harvestconnect
      args:
        # browser-facing URL is HOST-mapped, not the service name
        NEXT_PUBLIC_API_URL: "http://localhost:8000/api"
        NEXT_PUBLIC_API_TIMEOUT: "30000"
    restart: unless-stopped
    # host 3000 may be occupied by an unrelated process -> use 3001
    ports:
      - "3001:3000"
    depends_on:
      backend: { condition: service_healthy }

volumes:
  pgdata:
```

## startup.sh patch (add near "Database is ready!")
```sh
# Ensure upload temp dir exists (settings.FILE_UPLOAD_TEMP_DIR)
mkdir -p media/temp
```
Insert right after the `echo "Database is ready!"` line, before `python manage.py migrate`.

## requirements.txt additions (if CACHES/CHANNEL_LAYERS use redis)
```
django-redis>=5.4.0
channels-redis>=4.2.0
redis>=5.0.0
```

## Launch + verify
```bash
docker compose up -d --build > /tmp/compose.log 2>&1   # never pipe to tail (hangs)
docker compose ps                                      # backend/frontend healthy
docker compose exec backend python manage.py seed_data
curl -s -o /dev/null -w "api=%{http_code}\n" http://localhost:8000/api/   # expect 200
docker compose exec backend python -m pytest tests/ -v
node node_modules/.bin/playwright test --reporter=line   # from host, vs localhost:3001
```
