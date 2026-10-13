# Docker Compose + Rails 8 Debugging Cookbook

Session-derived patterns from deploying CRM Hub (2026-06-27). These are class-level patterns for Rails 8 + Docker Compose + Kamal projects.

## Architecture: Kamal vs Docker Compose

- **Kamal** (`config/deploy.yml`): deploys to remote servers only. Not for local dev.
- **Docker Compose** (`docker-compose.yml`): local runtime. Must add an `app` service manually.
- **Dockerfile**: shared by both. Production-optimized (multi-stage, asset precompile).

## The Boot Debugging Loop

When the app container starts but returns 500:

```
docker compose up -d app
sleep 8
curl -s -w "\n%{http_code}" http://localhost:3000  # → 500
docker compose logs app --no-log-prefix | grep -B 2 "Completed\|Error"
```

### Reading Stack Traces in Docker Logs

```bash
# Full error + backtrace
docker compose logs app --no-log-prefix 2>&1 | grep -A 30 "NameError\|RuntimeError\|ArgumentError"

# Just the error message
docker compose logs app --no-log-prefix 2>&1 | grep "Error\|Exception" | head -5
```

### One-Off Debugging Commands

```bash
# Test Rails boots without web server
docker compose exec app bundle exec rails runner 'puts "Boot OK"'

# Test specific constant loading
docker compose exec app bundle exec rails runner 'puts defined?(Ahoy::Store)'

# Check routes load
docker compose exec app bundle exec rails routes | head -20

# Interactive console
docker compose exec app bundle exec rails console
```

## Known Issues & Fixes

### 1. `uninitialized constant Ahoy::Store`

**Cause**: `ahoy_matey` 5.5.0 has a bug — `Ahoy::Tracker#initialize` calls `Ahoy::Store.new(...)` but only `Ahoy::DatabaseStore` is defined. No `Store = DatabaseStore` alias exists in the gem.

**Fix** — Create `config/initializers/ahoy.rb`:
```ruby
require "ahoy/database_store"
Ahoy::Store = Ahoy::DatabaseStore unless defined?(Ahoy::Store)
```

**Why `require` first**: `Ahoy::DatabaseStore` is autoloaded by Zeitwerk. The initializer runs before autoloading completes, so we must `require` it eagerly.

**Alternative fix** (if you don't need tracking): Set `Ahoy.api_only = true` in the initializer — this skips the `before_action :track_ahoy_visit` callback entirely.

### 2. Tailwind v4 Asset Path

**Cause**: `tailwindcss-rails` gem expects the Tailwind input CSS at `app/assets/tailwind/application.css`. Rails 8 apps sometimes place it at `app/assets/stylesheets/application.tailwind.css`.

**Fix**: Move the file:
```bash
mkdir -p app/assets/tailwind
mv app/assets/stylesheets/application.tailwind.css app/assets/tailwind/application.css
```

Also remove any old precompiled `application.css` in `app/assets/stylesheets/` that might conflict.

### 3. `database.yml` ERB + YAML Aliases

**Symptom**: `Psych::SyntaxError: scanning an alias` or `unknown keyword: :aliases`

**Root cause**: `ActiveSupport::ConfigurationFile.parse` processes ERB first, then YAML. The `<<: *default` YAML alias must survive ERB rendering. If env vars in `<%= %>` tags produce output identical to the raw content, the code path can skip ERB processing and try to parse `<%` as YAML.

**Fix**: Ensure all `<%= %>` lines in database.yml produce different output than the raw ERB tags. Quote them properly:
```yaml
password: <%= ENV.fetch("DB_PASSWORD", "password") %>
```

**Don't**: Replace `<%=` with `***` or other placeholders — this breaks ERB rendering.

### 4. Volume Mount Hot-Reload Limitations

**Symptom**: Code changes visible in container (`cat` shows new file) but behavior doesn't change.

**Cause**: Initializers run once at boot. New/changed initializers won't be picked up without restart. Zeitwerk reloads app code in development, but initializer changes need a full process restart.

**Fix**:
```bash
# Kill + recreate (not just restart)
docker kill <container_name>
docker compose up -d --force-recreate app
```

### 5. Host vs Container Gem Mismatch

**Symptom**: `Bundler::GemRequireError: cannot load such file -- debug/prelude` when running `bundle exec rails` on host.

**Cause**: Gems are installed inside the Docker image (`vendor/bundle`), not on the host. The host Ruby has a different gem set.

**Fix**: Never run Rails commands on the host. Always use:
```bash
docker compose exec app bundle exec rails <command>
# or for one-off:
docker compose run --rm app bundle exec rails <command>
```

## Debugging Workflow (Don't Loop!)

1. **Read the full error** — `docker compose logs app --no-log-prefix | grep -A 20 "Error"`
2. **Identify the class/module** — Is it a gem issue? A config issue? A missing file?
3. **Test in isolation** — `docker compose exec app bundle exec rails runner '...'`
4. **Fix the root cause** — Edit the source file (volume-mounted, so changes are instant)
5. **Restart properly** — `docker kill` + `docker compose up -d --force-recreate`
6. **Verify** — `curl -s -w "\n%{http_code}" http://localhost:3000`

**If the same error appears 3+ times**: Stop. You're looping. The error is telling you something specific — read it carefully. Common traps:
- Looking at the wrong file (host vs container)
- Editing a file that isn't volume-mounted
- Missing that the initializer load order matters
- Not realizing the web process caches state across restarts
