# acts_as_tenant Seed Pattern

When seeding a Rails 8 app with `acts_as_tenant`, you must handle tenant scoping explicitly.

## The Problem

`Current.account` set in `db/seeds.rb` may not propagate to model creation in seed context. This causes `ActiveRecord::RecordInvalid: Validation failed: Account must exist` even though you set `Current.account = account` at the top of the seed file.

## The Fix

Always pass `account:` explicitly on every tenant-scoped record:

```ruby
# db/seeds.rb
account = Account.create!(name: "Test", timezone: "UTC", currency: "USD")
Current.account = account  # Belt

# AND suspenders — pass account explicitly
User.create!(name: "Admin", email: "admin@test.com", password: "password123", account: account)
Client.create!(first_name: "John", last_name: "Doe", account: account, user: user)
Service.create!(name: "Haircut", duration: 30, price: 45, category: "Hair", active: true, account: account)
```

## Pitfall: Duplicate Devise Migrations

Running `rails g devise User` twice creates a duplicate `AddDeviseToUsers` migration that fails with `SQLite3::SQLException: duplicate column name: email`.

**Fix:** Check `db/migrate/` before re-running generators. Delete duplicate migration files manually.

## Pitfall: Running in Circles

After 2+ identical failures on the same command, STOP. Read the full stack trace, identify root cause, fix the code/config, then retry. The user will notice and call you out.
