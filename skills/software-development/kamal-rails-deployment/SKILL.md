---
name: kamal-rails-deployment
description: "Deploy Rails apps to production with Kamal. Covers accessory-based architecture (DB + Redis), design-first workflow with C4/ER/BPMN diagrams, production Dockerfile configuration, and the strict sequence: design → scaffold → deploy."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [rails, kamal, deployment, docker, production, devops]
    related_skills: [writing-plans, subagent-driven-development, systematic-debugging]
---

# Kamal Rails Deployment

## Overview

Deploy Ruby on Rails applications to production using Kamal's accessory-based architecture. This skill enforces a strict design-first workflow: C4 diagrams → ER diagrams → BPMN flows → code → deploy.

**Core principle:** Kamal manages runtime infrastructure (PostgreSQL, Redis, SSL, storage) as accessories — not docker-compose. Docker is only for local dev and the production Dockerfile.

## When to Use

- Setting up a new Rails app for production deployment
- Migrating a Rails app from docker-compose/Heroku to Kamal
- Configuring PostgreSQL + Redis accessories for Rails
- Writing production Dockerfiles for Rails 8+ (Solid Cache/Queue/Cable)
- Debugging Kamal deploy failures

**NOT for:** Non-Rails apps, non-Kamal deployments, local-only development without production target.

## The Workflow (Strict Sequence)

### Phase 0: Design (MANDATORY — No code before this)

Generate ALL three diagram types before touching any code:

1. **C4 Architecture** — System Context (who connects to the system) + Container Level (how it's deployed)
2. **Database ER Diagram** — Every table, every relationship, every foreign key
3. **BPMN Flows** — Business processes the system handles (booking, onboarding, payment, etc.)

**Output format:** Mermaid code blocks in `docs/DESIGN.md`, rendered to PNG via `mmdc`.

```bash
# Render all mermaid diagrams to PNG
mkdir -p docs/diagrams
# Extract each ```mermaid block from DESIGN.md
mmdc -i input.mmd -o output.png -b white -w 1600 -s 2
```

### Phase 1: Scaffold

```bash
# Generate Rails app (use Docker if host lacks build tools)
docker run --rm -v "$(pwd)":/rails -w /rails ruby:3.4 bash -c \
  "gem install rails && rails new myapp --database=postgresql --javascript=importmap --css=tailwind"
```

**Key scaffolding decisions:**
- `--database=postgresql` — matches Kamal accessory
- `--javascript=importmap` — no Node/Webpack needed (ponytail: simplest option)
- `--css=tailwind` — works with taste-skill for frontend quality
- Skip solid-* flags if using external Redis (Kamal accessory)

### Phase 2: Kamal Configuration

**`config/deploy.yml`** structure:

```yaml
service: myapp
image: your-registry/myapp

servers:
  web:
    - YOUR_SERVER_IP

proxy:
  ssl: true
  host: yourdomain.com

registry:
  server: ghcr.io
  username: your-user
  password:
    - KAMAL_REGISTRY_PASSWORD

env:
  secret:
    - RAILS_MASTER_KEY
  clear:
    SOLID_QUEUE_IN_PUMA: true
    DB_HOST: myapp-db  # matches accessory name

accessories:
  db:
    image: postgres:17
    host: YOUR_SERVER_IP
    port: "127.0.0.1:5432:5432"
    env:
      clear:
        POSTGRES_USER: myapp
        POSTGRES_DB: myapp_production
      secret:
        - POSTGRES_PASSWORD
    directories:
      - data:/var/lib/postgresql/data

  redis:
    image: valkey/valkey:8
    host: YOUR_SERVER_IP
    port: "127.0.0.1:6379:6379"
    directories:
      - data:/data

volumes:
  - "myapp_storage:/rails/storage"

builder:
  arch: amd64
```

**`config/database.yml`** for production:

```yaml
production:
  primary: &primary_production
    adapter: postgresql
    encoding: unicode
    database: myapp_production
    username: myapp
    password: <%= ENV["MYAPP_DATABASE_PASSWORD"] %>
    host: <%= ENV.fetch("DB_HOST", "myapp-db") %>
  cache:
    <<: *primary_production
    database: myapp_production_cache
    migrations_paths: db/cache_migrate
  queue:
    <<: *primary_production
    database: myapp_production_queue
    migrations_paths: db/queue_migrate
  cable:
    <<: *primary_production
    database: myapp_production_cable
    migrations_paths: db/cable_migrate
```

### Phase 3: Production Dockerfile

```dockerfile
ARG RUBY_VERSION=3.4
FROM docker.io/library/ruby:$RUBY_VERSION-slim AS base

WORKDIR /rails
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y curl libjemalloc2 libvips postgresql-client && \
    rm -rf /var/lib/apt/lists /var/cache/apt/archives

ENV RAILS_ENV="production" \
    BUNDLE_DEPLOYMENT="1" \
    BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_WITHOUT="development"

FROM base AS build
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential git libpq-dev libyaml-dev pkg-config && \
    rm -rf /var/lib/apt/lists /var/cache/apt/archives

COPY Gemfile Gemfile.lock ./
RUN bundle install && \
    rm -rf ~/.bundle/ "${BUNDLE_PATH}"/ruby/*/cache "${BUNDLE_PATH}"/ruby/*/bundler/gems/*/.git && \
    bundle exec bootsnap precompile --gemfile

COPY . .
RUN bundle exec bootsnap precompile app/ lib/
RUN SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

FROM base
RUN groupadd --system --gid 1000 rails && \
    useradd rails --uid 1000 --gid 1000 --create-home --shell /bin/bash
USER 1000:1000

COPY --chown=rails:rails --from=build "${BUNDLE_PATH}" "${BUNDLE_PATH}"
COPY --chown=rails:rails --from=build /rails /rails

ENTRYPOINT ["/rails/bin/docker-entrypoint"]
EXPOSE 80
CMD ["./bin/thrust", "./bin/rails", "server"]
```

### Phase 4: Local Development

Use docker-compose ONLY for local dev (not production):

```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"  # Use non-default port if conflicts
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: valkey/valkey:8
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  pg_data:
  redis_data:
```

**Bundle install via Docker** (avoids native extension issues on host):

```bash
# Create DB (connect via Docker network)
docker run --rm --network myapp_default -v "$(pwd)":/rails -w /rails \
  -e DB_HOST=postgres ruby:3.4 bash -c "bundle install && bundle exec rake db:create db:migrate"
```

### Phase 5: Deploy

```bash
# Initial setup
kamal setup

# Deploy
kamal deploy

# Common commands
kamal logs -f
kamal console
kamal shell
```

## Pitfalls

### Port Conflicts
Kamal accessories bind to `127.0.0.1:5432` and `127.0.0.1:6379` on the server. If you run local dev on the same machine, use different ports (5433, 6380) in docker-compose. Check existing ports with `ss -tlnp` before assigning.

### Bundle Install Fails on Host
Native gems (pg, nokogiri, etc.) often fail to compile on host due to missing system libs. **Fix:** Run `bundle install` inside the Docker container — it has all build tools pre-installed.

### Database Connection in Production
`DB_HOST` must match the accessory name (e.g., `myapp-db`), NOT `localhost`. Kamal creates a Docker network where the DB is accessible by its accessory name.

### Docker-Created Files Owned by Root
When running `rails new` or `rails generate` inside Docker, created files are owned by root. Fix with:
```bash
docker run --rm -v /project/path:/p alpine sh -c "chown -R 1000:1000 /p"
```

### Solid Trilogy (Cache/Queue/Cable)
Rails 8 uses Solid adapters backed by PostgreSQL. The `database.yml` config above includes separate databases for cache, queue, and cable — they all point to the same PostgreSQL accessory but use different schema files.

### Docker Build Context
The Dockerfile expects `Gemfile.lock` to exist. Generate it with `bundle install` before building. The `COPY vendor/* ./vendor/` line requires `vendor/` directory to exist (can be empty).

### `.kamal/secrets`
Never commit this file. It holds `RAILS_MASTER_KEY`, `POSTGRES_PASSWORD`, `KAMAL_REGISTRY_PASSWORD`. Add to `.gitignore`.

## Integration with Other Skills

- **writing-plans** — Generate implementation plan from design docs
- **subagent-driven-development** — Execute plan via fresh subagents per task
- **systematic-debugging** — Debug deploy failures (check `kamal logs`, verify env vars, test DB connectivity)
- **ponytail** — Apply "laziest solution that works" to all backend logic
- **taste-skill** — Apply anti-slop frontend quality to all views

## Design-First Discipline

**NEVER skip diagrams.** Before writing any migration or controller:
1. C4 shows the system boundaries and deploy target
2. ER shows every table and relationship — this IS your migration list
3. BPMN shows every business process — this IS your controller/workflow list

If a feature request doesn't have diagrams, generate them FIRST. The diagrams are the contract between design and implementation.

## References

- `references/kamal-cli-cheatsheet.md` — All essential Kamal commands with common flags
- `references/production-checklist.md` — Pre-deploy verification checklist
