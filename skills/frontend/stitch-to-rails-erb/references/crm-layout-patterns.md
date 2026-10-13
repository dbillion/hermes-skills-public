# CRM Layout Patterns (Session 2026-06-27)

## Standard Sidebar Pattern (All App Views)

Every app view (dashboard, clients, bookings, campaigns, loyalty, settings) uses this exact sidebar:

```erb
<%# Side Navigation Shell %>
<aside class="w-60 min-h-[100dvh] fixed left-0 top-0 bg-white border-r border-border z-50 flex flex-col p-8 hidden lg:flex">
  <div class="px-6 mb-8">
    <h1 class="text-xl font-bold tracking-tight text-primary">CRM Admin</h1>
    <p class="text-steel text-[12px] opacity-70">Enterprise Tier</p>
  </div>
  <nav class="flex-1 space-y-1 px-2 overflow-y-auto scrollbar-hide">
    <%= link_to dashboard_path, class: "flex items-center gap-3 px-3 py-2 rounded-lg #{active ? 'bg-primary-subtle text-primary border-l-4 border-primary font-bold' : 'text-steel hover:bg-canvas transition-colors'} group" do %>
      <svg class="w-5 h-5" ...>...</svg>
      <span class="text-sm text-steel">Dashboard</span>
    <% end %>
    <%# Repeat for clients, bookings, campaigns, loyalty, settings %>
  </nav>
  <div class="px-6 mt-8 border-t border-border pt-6 flex items-center gap-3">
    <div class="w-10 h-10 rounded-full bg-canvas flex items-center justify-center overflow-hidden">
      <div class="w-full h-full rounded-full bg-primary flex items-center justify-center text-white font-bold text-[12px]">AU</div>
    </div>
    <div>
      <p class="text-sm font-semibold text-ink leading-tight">Admin User</p>
      <p class="text-steel text-[11px]">System Owner</p>
    </div>
  </div>
</aside>
```

**Active state logic:** The current page's nav item gets `bg-primary-subtle text-primary border-l-4 border-primary font-bold`, others get `text-steel hover:bg-canvas transition-colors`.

## Mobile Navigation Pattern

```erb
<%# Mobile Nav Overlay %>
<div id="mobile-nav-overlay" class="fixed inset-0 bg-black/50 z-40 hidden lg:hidden" onclick="toggleMobileNav()"></div>

<%# Mobile Nav %>
<aside id="mobile-nav" class="fixed inset-y-0 left-0 w-60 bg-white z-50 hidden lg:hidden flex flex-col p-6">
  <div class="flex items-center justify-between mb-8">
    <h1 class="text-xl font-bold tracking-tight text-primary">CRM Admin</h1>
    <button onclick="toggleMobileNav()" class="p-2 text-steel hover:bg-canvas rounded-lg">
      <svg class="w-5 h-5" ...>...</svg>
    </button>
  </div>
  <nav class="flex-1 space-y-1 px-2 overflow-y-auto">
    <%= link_to dashboard_path, class: "flex items-center gap-3 px-3 py-2 rounded-lg text-steel hover:bg-canvas transition-colors" do %>
      ...
    <% end %>
  </nav>
</aside>
```

**Toggle button (in header):**
```erb
<button class="lg:hidden p-2 text-steel hover:bg-canvas rounded-lg" onclick="toggleMobileNav()">
  <svg class="w-5 h-5" ...>...</svg>
</button>
```

## Main Content Area

```erb
<main class="ml-0 lg:ml-60 flex flex-col min-h-[100dvh]">
  <header class="sticky top-0 z-40 bg-white border-b border-border px-4 lg:px-8 py-3 flex justify-between items-center">
    <div class="flex items-center gap-4 lg:gap-6 flex-1">
      <%# Mobile toggle button here %>
      <h2 class="text-xl font-bold tracking-tight text-ink">Page Title</h2>
      <%= form_with url: page_path, method: :get, local: true, class: "relative flex-1 max-w-md" do |f| %>
        <svg class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-steel" ...>...</svg>
        <%= f.search_field :q, class: "w-full bg-primary-subtle/30 border border-border rounded-lg py-2 pl-10 pr-4 text-sm" %>
      <% end %>
    </div>
    <div class="flex items-center gap-3">
      <%# Notification bell, help, avatar %>
    </div>
  </header>
  <section class="p-4 lg:p-8 flex-1">
    <%# Page content %>
  </section>
</main>
```

## Design System Tokens

| Token | Hex | Usage |
|-------|-----|-------|
| primary | #0D9488 | CTAs, active states, focus rings |
| primary-hover | #0F766E | Hover on primary buttons |
| primary-subtle | #CCFBF1 | Light teal backgrounds |
| canvas | #F8FAFB | Page background |
| ink | #18181B | Primary text |
| steel | #71717A | Secondary text |
| border | rgba(226,232,240,0.5) | Borders |
| success | #059669 | Positive states |
| warning | #D97706 | Caution states |
| error | #DC2626 | Error states |
| info | #0284C7 | Informational |

## Input Styling (Consistent Across All Forms)

```erb
<%# Text-like inputs %>
<input class="w-full px-4 py-3 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-spring text-sm min-h-[48px]" placeholder="..." />

<%# Search inputs %>
<input class="w-full bg-primary-subtle/30 border border-border rounded-lg py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary/20 transition-all outline-none" placeholder="..." />

<%# Select dropdowns %>
<select class="appearance-none bg-white border border-border rounded-lg px-3 pr-10 py-2 text-sm text-steel focus:ring-2 focus:ring-primary outline-none cursor-pointer">
  <option>Select...</option>
</select>
```

## Animation Classes

| Class | Effect |
|-------|--------|
| `animate-fade-up` | Fade in + slide up (0.5s spring) |
| `delay-75` | 75ms animation delay |
| `delay-150` | 150ms animation delay |
| `delay-225` | 225ms animation delay |
| `delay-300` | 300ms animation delay |
| `btn-push` | Scale(0.98) on :active |
| `transition-spring` | Cubic-bezier spring transition |
| `scrollbar-hide` | Hide scrollbar (add to @layer utilities) |
