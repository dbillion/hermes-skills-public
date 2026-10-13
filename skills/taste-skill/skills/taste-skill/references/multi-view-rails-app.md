# Multi-View Rails Application Building with Taste-Skill

## When to use this

When building a complete Rails application with 10+ views (auth, dashboard, resources, settings) that must share a consistent design system, responsive breakpoints, and animated interactions.

## Architecture Pattern

```
app/views/
  pages/           → Landing page (public, no auth)
  dashboard/       → Main dashboard
  clients/         → CRUD resource views
  bookings/        → Calendar + list views
  campaigns/       → Marketing views
  settings/        → User settings
  admin/           → Admin namespace views
  devise/          → Auth views (sessions, registrations, passwords)
  layouts/
    application.html.erb  → Main layout with nav, footer
    _sidebar.html.erb    → Shared sidebar partial
    _nav.html.erb        → Shared top nav partial
```

## Responsive Strategy (Mobile-First)

Every view must declare explicit breakpoints. No "it'll work, Tailwind handles it" assumptions.

| Breakpoint | Width | Key Changes |
|---|---|---|
| Base (mobile) | < 640px | Single column, `px-4`, 48px touch targets, hidden sidebar, card lists, FAB |
| `sm:` | 640px+ | 2-col stats, expanded nav items |
| `md:` | 768px+ | 2-col card grids, sidebar collapses to icons, table view |
| `lg:` | 1024px+ | Full sidebar, split layouts, bento grids |
| `xl:` | 1280px+ | Wide containment `max-w-7xl` |

### Responsive Patterns

**Sidebar → Bottom Tabs (mobile):**
```erb
<!-- Desktop: sidebar -->
<aside class="hidden lg:block w-64 fixed left-0 top-0 h-screen">...</aside>
<!-- Mobile: bottom tab bar -->
<nav class="fixed bottom-0 left-0 right-0 lg:hidden bg-white border-t border-border z-40">
  <%= link_to dashboard_path, class: "flex-1 flex flex-col items-center py-3 #{current_page?(dashboard_path) ? 'text-primary' : 'text-steel'}" do %>
    <svg>...</svg>
    <span class="text-[10px] mt-1">Dashboard</span>
  <% end %>
</nav>
```

**Table → Card List (mobile):**
```erb
<!-- Desktop table -->
<table class="hidden sm:table w-full">...</table>
<!-- Mobile cards -->
<div class="sm:hidden divide-y divide-border">
  <% @items.each do |item| %>
    <div class="p-4"><%= item.name %></div>
  <% end %>
</div>
```

**Bento Grid → Stack (mobile):**
```erb
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-4 lg:gap-6">
  <div class="md:col-span-2 lg:col-span-8">...</div>
  <div class="lg:col-span-4">...</div>
</div>
```

**Calendar → List (mobile):**
```erb
<!-- Desktop: full calendar grid -->
<div class="hidden md:block">...</div>
<!-- Mobile: date-grouped list view -->
<div class="md:hidden">
  <div class="text-xs uppercase tracking-wider text-steel font-semibold mb-3">Today</div>
  <!-- booking cards -->
</div>
```

## Shared Partials

Extract repeated UI into partials:

- `_page_header.html.erb` — Page title + description + action buttons
- `_filter_pills.html.erb` — Horizontal scrollable filter tabs
- `_empty_state.html.erb` — Illustrated empty state with CTA
- `_stat_card.html.erb` — Metric card with count-up animation
- `_status_badge.html.erb` — Colored status pill

## View Building Workflow

1. Create the ERB template with full responsive classes
2. Add `reveal-hidden` + `data-reveal-delay="N"` to sections for scroll-reveal
3. Add `animate-fade-up delay-N` to hero/entry elements
4. Add `data-controller="magnetic"` to primary CTA buttons
5. Add `data-controller="count-up" data-count-up-target-value="N"` to metric numbers
6. Build Tailwind CSS: `npx @tailwindcss/cli -i app/assets/stylesheets/application.tailwind.css -o .stitch/output.css --minify`
7. Convert to standalone HTML for screenshot verification
8. Screenshot at 375px, 768px, 1440px breakpoints

## Parallel View Building with Subagents

For large multi-view builds, use `delegate_task` to build 2-3 views simultaneously. Each subagent gets:
- The design system context (colors, fonts, radius)
- The responsive rules
- The Stimulus controller patterns
- The file paths to write

**Fallback pattern:** If a subagent times out (common for 5+ large views), check what it completed with `find` and `wc -l`, then build the remaining views directly.

## Key Pitfalls

1. **Don't use `h-screen`** — iOS Safari jumps catastrophically. Always `min-h-[100dvh]`.
2. **Sidebar must be explicitly hidden on mobile** — `hidden lg:block`, not responsive width.
3. **Tables need mobile card fallback** — `hidden sm:table` + `sm:hidden` card list.
4. **Touch targets on mobile** — All interactive elements `min-h-[48px]` (exceeds 44px WCAG).
5. **Form inputs on mobile** — `text-base` (16px) minimum to prevent iOS zoom on focus.
6. **Filter pills horizontal scroll** — `overflow-x-auto pb-2 -mx-4 px-4` with `shrink-0` on pills.
7. **FAB on mobile, inline button on desktop** — `fixed bottom-6 right-6 md:hidden` for FAB, `md:inline-flex` for regular button.
