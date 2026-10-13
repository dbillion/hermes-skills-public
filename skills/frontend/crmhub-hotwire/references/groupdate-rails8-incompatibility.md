# groupdate 5.x + Rails 8.1 Incompatibility

## Problem
`groupdate` 5.2.4 crashes on Rails 8.1.3 when groupdate methods are called on an `ActiveRecord::Relation` (created by `.where()`, `.joins()`, etc.):

```
NoMethodError (undefined method 'group_by_period' for nil):
  groupdate/enumerable.rb:8:in 'block (3 levels) in <module:Enumerable>'
    scoping { @klass.group_by_period(period, *args, **options, &block) }
```

## Root Cause
Rails 8.1 changed `ActiveRecord::Relation` internals — `@klass` is now `nil` when accessed on a Relation created via `.where()`. groupdate internally calls `@klass.group_by_period(...)` inside `scoping {}`, so `nil.receiver` blows up.

The gem works perfectly when called directly on the model class — only the Relation-chain pattern fails.

## Reproduction Steps

### 1. Confirm gem IS installed
```bash
cd /home/deeone/projects/crm_hub
bundle show groupdate
# => vendor/bundle/ruby/3.4.0/gems/groupdate-5.2.4
```

### 2. Confirm gem loads in isolation
```bash
bundle exec ruby -e "require 'groupdate'; puts Groupdate::VERSION"
# => 5.2.4
```

### 3. Confirm gem works on model class directly
```bash
bundle exec rails runner 'puts Client.group_by_day(:created_at).count.inspect'
# => {"Sat, 27 Jun 2026"=>10}  ✅ WORKS
```

### 4. Confirm gem FAILS on Relation chain
```bash
bundle exec rails runner 'puts Client.where("created_at >= ?", 30.days.ago).group_by_day(:created_at).count.inspect'
# => NoMethodError: undefined method 'group_by_period' for nil  ❌ FAILS
```

### 5. Confirm the pattern that WORKS
```bash
bundle exec rails runner 'puts Client.group_by_day(:created_at, range: 30.days.ago..Time.current).count.inspect'
# => {"Sat, 27 Jun 2026"=>10}  ✅ WORKS
```

## The Fix Pattern

Replace:
```ruby
Model.where("date_col >= ?", range_start).group_by_day(:date_col).aggregate(...)
```

With:
```ruby
Model.group_by_day(:date_col, range: range_startjoins(...).aggregate(...)
```

**Key insight:** The `.where()` filter moves INSIDE the `range:` option of groupdate, instead of being a separate scope.

## Failing Patterns (ALL of these crash)
Booking.where(...).group_by_day(:col).count
Client.where(...).group_by_week(:created_at).count
Booking.joins(:service).where(...).group_by_month(:starts_at).sum(:price)
Order.where(...).group_by_day(:created_at).count

## Working Patterns (safe on Rails 8.1)
Booking.group_by_day(:col, range: start..end).count
Client.group_by_week(:created_at, range: start..end).count
Booking.group_by_month(:starts_at, range: start..end).joins(:service).sum(:price)
Order.group_by_day(:created_at)  # without range, on class directly — also works

## Related Gems with Same Pattern
Any gem that uses `@klass` internally inside `scoping {}` on a Relation may have the same issue. If you see `undefined method 'X' for nil` inside a gem's `scoping` block, suspect the same root cause.
