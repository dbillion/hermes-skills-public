# Production Checklist

Run this checklist before declaring a Kamal-deployed Rails app "done."

## Pre-Deploy

- [ ] `config/deploy.yml` has correct server IP, image name, registry credentials
- [ ] `.kamal/secrets` exists and contains `RAILS_MASTER_KEY`, `POSTGRES_PASSWORD`, `KAMAL_REGISTRY_PASSWORD`
- [ ] `.kamal/secrets` is in `.gitignore`
- [ ] `config/database.yml` production section uses `DB_HOST` env var (not hardcoded)
- [ ] `config/environments/production.rb` has `config.assume_ssl = true` if using proxy SSL
- [ ] `config/environments/production.rb` has `config.force_ssl = true`
- [ ] Dockerfile builds successfully: `docker build -t myapp .`
- [ ] `RAILS_MASTER_KEY` is set (or `config/master.key` exists for production)

## Database

- [ ] All migrations run: `kamal app exec "bin/rails db:migrate"`
- [ ] Schema is up to date: check `db/schema.rb` is committed
- [ ] Solid Cache/Queue/Cable tables exist (if using trilogy)
- [ ] Database indexes exist for all foreign keys
- [ ] Database indexes exist for all search/filter columns (Ransack, etc.)

## Assets & Frontend

- [ ] Assets precompile without error: `SECRET_KEY_BASE_DUMMY=*** ./bin/rails assets:precompile`
- [ ] Tailwind CSS compiles (if using tailwindcss-rails)
- [ ] No div-based fake screenshots (taste-skill compliance)
- [ ] All CTAs have readable text (WCAG AA contrast)
- [ ] Dark mode works (if applicable)

## Security

- [ ] `config.filter_parameter_logging += [:password, :token, :secret]`
- [ ] Rate limiting configured (Rack::Attack or similar)
- [ ] Content Security Policy set
- [ ] No secrets in code (all via env)
- [ ] Brakeman scan passes: `bundle exec brakeman -q`

## Performance

- [ ] Database connection pooling configured (`max_connections` in database.yml)
- [ ] Solid Cache configured for fragment caching
- [ ] N+1 queries eliminated (Bullet gem in dev)
- [ ] Large queries use `find_each` not `all`
- [ ] Background jobs (Sidekiq/Solid Queue) for email/SMS sending

## Monitoring

- [ ] Health check endpoint exists (`/up` or `/health`)
- [ ] Logging configured (JSON format for production)
- [ ] Error tracking configured (Sentry/Bugsnag optional)
- [ ] Ahoy or similar for visit tracking (if CRM/marketing)

## Post-Deploy Verification

- [ ] `kamal logs -f` shows no errors
- [ ] `kamal containers` shows all containers healthy
- [ ] App responds on port 80/443
- [ ] Database accessible: `kamal dbc` connects
- [ ] Redis accessible: `kamal accessory boot redis` works
- [ ] SSL certificate active (if configured)
- [ ] Backups configured (PostgreSQL dumps or WAL)

## Rollback Plan

```bash
# If deploy fails:
kamal rollback

# If DB migration breaks:
kamal app exec "bin/rails db:rollback STEP=1"
kamal deploy
```
