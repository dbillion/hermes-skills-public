---
name: crmhub-hotwire
description: Build reactive CRM pages with Hotwire (Turbo Drive, Turbo Frames, Turbo Streams) and Stimulus controllers for CRMHub (Rails 8 + SQLite + Docker + Kamal). Covers frame-scoped navigation, stream-based real-time updates, Stimulus controller patterns, and Rails 8 helper conventions. NOT Laravel/Livewire — this is Rails Hotwire only.
allowed-tools:
  - read_file
  - write_file
  - patch
  - search_files
  - terminal
  - mcp_lightpanda_markdown
  - mcp_lightpanda_goto
  - mcp_lightpanda_evaluate
  - mcp_stitch_get_screen
  - mcp_stitch_list_screens
  - mcp_stitch_generate_screen_from_text
  - mcp_stitch_edit_screens
---

# CRMHub Hotwire Skill

> **Stack:** Rails 8 · SQLite · Docker · Kamal · Hotwire (Turbo + Stimulus)
> **NOT:** Laravel / Livewire / Inertia / React
> **Design system:** Teal `#0D9488` · Geist font · Zinc neutrals · 12px border-radius · `min-h-[100dvh]`

## Overview

CRMHub uses Hotwire to deliver reactive, SPA-like CRM pages without a JavaScript framework. Turbo Drive intercepts navigation, Turbo Frames scope partial swaps, Turbo Streams push real-time DOM updates over WebSocket or form responses, and Stimulus augments HTML with lightweight controller logic. This skill provides numbered rules, reference patterns, and reusable templates for every common CRM page scenario.

**⚠️ CRITICAL: This is RAILS 8 + HOTWIRE. NOT Laravel/Livewire/Inertia/React/Vue/Alpine. Never research or reference Livewire docs for a Rails project. The user will correct you immediately.**

---

## Rules

### 1. Always Use Turbo Drive — Never Write `fetch()` for Page Navigation

Turbo Drive automatically intercepts all `<a>` clicks and form submits, fetches the HTML, and swaps `<body>` without a full page reload. **Never** write custom `fetch()` or `XMLHttpRequest` for navigation. If you need to opt out of Turbo Drive for a specific link, use `data-turbo="false"`. If you need to disable Turbo globally (you shouldn't), use `Turbo.session.drive = false` in `application.js`.

```html
<!-- ✅ Default: Turbo Drive handles this automatically -->
<%= link_to "Clients", clients_path, class: "text-teal-600 hover:underline" %>

<!-- ✅ Opt out for external links or downloads -->
<%= link_to "Export CSV", export_clients_path(format: :csv), data: { turbo: false } %>
```

### 2. Scope Partial Updates with `turbo_frame_tag` — One Frame Per Updateable Region

Every region of a page that updates independently must be wrapped in a `turbo_frame_tag` with a unique `id`. When a link or form inside a frame is activated, Turbo fetches the response, extracts the matching `<turbo-frame id="...">` from it, and swaps only that frame's content. The rest of the page stays untouched.

```erb
<!-- Index page: client list is a frame -->
<%= turbo_frame_tag "clients_list" do %>
  <% @clients.each do |client| %>
    <div class="rounded-xl border border-zinc-200 p-4">
      <%= link_to client.name, client_path(client), data: { turbo_frame: "client_detail" } %>
    </div>
  <% end %>
<% end %>

<!-- Same index page: detail panel is a separate frame -->
<%= turbo_frame_tag "client_detail" do %>
  <p class="text-zinc-500">Select a client to view details.</p>
<% end %>
```

### 3. Use Turbo Streams for Create / Update / Destroy — Never Redirect After Form Submit

When a form creates, updates, or destroys a record, the controller must respond with `turbo_stream` format, **not** a redirect. Turbo Streams deliver `<turbo-stream>` elements that perform DOM actions (append, prepend, replace, update, remove, before, after, refresh). A redirect causes Turbo Drive to follow it and swap the whole page, defeating the purpose.

```ruby
# ✅ Correct: respond with turbo_stream
def create
  @client = Client.create!(client_params)
  respond_to do |format|
    format.turbo_stream
    format.html { redirect_to @client }
  end
end

# ❌ Wrong: redirect breaks the stream
def create
  @client = Client.create!(client_params)
  redirect_to @client  # Turbo follows redirect, swaps whole page
end
```

### 4. Know All Eight Turbo Stream Actions — Use the Right One

| Action | Effect | CRM Use Case |
|---|---|---|
| `append` | Insert as last child of target | Add new appointment to end of list |
| `prepend` | Insert as first child of target | Add new client to top of list |
| `replace` | Replace entire target element | Update edited form with saved record |
| `update` | Replace only target's children | Update count badge without replacing wrapper |
| `remove` | Remove target element entirely | Delete a client card |
| `before` | Insert before target element | Insert a flash message above a section |
| `after` | Insert after target element | Insert a status row below a header |
| `refresh` | Re-fetch target from server via fetch | Auto-refresh a dashboard section |

```erb
<%# app/views/clients/create.turbo_stream.erb %>
<%= turbo_stream.prepend "clients_list", @client %>
<%= turbo_stream.replace "client_form", partial: "clients/form", locals: { client: Client.new } %>
<%= turbo_stream.update "clients_count", @clients.count %>
<%= turbo_stream.append "flash_messages", partial: "shared/flash", locals: { message: "Client created" } %>
```

### 5. Subscribe to Real-Time Updates with `turbo_stream_from` + Broadcasts

For live updates (new appointment, status change, message received), use `turbo_stream_from` on the page to open a WebSocket subscription, and call `broadcasts_to` / `broadcast` in the model to push Turbo Stream actions to all connected clients.

```erb
<!-- Show page: subscribe to this client's stream -->
<%= turbo_stream_from @client %>

<div id="<%= dom_id(@client) %>">
  <h2><%= @client.name %></h2>
  <span data-controller="status-badge"><%= @client.status %></span>
</div>
```

```ruby
# app/models/client.rb
class Client < ApplicationRecord
  after_create_commit  -> { broadcast_prepend_to "clients", target: "clients_list", partial: "clients/client", locals: { client: self } }
  after_update_commit  -> { broadcast_replace_to "clients", target: "clients_list", partial: "clients/client", locals: { client: self } }
  after_destroy_commit -> { broadcast_remove_to "clients", target: dom_id(self) }
end
```

### 6. Every Stimulus Controller Follows the Same Skeleton — `data-controller`, Targets, Values, Actions

Stimulus controllers are registered with `data-controller="name"`, reference elements with `data-{controller}-target="name"` (declared in `static targets`), accept typed values via `data-{controller}-{value}-value` (declared in `static values`), and respond to events via `data-action="event->controller#method"`.

```javascript
// app/javascript/controllers/appearance_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["button", "icon"]
  static values = { theme: String, persist: { type: Boolean, default: false } }

  connect() {
    this.themeValue = localStorage.getItem("theme") || "light"
    this.applyTheme()
  }

  toggle() {
    this.themeValue = this.themeValue === "light" ? "dark" : "light"
    if (this.persistValue) localStorage.setItem("theme", this.themeValue)
    this.applyTheme()
  }

  applyTheme() {
    document.documentElement.classList.toggle("dark", this.themeValue === "dark")
    this.iconTarget.textContent = this.themeValue === "dark" ? "☀️" : "🌙"
  }

  // Runs when element leaves the DOM
  disconnect() {
    // Cleanup: remove listeners, clear intervals, etc.
  }
}
```

```html
<div data-controller="appearance" data-appearance-persist-value="true">
  <button data-action="click->appearance#toggle" data-appearance-target="button">
    <span data-appearance-target="icon">🌙</span>
  </button>
</div>
```

### 7. Use `data-turbo-frame` to Control Where a Link/Form Renders — Not Full Page Swap

When a link or form should update a specific frame on the page (not navigate away), add `data-turbo-frame="frame_id"` to the link or form element. This tells Turbo to extract only the matching frame from the response.

```erb
<!-- Link renders into the detail frame, not the whole page -->
<%= link_to client.name, client_path(client),
      data: { turbo_frame: "client_detail" },
      class: "hover:text-teal-600" %>

<!-- Form submits into a specific frame -->
<%= form_with model: @appointment,
      data: { turbo_frame: "appointments_list" } do |f| %>
  <%# ... %>
<% end %>
```

### 8. Use `button_to` with `turbo_method` and `turbo_confirm` for Destructive Actions — Never Raw Links

Destructive actions (delete, archive, deactivate) must use `button_to` with `data: { turbo_method: :delete, turbo_confirm: "Are you sure?" }`. Never use `link_to ... method: :delete` — it generates a `<form>` with a hidden `_method` input, which is fragile and not Turbo-native.

**⚠️ CRITICAL: Do NOT use `button_to ... do | ... end` (block form) with `data: { turbo_method: :delete }`.** This triggers `ActionView::stringify_keys` crash in Rails 8. Use the non-block form below, or switch to `form_with` if you need a block with custom HTML content.

```erb
<%= button_to "Delete", client_path(@client),
      method: :delete,
      data: { turbo_confirm: "Permanently delete this client? This cannot be undone." },
      class: "bg-red-500 text-white rounded-xl px-4 py-2 hover:bg-red-600" %>
```

### 9. Use `data-turbo-action="advance"` to Update URL Without Full Reload — For Frame Navigation That Should Be Bookmarkable

When navigating within a Turbo Frame (e.g., clicking a client in a list to see their detail), you may want the URL to update so the page is bookmarkable and the browser back button works. Add `data-turbo-action="advance"` to the link.

```erb
<%= link_to client.name, client_path(client),
      data: { turbo_frame: "client_detail", turbo_action: "advance" } %>
```

### 10. Use `request.referrer` or `params[:return_to]` for Cancel/Back Buttons — Never Hardcode Paths

Cancel buttons on forms should return to where the user came from. Use `request.referrer` or a `return_to` param, and always wrap in `turbo_frame` context so only the frame swaps.

```erb
<%= link_to "Cancel", request.referrer || clients_path,
      data: { turbo_frame: "_top" },
      class: "text-zinc-500 hover:underline" %>
```

Use `data-turbo-frame="_top"` to break out of frame-scoped navigation and return to full-page context.

### 11. Tailwind v4 Design System — Colors, Typography, Spacing, Components

CRMHub uses **Tailwind CSS v4** with `@theme` tokens (CSS-first, no `tailwind.config.js`). All design tokens are defined in `app/assets/tailwind/application.css`.

#### ⚠️ CRITICAL: Tailwind v4 Scanner Does NOT Detect Arbitrary Values in ERB Files

Tailwind v4's class scanner parses source files to find classes to compile. **It does NOT detect arbitrary-value classes like `text-[11px]`, `text-[32px]`, `active:scale-[0.98]`, `h-[400px]` in ERB files.** These classes silently disappear from the compiled CSS output, causing unstyled text and broken layouts on production.

**Rule: Replace ALL arbitrary-value classes in ERB with standard Tailwind equivalents.**

| Arbitrary (BROKEN) | Standard (WORKS) |
|---|---|
| `text-[9px]`, `text-[10px]`, `text-[11px]`, `text-[12px]` | `text-xs` (12px) |
| `text-[13px]`, `text-[14px]`, `text-[16px]` | `text-sm` (14px) |
| `text-[18px]` | `text-lg` (18px) |
| `text-[20px]` | `text-xl` (20px, exact match) |
| `text-[24px]` | `text-2xl` (24px) |
| `text-[28px]` | `text-2xl` (24px, closest) |
| `text-[32px]` | `text-3xl` (30px) |
| `active:scale-[0.98]` | `active:scale-95` |
| `active:scale-[0.97]` | `active:scale-97` |
| `active:translate-y-[1px]` | `active:translate-y-px` |

**Fix pattern — bulk replace in all views:**
```python
# Run via execute_code tool
patterns = [
    ('text-[9px]', 'text-xs'), ('text-[10px]', 'text-xs'), ('text-[11px]', 'text-xs'), ('text-[12px]', 'text-xs'),
    ('text-[13px]', 'text-sm'), ('text-[14px]', 'text-sm'), ('text-[15px]', 'text-sm'), ('text-[16px]', 'text-sm'),
    ('text-[18px]', 'text-lg'), ('text-[20px]', 'text-xl'), ('text-[24px]', 'text-2xl'), ('text-[28px]', 'text-2xl'),
    ('text-[32px]', 'text-3xl'), ('active:scale-[0.98]', 'active:scale-95'), ('active:scale-[0.97]', 'active:scale-97'),
    ('active:translate-y-[1px]', 'active:translate-y-px'),
]
```

**Material symbols `text-[NNpx]` (icon sizes):**
| Arbitrary | Standard |
|---|---|
| `text-[14px]` for icons | `text-sm` |
| `text-[18px]` for icons | `text-lg` |
| `text-[28px]` for FAB icons | `text-2xl` |

#### Tailwind v4 CSS Architecture: `@theme` + `@layer components`

Use both layers together — `@theme` for design tokens, `@layer components` for explicit utility definitions that the scanner might miss:

```css
@import "tailwindcss";

@theme {
  --color-primary: #0D9488;
  --color-primary-hover: #0F766E;
  /* ... other color tokens ... */
  --font-geist: "Geist", system-ui, sans-serif;
}

@layer components {
  /* Design system classes that ARE in ERB views */
  .text-page-title { font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; }
  .text-section-heading { font-size: 1.25rem; font-weight: 600; }
  .font-page-title { letter-spacing: -0.02em; font-size: 2rem; font-weight: 700; }
  /* Custom colors from @theme are automatically available as Tailwind classes */
  .bg-on-primary { background-color: #FFFFFF; }
  .hover\:bg-accent-hover:hover { background-color: #D97706; }
  .hover\:bg-primary-hover:hover { background-color: #0F766E; }
  .hover\:bg-primary\/20:hover { background-color: rgba(13,148,136,0.13); }
  /* Standard utilities not auto-generated from @theme */
  .font-semibold { font-weight: 600; }
  .font-bold { font-weight: 700; }
  .font-mono { font-family: Geist Mono, monospace; }
  .uppercase { text-transform: uppercase; }
  .tracking-widest { letter-spacing: 0.1em; }
  .truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
}
```

**After editing `application.css`, rebuild:**
```bash
cd /home/deeone/projects/crm_hub
bundle exec bin/rails tailwindcss:build
```

**Verify custom classes compile:**
```bash
grep "page-title\|section-heading\|accent-hover" app/assets/builds/tailwind.css | sort | uniq -c
```

#### Color Tokens (`@theme` in `application.css`)

| Token | Hex | Tailwind Class | Usage |
|-------|-----|---------------|-------|
| primary | `#0D9488` | `bg-primary`, `text-primary` | CTAs, active states, focus rings |
| primary-hover | `#0F766E` | `hover:bg-primary-hover` | Hover on primary buttons |
| primary-subtle | `#CCFBF1` | `bg-primary-subtle`, `text-primary-subtle` | Light teal backgrounds, active nav items |
| primary-fixed | `#89F5E7` | `bg-primary-fixed` | Accent backgrounds |
| canvas | `#F8FAFB` | `bg-canvas` | Page background |
| surface | `#FFFFFF` | `bg-surface`, `bg-white` | Card backgrounds |
| ink | `#18181B` | `text-ink` | Primary text, headings |
| steel | `#71717A` | `text-steel` | Secondary text, metadata, timestamps |
| border | `rgba(226,232,240,0.5)` | `border-border`, `border` | Card borders, dividers |
| success | `#059669` | `bg-success/10`, `text-success` | Positive states, confirmed badges |
| warning | `#D97706` | `bg-warning/10`, `text-warning` | Caution states, pending badges |
| error | `#DC2626` | `bg-error/10`, `text-error` | Error states, delete actions |
| info | `#0284C7` | `bg-info/10`, `text-info` | Informational |

#### Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font-geist` | `"Geist", system-ui, sans-serif` | All body text, navigation, labels |
| `--font-mono` | `"Geist Mono", "JetBrains Mono", monospace` | Prices, timestamps, metrics, IDs, phone numbers |

**Font loading** (in layout `<head>`):
```html
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@100..900&family=Geist+Mono:wght@100..800&display=swap" rel="stylesheet">
```

#### Spacing & Sizing

| Token | Value | Class | Usage |
|-------|-------|-------|-------|
| sidebar width | `240px` | `w-60` (24 via w-60 = 15rem = 240px) | Main navigation sidebar |
| sidebar collapsed | `64px` | `w-16` | Collapsed sidebar |
| max content | `1280px` | `max-w-7xl` | Centered content area |
| base spacing | `4px` | — | All spacing multiples of 4 |
| card padding | `20px` | `p-5` (1.25rem = 20px) | Card internal padding |
| section gaps | `32px` | `gap-8` (2rem = 32px) | Between major layout sections |
| card gaps | `16px` | `gap-4` | Grid layouts, form fields |

#### Border Radius

| Usage | Class |
|-------|-------|
| Buttons, inputs | `rounded-lg` (8px) — NOT `rounded-xl` for inputs per Stitch |
| Cards, panels | `rounded-xl` (12px) — standard card |
| Large panels | `rounded-2xl` (16px) — hero cards |
| Status badges | `rounded-full` — pills |

#### Component Patterns

**Cards:**
```erb
<div class="bg-white rounded-xl border border-border p-6 shadow-sm hover:shadow-md transition-shadow">
  <!-- card content -->
</div>
```

**Sidebar Navigation Item (active):**
```erb
"flex items-center gap-3 px-3 py-2 rounded-lg bg-primary-subtle text-primary border-l-4 border-primary font-bold transition-spring group"
```

**Sidebar Navigation Item (inactive):**
```erb
"flex items-center gap-3 px-3 py-2 rounded-lg text-steel hover:bg-canvas transition-colors group"
```

**Primary Button:**
```erb
class: "px-4 py-2.5 bg-primary text-white rounded-xl font-medium hover:bg-primary-hover transition-spring btn-push"
```

**Secondary/Ghost Button:**
```erb
class: "px-4 py-2.5 border border-border text-ink rounded-xl font-medium hover:bg-canvas transition-spring"
```

**Destructive Button:**
```erb
class: "px-4 py-2.5 bg-error text-white rounded-xl font-medium hover:bg-error/90 transition-spring"
```

**Status Badges:**
```erb
# confirmed/scheduled/active/sending: "bg-success/10 text-success"
# pending: "bg-warning/10 text-warning"
# completed: "bg-primary/10 text-primary"
# cancelled/no_show/failed/bounced: "bg-error/10 text-error"
# inactive/draft/churned: "bg-zinc-100 text-steel"

<span class="text-xs px-2.5 py-1 rounded-full font-medium bg-success/10 text-success">
  <%= status %>
</span>
```

**Data Tables:**
```erb
<div class="bg-white rounded-xl border border-border overflow-hidden">
  <table class="w-full">
    <thead class="bg-canvas border-b border-border">
      <tr>
        <th class="text-left px-6 py-3 text-xs font-semibold text-steel uppercase tracking-wider">Header</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-border">
      <tr class="hover:bg-canvas transition-colors">
        <td class="px-6 py-4 text-sm font-medium text-ink">Value</td>
      </tr>
    </tbody>
  </table>
</div>
```

**Form Inputs (using form_with):**
```erb
<div class="space-y-2">
  <%= f.label :field, class: "block text-sm font-medium text-ink" %>
  <%= f.text_field :field,
      class: "w-full px-4 py-3 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm" %>
</div>
```

**Avatar/Initials:**
```erb
<div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white font-bold text-xs">
  <%= user.initials %>
</div>
```

**Touchable minimum:** All clickable elements must be at least `min-h-[48px]`.

**Flash Messages:**
```erb
<div class="fixed bottom-4 right-4 z-50 space-y-2" id="flash_messages" data-turbo-permanent>
  <% flash.each do |type, message| %>
    <div class="rounded-xl px-4 py-3 shadow-lg <%= type == "notice" ? "bg-primary text-white" : "bg-error text-white" %>"
         data-controller="flash">
      <%= message %>
    </div>
  <% end %>
</div>
```

#### Animation Classes

```css
/* In application.css */
.animate-fade-up { animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.btn-push:active { transform: scale(0.98) translateY(1px); transition: transform 0.1s; }
.transition-spring { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
```

#### Stitch-to-ERB Conversion Quick Reference

When converting Stitch HTML to ERB (per stitch-to-rails-erb skill):

| Stitch Pattern | Rails ERB |
|---|---|
| `<form onsubmit="return false;">` | `<%= form_with model: @x, local: true, class: "space-y-6" do \|f\| %>` |
| `<input type="email">` | `<%= f.email_field :email, class: "w-full px-4 py-3 rounded-xl border border-border..." %>` |
| `<button type="submit">` | `<%= f.submit "Save", class: "..." %>` |
| `<a href="#clients">` | `<%= link_to "Clients", clients_path, class: "..." %>` |
| `<span class="material-symbols-outlined">users</span>` | `<svg ...>...</svg>` (Heroicons) |
| Custom color `#00685f` | `primary` (#0D9488) |
| Custom color `#656467` | `steel` (#71717A) |
| Custom color `eaefed` | `canvas` (#F8FAFB) |
| `border-radius: 12px` | `rounded-xl` |
| `border-radius: 8px` | `rounded-lg` |
| Custom `<style>` animations | Move to `application.css` as Tailwind utilities |

#### Layout Shell

```erb
<!-- app/views/layouts/application.html.erb -->
<!-- IMPORTANT: Do NOT render sidebar in the layout. Each authenticated view renders it explicitly. -->
<!-- This avoids double sidebar when subagents add sidebar to views. -->
<body class="min-h-[100dvh] bg-canvas text-ink antialiased font-geist">
  <!-- Flash messages -->
  <%= turbo_frame_tag "flash_messages", data: { turbo_permanent: true },
      class: "fixed bottom-4 right-4 z-50 space-y-2" %>

  <%= yield %>
</body>
```

**Authenticated views must start with:**
```erb
<%= render "application/sidebar" %>
```
This ensures the sidebar appears. Public pages (landing, auth) should NOT include the sidebar.

**Appended Content:**

### 12. Test Every Turbo Interaction — Verify Frames Swap, Streams Broadcast, Controllers Connect

For every Hotwire feature, verify:

1. **Frame swap:** Click a link inside a frame → only the frame content changes, URL does not change (unless `turbo-action="advance"`).
2. **Stream response:** Submit a form → response contains `<turbo-stream>` elements, not a redirect.
3. **Broadcast:** Open two browser tabs → create a record in one → it appears in the other via WebSocket.
4. **Controller connect:** Load page → check browser console for `connect()` log → verify DOM reflects controller logic.
5. **Controller cleanup:** Navigate away → verify `disconnect()` ran (no orphaned listeners, intervals cleared).

```ruby
# spec/system/client_management_spec.rb
require "system_helper"

RSpec.describe "Client Management", type: :system do
  it "creates a client via Turbo Stream" do
    visit clients_path
    fill_in "client_name", with: "Acme Salon"
    click_button "Create Client"
    within "#clients_list" do
      expect(page).to have_text("Acme Salon")
    end
    expect(page).not_to have_current_path(new_client_path)
  end

  it "updates a client in real-time across tabs" do
    visit client_path(@client)
    window = open_window { visit client_path(@client) }
    within_window(window) { click_button "Activate" }
    expect(page).to have_text("Active")  # Updated via broadcast
  end
end
```

### 15. Role-Based Dashboard Architecture — Different Views Per User Role

When the CRM requires **different dashboards per user role** (owner, manager, stylist, receptionist), use a **partial-based architecture** where `dashboard#index` renders a role-specific partial. Each role gets its own Stitch-designed HTML page with completely different widgets, data scopes, and button layouts.

**File structure:**
```
app/views/dashboard/
├── index.html.erb              # Router: <%= render "dashboard/#{@role}" %>
├── _owner.html.erb             # Metrics: clients, revenue, campaigns, loyalty
├── _manager.html.erb           # Revenue + staff roster + appointment grid
├── _stylist.html.erb           # Commission + my appointments + client notes
├── _receptionist.html.erb      # Booking grid with check-in/out + walk-in form
├── _admin.html.erb             # System health
└── _sidebar.html.erb           # Role-aware navigation (shared)
```

**Controller:**
```ruby
class DashboardController < ApplicationController
  def index
    @role = current_user.role_name
    load_role_data
  end

  private

  def load_role_data
    case @role
    when "owner"
      @clients_count = Client.count
      @revenue_today = Booking.joins(:service)
        .where("date(bookings.starts_at) = ?", Date.today).sum(:price)
    when "manager"
      @staff_on_floor = User.joins(:roles).where(roles: { name: "stylist" }).limit(6)
      @todays_bookings = Booking.where("date(starts_at) = ?", Date.today)
        .order(:starts_at).limit(20)
    when "stylist"
      # SCOPED TO CURRENT USER — only see own data
      @my_bookings_today = Booking.where(user: current_user)
        .where("date(starts_at) = ?", Date.today).order(:starts_at)
      @my_bookings_next48 = Booking.where(user: current_user,
        starts_at: Time.current..48.hours.from_now).order(:starts_at).limit(5)
    when "receptionist"
      @todays_bookings = Booking.where("date(starts_at) = ?", Date.today).order(:starts_at)
      @stylists = User.joins(:roles).where(roles: { name: "stylist" })
      @services = Service.where(active: true).order(:name)
    end
  end
end
```

**⚠️ CRITICAL: Data Scoping by Role**
- **Stylist** sees ONLY `Booking.where(user: current_user)` — never all shop bookings
- **Manager/Owner** sees aggregate data across all users
- **Receptionist** sees today's bookings for ALL stylists (to check people in) but NOT revenue/commissions

**⚠️ `where()` Syntax Pitfall with Mixed Conditions:**
```ruby
# WRONG — SyntaxError: unexpected ','
Booking.where(user: current_user, "date(starts_at) = ?", Date.today)
# CORRECT — chain separate where calls
Booking.where(user: current_user).where("date(starts_at) = ?", Date.today)
```

**Role-specific buttons have different targets:**
| Button | Role | Target |
|--------|------|--------|
| New Appointment | Manager | `new_booking_path` |
| New Booking FAB | Stylist | `new_booking_path` |
| Check-in / Check-out | Receptionist | `button_to booking_path(b), method: :patch, params: { booking: { status: :confirmed } }` |
| View All | Manager/Owner | `bookings_path` |
| View Full Report | Stylist | `analytics_path` |

**Sidebar Role Visibility:**
```erb
<% if %w[owner manager].include?(@role) %>
  <!-- Campaigns, Analytics, Staff, Settings -->
<% end %>
<% if %w[owner manager stylist].include?(@role) %>
  <!-- Loyalty -->
<% end %>
```

**Verification — test ALL roles (not just owner):**
```bash
for email in owner@glowhair.com manager@glowhair.com elena@glowhair.com front@glowhair.com; do
  TOKEN=*** -s -c /tmp/crm_test.txt http://localhost:3000/users/sign_in | grep -oP 'name="authenticity_token" value="\K[^"]+')
  curl -s -b /tmp/crm_test.txt -c /tmp/crm_test.txt -X POST http://localhost:3000/users/sign_in -d "authenticity_token=${TOKEN}&user[email]=${email}&user[password]=password123" -o /dev/null
  CODE=$(curl -s -b /tmp/crm_test.txt http://localhost:30w "%{http_code}")
  echo "${email}: HTTP ${CODE}"
done
```

**FAB (Floating Action Button) Pattern:**
```erb
<% if @role == "stylist" %>
  <%= link_to new_booking_path,
      class: "fixed bottom-8 right-8 w-14 h-14 bg-primary text-white rounded-full shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 transition-all flex items-center justify-center z-40" do %>
    <span class="material-symbols-outlined text-[28px]" style="font-variation-settings: 'FILL' 1;">add</span>
  <% end %>
<% end %>
```

---

Elements like a live search input, a toast container, or a media player should survive Turbo Drive page swaps. Add `data-turbo-permanent` and ensure the element has a stable `id`. Turbo matches the `id` between old and new pages and keeps the old element in place.

```erb
<div id="toast_container" data-turbo-permanent
     class="fixed bottom-4 right-4 z-50 space-y-2">
  <!-- Toasts appended here survive page navigation -->
</div>
```

### 14. Use Stimulus `values` for Configuration — Never Hardcode in Controller Logic

Stimulus `static values` provide typed, declarative configuration that can be set per-instance from HTML data attributes. Always use them instead of reading `this.element.dataset` directly or hardcoding constants.

```javascript
// ✅ Configurable via HTML attributes
export default class extends Controller {
  static values = {
    url: String,           // data-chart-url-value="/dashboard/data.json"
    interval: { type: Number, default: 30 },  // data-chart-interval-value="60"
    animate: { type: Boolean, default: true }  // data-chart-animate-value="false"
  }
  connect() {
    this.refresh()
    if (this.intervalValue > 0) {
      this.timer = setInterval(() => this.refresh(), this.intervalValue * 1000)
    }
  }
  disconnect() { clearInterval(this.timer) }
}
```

```html
<div data-controller="chart"
     data-chart-url-value="/dashboard/revenue.json"
     data-chart-interval-value="60"
     data-chart-animate-value="true">
</div>
```

---

## Lessons Learned (Session 2026-06-27 — Updated)

### User Workflow Preferences (CRITICAL)

⚠️ **"You single handedly ruined it"** — After 2+ identical errors, STOP iterating the same fix and DIAGNOSE. Root cause analysis > repeated attempts.

⚠️ **"The html has picture element you could have rendered with perfect integrity"** — `<picture>` elements and `<img>` tags are intentional design assets. They MUST be converted 1:1.

⚠️ **"Do it for all the pages, not all the charts are showing"** — When fixing CSS, charts, or layout issues, apply fixes universally across ALL pages, not just a sample. The user will notice when only some pages look right.

⚠️ **Tailwind v4 scanner does NOT detect arbitrary values in ERB** — Classes like `text-[11px]`, `text-[32px]`, `active:scale-[0.98]` are silently DROPPED from compiled CSS. This is a CORE skill fact — always replace arbitrary values in ERB with standard Tailwind equivalents. See Section 11 for the complete mapping table.

⚠️ **CSS rebuild required after any edit to `application.css`** — Just saving the CSS file doesn't recompile. Always run `bundle exec bin/rails tailwindcss:build` and restart the Rails server to get a new asset hash.

⚠️ **Use `grep -c` correctly** — `grep -c` counts MATCHING LINES, not occurrences. After building CSS, verify with `grep -o "class-name" compiled.css | sort | uniq -c` to count actual matches.

⚠️ **Don't assume the CSS was the problem** — Landing page worked because it used standard classes (`bg-primary`, `text-steel`). Authenticated pages used custom tokens that weren't being compiled. Before rebuilding CSS from scratch, verify what the compiled output actually contains.

⚠️ **CSRF auth for testing** — When verifying auth-gated pages with `curl`, the CSRF token format from Devise is `name="authenticity_token" value="..."` not `csrf-token" content="..."`. Use the correct regex: `grep -oP 'authenticity_token" value="\K[^"]+'`.

⚠️ **Use context 7 mcp when in doubt** — For gem compatibility research and version questions, use Context 7 MCP tools before installing. Don't guess versions.

⚠️ **Don't delegate 11+ page conversions to one subagent** — Subagents time out at 600s. Break page conversions into batches of 3 pages max per subagent.

⚠️ **gcloud CLI cannot create OAuth client credentials** — For Google OAuth setup, you MUST use the Google Cloud Console web UI.

⚠️ **Server dies with SIGTERM on port conflict** — The Rails server process (`proc_...`) exits with code -15 when killed. Always restart with `kill $(cat tmp/pids/server.pid); sleep 1; bundle exec rails server`.

⚠️ **groupdate + Rails 8.1** — `@klass` is nil on chained Relations. Call on model CLASS only. See `references/groupdate-rails8-incompatibility.md`.

### Authenticated Page Screenshot Strategy
When converting auth-gated pages, `curl` returns 302 (redirect to sign-in) — you CANNOT verify content without a session. Solution: use `curl` + cookie jar to authenticate, then verify:
```bash
# Get CSRF token from sign-in page
TOKEN=$(curl -s http://localhost:3000/users/sign_in | grep -oP 'authenticity_token" value="\K[^"]+')

# Post credentials, save cookie
curl -s -c /tmp/cookies.txt -X POST http://localhost:3000/users/sign_in \
  -d "user[email]=owner@glowhair.com&user[password]=password123&authenticity_token=$TOKEN"

# Now you can verify protected pages
curl -s -b /tmp/cookies.txt http://localhost:3000/dashboard

### `button_to` with `do` Block + `data:` Hash Causes `stringify_keys` Crash (Rails 8)
⚠️ **This actually happened in production.** `button_to "Label", path, method: :delete, data: { turbo_method: :delete } do %>` triggers:
```
ActionView::Template::Error (undefined method 'stringify_keys' for an instance of String)
```
The block form of `button_to` combined with a `data:` hash causes Rails to misinterpret the label string as an options hash.

**Fix:** Use `form_with url: ..., method: :delete` + `<button type="submit">` instead:
```erb
<%= form_with url: destroy_user_session_path, method: :delete do |f| %>
  <button type="submit" class="...">
    <svg>...</svg>
    Sign Out
  </button>
<% end %>
```
**Rule:** `button_to` WITHOUT a block is safe. `button_to ... do | ... end` with `data:` is NOT. Use `form_with` for block-style destructive buttons.

### Double Sidebar Pitfall
When the layout renders `<%= render "application/sidebar" %>` AND individual views also render it, you get TWO sidebars. **Fix:** Remove sidebar from layout entirely. Each authenticated view starts with `<%= render "application/sidebar" %>`. Public pages (landing, auth) do NOT render sidebar.

**Correct layout pattern:**
```erb
<!-- app/views/layouts/application.html.erb -->
<body class="font-geist antialiased bg-canvas text-ink">
  <%= turbo_frame_tag "flash_messages", data: { turbo_permanent: true }, class: "fixed bottom-4 right-4 z-50 space-y-2" %>
  <%= yield %>
</body>
```

**Authenticated view pattern (every dashboard/resource page):**
```erb
<% content_for :title, "Page Title" %>
<%= render "application/sidebar" %>
<main class="ml-60 min-h-[100dvh]">
  <!-- page content -->
</main>
```

**Public page pattern (landing, auth):**
```erb
<% content_for :title, "Page Title" %>
<!-- NO sidebar render — just the page content with its own nav -->
```

### Image Fidelity in Stitch → ERB Conversion
When converting Stitch HTML, ALL `<img>`, `<picture>`, and `<source>` tags must be preserved with their exact `src`/`srcset` URLs. These are intentional design elements — not replaceable with placeholders or `class="hidden"`.

**Stitch image URL patterns:**
- `lh3.googleusercontent.com/aida-public/...` — AIDA-generated illustrations (avatars, hero images, product previews)
- `picsum.photos/seed/xxx/W/H` — Placeholder images used by Stitch for mockups

**Both must be preserved.** A view with 0 `<img>` tags when the Stitch source has 3+ is a fidelity failure.

**Session proof:** The assistant once added `<img ... class="hidden">` to a view that needed images — rendering them invisible. Never hide images that are meant to be visible. Also, adding `<img>` with `class="hidden"` does NOT satisfy the fidelity requirement — it's just a hidden image taking up 0 space.

**Correct approach:** When the Stitch HTML has an image, the ERB must have that same image in the same position with the same visibility. If the image is visible in Stitch, it must be visible in ERB.

**Verification:** Compare image counts between Stitch HTML and ERB view. They should match.
```bash
# Count images in Stitch HTML
grep -c '<img\|<picture' /home/deeone/projects/.stitch/designs/PAGE.html

# Count images in ERB view
grep -c '<img\|<picture' /home/deeone/projects/crm_hub/app/views/PATH/PAGE.html.erb
```

### Google OAuth for Desktop Apps
When adding Google sign-in to a shared desktop app:
- **gcloud CLI CANNOT create OAuth client credentials** — you MUST use Google Cloud Console web UI
- Use `prompt: 'select_account'` to force account picker (critical for shared machines)
- Store credentials in `~/.openclaw/credentials/google-oauth.json` (never commit)
- Link Google accounts to existing users by email
- See `references/google-oauth-desktop.md` for full setup guide

### groupdate 5.x + Rails 8.1 Incompatibility (CRITICAL)
`Model.where(...).group_by_day(:col)` crashes with `NoMethodError: undefined method 'group_by_period' for nil` because Rails 8.1 sets `@klass = nil` on Relation after `.where()`. groupdate internally calls `@klass.group_by_period(...)` inside `scoping {}`, so `@klass` being nil causes the crash.

**Debugging path (for any "gem works in isolation but 500 at runtime"):**
1. Check gem IS installed: `bundle show groupdate`
2. Check gem loads: `bundle exec ruby -e "require 'groupdate'; puts Groupdate::VERSION"`
3. Check the ACTUAL error in `log/development.log` — NOT the error you expect. The error text says `group_by_period for nil` but the root cause is `@klass = nil`, not a missing method.
4. Isolate the failing pattern: try calling on the model CLASS directly vs. on a Relation chain.

**Fix:** Call groupdate methods on the model CLASS, not a Relationrange:` option for date filtering:
```ruby
# ❌ WRONG — crashes on Rails 8.1 with "group_by_period for nil"
Booking.where("starts_at >= ?", 30.days.ago).group_by_day(:starts_at).sum("services.price")
# ✅ CORRECT — call on class, use range: option
Booking.group_by_day(:starts_at, range: 30.days.ago..Time.current).joins(:service).sum("services.price")
```

**Same pattern applies to:** `group_by_week`, `group_by_month`, `group_by_year`, `group_by_hour`, and any groupdate method chained after `.where()` or `.joins()` that returns a Relation.

### Chartkick + Chart.js Setup (Rails 8 + Importmap)
For analytics dashboards, use Chartkick with Chart.js via importmap:

```ruby
# Gemfile
gem "chartkick", "~> 5.0"
```

```bash
# config/importmap.rb — run once
bin/importmap pin chartkick chart.js
```

```javascript
// app/javascript/application.js
import "chartkick"
import "chart.js"   // ← NOT "Chart.bundle" — use the exact pin name from importmap
```

```erb
<!-- In views -->
<%= line_chart @revenue_data, prefix: "$", thousands: "," %>
<%= area_chart @client_growth %>
<%= pie_chart @service_popularity %>
```

**⚠️ Import name must match `config/importmap.rb` pin name.** The gem's npm package is `chartkick` and the importmap pin is `chart.js` (lowercase). Using `import "Chart.bundle"` silently fails — no chart renders, no JS error. Always verify the pin name matches: `grep "chart" config/importmap.rb`.

**Note:** Chartkick renders charts using Chart.js which requires JavaScript execution. Headless Chrome screenshots may show "Loading..." placeholders — this is normal. The charts render correctly in a real browser. To verify charts are present in HTML, check for `LineChart` or `AreaChart` in the page source.

### Devise `after_sign_up_path_for` Stub — Must Override or Users Redirect to Root

The generated `Users::RegistrationsController` comes with `after_sign_up_path_for` commented out and calling `super`. After a user signs up, they get dumped at `root`. **Always uncomment and override** to redirect to the intended page:

```ruby
# app/controllers/users/registrations_controller.rb
class Users::RegistrationsController < Devise::RegistrationsController
  # Redirect to staff dashboard after account creation
  def after_sign_up_path_for(resource)
    staff_index_path
  end

  # Also override for unconfirmed/inactive accounts if needed
  # def after_inactive_sign_up_path_for(resource)
  #   staff_index_path
  # end
end
```

**Debugging symptom:** A new user signs up and the page reloads to root (`/`), or the URL shows `users` instead of `staff`. The controller action completes (no 500) — it just goes to the wrong place.

### Invoice PDF Generation with Prawn
For invoice/PDF generation, use the Prawn gem (pure Ruby, no dependencies):

```ruby
# Gemfile
gem "prawn", "~> 2.4"
```

```ruby
# app/services/invoice_pdf_generator.rb
class InvoicePdfGenerator
  def initialize(invoice)
    @invoice = invoice
  end

  def generate
    Prawn::Document.new(page_size: "A4") do |pdf|
      pdf.text "Invoice ##{@invoice.number}", size: 18, style: :bold
      # ... layout logic
    end.render
  end
end
```

### Transactional Email with Postmark
For sending emails to customers (booking confirmations, cancellations):

```ruby
# Gemfile
gem "postmark-rails", "~> 0.22"
gem "letter_opener", group: :development  # preview emails in browser
```

```ruby
# config/environments/development.rb
config.action_mailer.delivery_method = :letter_opener
config.action_mailer.perform_deliveries = true

# config/environments/production.rb
config.action_mailer.delivery_method = :postmark
config.action_mailer.postmark_settings = { api_token: ENV["POSTMARK_API_KEY"] }
```

```ruby
# app/mailers/booking_mailer.rb
class BookingMailer < ApplicationMailer
  def confirmation(booking)
    @booking = booking
    mail(to: booking.client.email, subject: "Booking Confirmed")
  end
end
```

### Debugging 500 Errors
When the server returns 500:
1. `tail -50 log/development.log` — get the actual exception
2. **Check `references/groupdate-rails8-incompatibility.md` and this section's list BEFORE guessing** — most "gem works in isolation but 500 at runtime" issues are documented
3. Common causes seen in production:
   - `NameError: uninitialized constant Ahoy::Store` → run `bin/rails generate ahoy:install && bin/rails db:migrate`
   - `syntax_error` in controller → read the file, fix stale `end` or leftover comments from bad patches
   - `undefined method 'stringify_keys' for String` in view → `button_to ... do` with `data:` hash — use `form_with` instead
   - Asset not found → check `app/assets/builds/tailwind.css` exists and layout uses `stylesheet_link_tag "tailwind"` not `"application.tailwind"`
   - **Custom Tailwind classes missing from compiled CSS** → Tailwind v4 scanner drops arbitrary-value classes (`text-[11px]`, `active:scale-[0.98]`, etc.) from ERB files. See Section 11 for the complete replacement table and fix pattern. Rebuild with `bundle exec bin/rails tailwindcss:build` and verify with `grep "page-title\|section-heading\|accent-hover" app/assets/builds/tailwind.css`
   - `undefined method 'group_by_day' for ActiveRecord::Relation` or `group_by_period for nil` → groupdate + Rails 8.1 incompatibility, see groupdate section above
   - **"Gem works in isolation but 500 at runtime"** → check for framework internal API changes (e.g., `@klass` nil on Relation). Call the gem's methods on the model CLASS, not a chained Relation. See `references/groupdate-rails8-incompatibility.md`
3. Fix the root cause in source
4. Kill + restart server: `lsof -ti:3000 | xargs kill -9; bundle exec rails server -b 0.0.0.0 -p 3000` (or `kill $(cat tmp/pids/server.pid)`)
5. Verify via HTTP (auth-gated pages need cookie — see groupdate reference for auth pattern):
   ```bash
   # Get CSRF token
   TOKEN=$(curl -s http://localhost:3000/users/sign_in | grep -oP 'authenticity_token" value="\K[^"]+')
   # Login and capture session cookie
   curl -s -c /tmp/cookies.txt -b http://localhost:3000/users/sign_in -X POST \
     -d "user[email]=owner@glowhair.com&user[password]=password123&authenticity_token=$TOKEN" -o /dev/null
   # Test protected page (use ONLY the _crm_hub_session cookie to avoid cookie collision)
   SESSION_COOKIE=$(grep _crm_hub_session /tmp/cookies.txt | awk '{print $NF}')
   curl -s -b "_crm_hub_session=$SESSION_COOKIE" http://localhost:3000/analytics -o /dev/null -w "%{http_code}"
   # => should print 200
   ```
6. Capture screenshot of the working page:
   ```bash
   google-chrome --headless --no-sandbox --window-size=1280,900 --screenshot=/tmp/crmhub_analytics.png http://localhost:3000/analytics
   ```

### Tailwind CSS Asset Path
The `tailwindcss-rails` gem outputs `tailwind.css` (not `application.tailwind.css`) when input is at `app/assets/tailwind/application.css`. Layout must use:
```erb
<%= stylesheet_link_tag "tailwind", "data-turbo-track": "reload" %>
```

**⚠️ After any change to `application.css`:**
1. Run `bundle exec bin/rails tailwindcss:build`
2. Kill and restart Rails server (`kill $(cat tmp/pids/server.pid); bundle exec rails server`) — the asset hash changes and old in-memory CSS will be stale
3. Verify new hash in HTML source: `curl -s http://localhost:3000/ | grep -o '/assets/tailwind-[a-f0-9]*\.css'`
4. Verify custom classes present: `curl -s "http://localhost:3000${HASHED_URL}" | grep -o "page-title\|section-heading\|accent-hover" | sort | uniq -c`

**⚠️ Tailwind v4 scanner caveat:** The scanner drops arbitrary-value classes (`text-[11px]`, etc.) from ERB. Always replace them with standard equivalents. See Section 11.

### Running Rails Server in Background
Use `terminal(background=true)` then `process(action="poll")` to check output. Don't use shell `&` in foreground mode — it errors. Rails logs go to `log/development.log`, NOT the terminal background output.

### Subagent Delegation Limits for Page Conversion
**Hard limit: 3 pages per subagent batch.** Subagents reliably time out at 600s when given 8-12 pages. Parallel batches of 3 are faster than one giant batch because they don't time out.

**Anti-patterns that failed this session:**
- 11 pages → timed out (600s)
- 8 pages → timed out (600s)  
- 5 pages → timed out (600s)
- 3 pages + browser verification → timed out (600s)
- 3 pages, file-only tools → **completed in 50-250s** ✅

**Expected Stitch view file paths:**
- `/home/deeone/projects/.stitch/designs/` — auth pages, core pages
- `/home/deeone/projects/.stitch/final/` — dashboards, analytics, staff, portal

See the `references/` directory for detailed pattern documentation:

- `references/turbo-patterns.md` — Turbo Frame and Turbo Stream patterns for every CRM page type (list, detail, form, dashboard, real-time)
- `references/stimulus-controllers.md` — Full Stimulus controller templates for all 10 CRMHub controllers (appearance, magnetic, password-toggle, count-up, modal, tabs, calendar, chart, search, filter)
- `references/tailwind-design-system.md` — Complete Tailwind v4 design tokens, color map, spacing, component patterns, and Stitch-to-ERB conversion reference
- `references/rails-8-boot-debugging.md` — Debugging 500 errors, common root causes, server startup patterns, acts_as_tenant seed pitfalls
- `references/verified-output-checklist.md` — Pre-deliverable checklist: section count, image count, URL integrity, class mapping, HTTP status, screenshot verification
- `references/stitch-image-audit.md` — Image fidelity verification: audit script, common failure modes, correct Stitch → ERB image conversion
- `references/google-oauth-desktop.md` — Google OAuth setup for shared desktop apps: Console UI steps, gems, callback controller, multi-user considerations
- `references/groupdate-rails8-incompatibility.md` — groupdate 5.x + Rails 8.1 crash: root cause (`@klass=nil`), reproduction steps, fix pattern, list of failing/working call patterns

## Templates

See the `templates/` directory for reusable code:

- [`templates/turbo_stream_responses.rb`](templates/turbo_stream_responses.rb) — Controller action patterns for create/update/destroy with Turbo Stream responses
- [`templates/stimulus_controller_template.js`](templates/stimulus_controller_template.js) — Base Stimulus controller template with all conventions

## Scripts

Use these directly — they are deterministic, self-contained actions:

- [`references/verify_tailwind_tokens.py`](references/verify_tailwind_tokens.py) — Verify all custom Tailwind tokens are in compiled CSS output. Detects missing tokens and arbitrary-value violations in ERB. Run without args to check, `--fix` to apply replacements:
  ```bash
  cd /home/deeone/projects/crm_hub
  python3 ~/.hermes/skills/frontend/crmhub-hotwire/references/verify_tailwind_tokens.py
  # Fix: python3 ~/.hermes/skills/frontend/crmhub-hotwire/references/verify_tailwind_tokens.py --fix
  ```

---

## Verification Checklist

Before considering a Hotwire feature complete, verify all of the following:

- [ ] **Turbo Drive:** No custom `fetch()` calls for navigation. All links/forms use default Turbo Drive behavior.
- [ ] **Turbo Frames:** Every independently-updating page region is wrapped in `turbo_frame_tag` with a unique `id`.
- [ ] **Frame targeting:** Links that should update a specific frame use `data-turbo-frame="frame_id"`.
- [ ] **Bookmarkable frames:** Frame navigation that should update the URL uses `data-turbo-action="advance"`.
- [ ] **Turbo Streams (forms):** Create/update/destroy actions respond with `format.turbo_stream` — no redirect on Turbo requests.
- [ ] **Stream actions:** The correct action is used (prepend for new items, replace for edits, remove for deletes, update for counters).
- [ ] **Real-time broadcasts:** Model callbacks use `broadcast_prepend_to` / `broadcast_replace_to` / `broadcast_remove_to`. Pages use `turbo_stream_from` to subscribe.
- [ ] **Destructive actions:** Use `button_to` with `data: { turbo_method: :delete, turbo_confirm: "..." }` — never `link_to ... method: :delete`.
- [ ] **Stimulus controllers:** Registered with `data-controller`, targets declared in `static targets`, values declared in `static values`, actions via `data-action="event->controller#method"`.
- [ ] **Controller cleanup:** `disconnect()` clears intervals, removes event listeners, and nullifies references.
- [ ] **Permanent elements:** Stateful widgets (toast container, media player) use `data-turbo-permanent` with stable `id`.
- [ ] **Design system:** All HTML uses Teal `#0D9488` (`teal-600`), Geist font, Zinc neutrals, `rounded-xl` (12px radius), `min-h-[100dvh]` on body.
- [ ] **System tests:** Frame swaps, stream responses, cross-tab broadcasts, and controller connect/disconnect are covered by system specs.
- [ ] **No JS framework:** No React, Vue, Alpine, or Livewire. All interactivity is Turbo + Stimulus only.

---

## Rails 8 + acts_as_tenant Seed Pattern

When using `acts_as_tenant`, seeds need either:
1. `Current.account = account` set early in seed file, AND
2. Every tenant-scoped record must have `account: account` passed explicitly (Current.account is not always available in seed context)

```ruby
# db/seeds.rb — correct pattern
account = Account.create!(name: "Test Salon", timezone: "UTC", currency: "USD")
Current.account = account  # set early

# Still pass account explicitly — Current.account may not propagate in seed context
User.create!(name: "Admin", email: "admin@test.com", password: "password123", account: account)
Client.create!(first_name: "John", last_name: "Doe", account: account, user: user)
```

**Pitfall:** Running `rails g devise User` twice creates a duplicate migration that fails with `duplicate column name: email`. Always check `db/migrate/` before re-running generators.
