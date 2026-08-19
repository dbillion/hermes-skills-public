# Rails 8 Boot Failure Debugging

## The Golden Rule
**After 2 identical failures, STOP. Read the log. Diagnose. Fix root cause. Retry.**

Rails logs to `log/development.log` (NOT stdout). When running `rails server` in background, errors don't appear in terminal output.

## Debugging Flow

```bash
# 1. Get the actual exception
tail -40 log/development.log

# 2. Identify root cause from error message

# 3. Fix in source (edit the file)

# 4. Kill + restart server
lsof -ti:3000 | xargs kill -9 2>/dev/null
rails server -b 0.0.0.0 -p 3000

# 5. Verify
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

## Common 500 Root Causes (Rails 8 + SQLite)

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `NameError: uninitialized constant Ahoy::Store` | `ahoy_matey` 5.x needs its model files | `bin/rails generate ahoy:install && bin/rails db:migrate` |
| `syntax_error` in controller | Stale `end` or leftover comments from bad patch | Read the file, remove duplicate `end`, clean up |
| `ActionController::RoutingError` for /dashboard | Route defined as `get "dashboard/index"` not `get "dashboard"` | Fix `config/routes.rb` |
| 500 on asset load (Tailwind) | Layout references `"application.tailwind"` but file is `tailwind.css` | Change to `stylesheet_link_tag "tailwind"` |
| `ActiveRecord::StatementInvalid: no such table` | Migration not run | `bin/rails db:migrate` |
| `NameError: uninitialized constant` (any gem) | Gem not properly installed or generator not run | Check `Gemfile.lock`, run the gem's install generator |
| `NoMethodError: undefined method 'group_by_day' for ActiveRecord::Relation` | groupdate 5.x + Rails 8.1: `@klass` is nil on Relation after `.where()` | Call `.group_by_day` on the model class with `range:` option instead of chaining after `.where()` |
| `NoMethodError: undefined method 'group_by_period' for nil` | Same as above — groupdate's `scoping{}` block hits `@klass=nil` | Same fix: use `Model.group_by_day(:col, range: start..end)` not `Model.where(...).group_by_day(:col)` |

## groupdate 5.x + Rails 8.1 Compatibility (CRITICAL)

**The bug:** groupdate 5.2.4 calls `@klass.group_by_period(...)` inside a `scoping{}` block. In Rails 8.1, `Relation#@klass` is `nil` after `.where()`, so this blows up with a confusing `undefined method 'group_by_period' for nil`.

**Symptoms:**
- `Model.where("x > ?", date).group_by_day(:col).count` → 500
- `Model.group_by_day(:col).count` → works fine (called on class, not Relation)
- Gem is installed and loads via `bundle exec ruby -e "require 'groupdate'"` — NOT a gem install issue

**The fix — always call group_by helpers on the model class, not a Relation chain:**

```ruby
# ❌ WRONG — crashes with NoMethodError on Rails 8.1
Booking.where("starts_at >= ?", 30.days.ago).group_by_day(:starts_at).sum("services.price")

# ✅ CORRECT — call on class, use range: option for filtering
Booking.group_by_day(:starts_at, range: 30.days.ago..Time.current).joins(:service).sum("services.price")
```

**Debugging checklist when this error appears:**
1. Confirm gem is installed: `bundle exec ruby -e "require 'groupdate'; puts Groupdate::VERSION"`
2. Confirm the call is on a **class** not a **Relation** — `.where().group_by_day()` fails; `.group_by_day(range: ...)` works
3. If the query also needs joins/where, chain `.joins()` / `.where()` AFTER `.group_by_day()`, or pass `range:` to group_by_day and add conditions as additional `.where()` calls
4. Restart server after code fix: `lsof -ti:3000 | xargs kill -9 2>/dev/null; bundle exec rails server -b 0.0.0.0 -p 3000`

## Tailwind CSS Asset Path (CRITICAL)

The `tailwindcss-rails` gem outputs `tailwind.css` (NOT `application.tailwind.css`) when input is at `app/assets/tailwind/application.css`.

```erb
# CORRECT
<%= stylesheet_link_tag "tailwind", "data-turbo-track": "reload" %>

# WRONG (causes 500)
<%= stylesheet_link_tag "application.tailwind", "data-turbo-track": "reload" %>
```

## Running Rails Server in Background

```python
# Use terminal(background=True), NOT shell '&'
terminal(background=True, command="cd /app && rails server -b 0.0.0.0 -p 3000")

# Then poll for output
process(action="poll", session_id="...")
```

Rails logs to `log/development.log`, NOT the terminal. Always read the log file for errors.

## acts_as_tenant Seed Pattern

```ruby
# db/seeds.rb — correct pattern
account = Account.create!(name: "Test Salon", timezone: "UTC", currency: "USD")

# Pass account: explicitly on EVERY tenant-scoped create
# Current.account alone doesn't propagate in seed context
User.create!(name: "Admin", email: "admin@test.com", password: "password123", account: account)
Client.create!(first_name: "John", account: account)
```

## Devise Generator Pitfall

Running `rails g devise User` twice creates a duplicate `AddDeviseToUsers` migration → `SQLite3::SQLException: duplicate column name: email`. Always check `db/migrate/` before re-running generators.
