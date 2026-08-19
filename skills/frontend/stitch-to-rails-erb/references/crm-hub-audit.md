# CRM Hub Project Audit Patterns

This document captures the specific audit patterns and fixes discovered during the CRM Hub project refactoring (2026-06-27). Use these as a checklist when auditing similar Rails 8 CRM projects.

## Audit Checklist

### 1. Sidebar Duplication Detection

```bash
# Find views with inline sidebar (should be extracted to partial)
grep -rl 'aside class.*w-60' app/views/ | grep -v application/

# Count: if > 1, extract to shared partial
```

**Fix**: Create `app/views/application/_sidebar.html.erb` and replace all inline sidebars with `<%= render "application/sidebar" %>`.

### 2. Tailwind Divide with rgba Colors

```bash
# Tailwind divide-* utilities don't work well with rgba border colors
grep -rn 'divide-border' app/views/
```

**Fix**: Replace `divide-border` with `divide-zinc-200` (or use inline `--tw-divide-opacity`).

### 3. Viewport Height Inconsistency

```bash
# h-[100dvh] clips content that exceeds viewport
grep -rn 'h-\[100dvh\]' app/views/
```

**Fix**: Change to `min-h-[100dvh]` to allow content expansion.

### 4. Missing content_for :title

```bash
# Views without title (exclude special files)
find app/views -name '*.erb' -not -path '*/layouts/*' -not -name 'manifest*' | while read f; do
  grep -q 'content_for.*title' "$f" || echo "MISSING: $f"
done
```

**Fix**: Add `<% content_for :title, "Page Name" %>` at the top of each view.

### 5. Legacy rails-ujs Attributes

```bash
# Rails 8 uses Turbo, not rails-ujs
grep -rn 'data-method=' app/views/    # Should use data-turbo-method
grep -rn 'data-confirm=' app/views/   # Should use data-turbo-confirm
grep -rn 'data-remote=' app/views/    # Should use turbo_frame_tag
```

**Fix**: Replace with Turbo equivalents.

### 6. OmniAuth Without turbo: false

```bash
# Social auth buttons MUST disable Turbo
grep -rn 'omniauth' app/views/ | grep -v 'turbo: false'
```

**Fix**: Add `data: { turbo: false }` to all OmniAuth buttons.

### 7. Turbo Frame Wrapping

```bash
# Check if main content is wrapped in turbo_frame_tag
for f in app/views/dashboard/index.html.erb app/views/clients/index.html.erb; do
  grep -q 'turbo_frame_tag' "$f" || echo "MISSING turbo_frame: $f"
done
```

**Fix**: Add `<%= turbo_frame_tag "main_content" do %>` wrapper and `<% end %>`.

### 8. Solid Cable Channel Setup

```bash
# Check for ActionCable channels
ls app/channels/
```

**Fix**: Create `app/channels/dashboard_channel.rb` for real-time updates, add `<%= turbo_stream_from "dashboard" %>` to views.

## Common Fix Patterns (One-liners)

```bash
# Fix divide-border across all views
find app/views -name '*.erb' -exec sed -i 's/divide-border/divide-zinc-200/g' {} \;

# Fix h-[100dvh] to min-h-[100dvh]
find app/views -name '*.erb' -exec sed -i 's/class="\(.*\)h-\[100dvh\]/class="\1min-h-[100dvh]/g' {} \;
```

## Project-Specific Metrics (CRM Hub)

| Metric | Before | After |
|--------|--------|-------|
| Sidebar lines duplicated | 264 (6×44) | 1 partial (45 lines) |
| Views with Turbo Frames | 0 | 5 |
| Views with inline sidebar | 6 | 0 |
| `divide-border` issues | 5 files | 0 |
| Real-time channels | 0 | 1 (DashboardChannel) |
| `h-[100dvh]` inconsistencies | 2 files | 0 |
