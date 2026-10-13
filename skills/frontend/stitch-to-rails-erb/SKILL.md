---
name: stitch-to-rails-erb
description: "Convert Stitch-generated HTML into production-ready Rails 8 ERB views. Handles form helpers (form_with, FormBuilder), Devise auth, Tailwind CSS v4 design tokens, partials, Turbo Frames/Stimulus, ActionView helpers, SPA navigation, Solid Cable real-time updates, Docker Compose local deployment, and project auditing. v4 — includes Docker debugging cookbook and Rails 8 boot failure patterns."
allowed-tools:
  - Read
  - Write
  - Terminal
  - Patch
---

# Stitch HTML to Rails ERB Conversion Skill (v2)

Converts Google Stitch HTML output into proper Rails 8 ERB views. Stitch generates standalone HTML with inline Tailwind config, Material Symbols icons, and custom color tokens. This skill rewrites each component into idiomatic Rails 8 ERB with `form_with` + FormBuilder, Rails routing, Tailwind CSS v4, Turbo/Stimulus, and the project design system.

## Architecture: What Stitch Outputs vs What Rails Needs

**Stitch generates:** `<!DOCTYPE html>` document with `<head>` (Tailwind CDN, Material Symbols font, custom `tailwind.config` script, custom `<style>`), `<body>` with full page markup.

**Rails ERB expects:** A view template that yields into `app/views/layouts/application.html.erb`. The layout already has `<html>`, `<head>`, `<body>`, Tailwind CSS, Geist font, and Stimulus. The view only provides the inner content.

**Conversion = Strip wrapper + Convert ERB logic + Map tokens**

## Pre-Conversion Checklist

Before touching any HTML file, confirm:
1. **Project design system tokens** are defined in `app/assets/tailwind/application.css` (Tailwind v4 `@theme` block)
2. **Tailwind CSS v4** is configured and builds successfully (`bin/rails tailwindcss:build`)
3. **Application layout** (`app/views/layouts/application.html.erb`) includes Geist font + Tailwind + `<%= yield :head %>`
4. **Stimulus controllers** exist for: appearance (scroll-reveal), magnetic (hover), count-up, password-toggle
5. **Routes** are defined in `config/routes.rb` for all target resources
6. **Devise** is installed if converting auth views

---

## Rule 1: Strip the Wrapper

REMOVE entirely:
- `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>` tags
- `<script src="https://cdn.tailwindcss.com...">` (Rails handles Tailwind)
- `<link>` tags for fonts (Geist, Material Symbols — layout handles these)
- `<style>` blocks (our design system handles styles)
- `<script>` blocks with `tailwind.config = {...}` (our `@theme` handles tokens)
- `<script>` blocks with inline JS (replace with Stimulus controllers)

KEEP: Only the inner content that was between `<body>` tags.

---

## Rule 2: Form Conversion (CRITICAL)

### Rails 8 Form Helper API

Rails 8 uses `form_with` as the **sole** form helper (form_for and form_tag are legacy). It yields a `FormBuilder` object (`f`) that generates inputs bound to models or scopes.

**Signature:** `form_with(model: nil, scope: nil, url: nil, local: true, **options, &block)`

### Form Patterns by Use Case

#### Pattern A: Devise Authentication Forms

```erb
<%# SIGN IN %>
<%= form_with model: resource, as: resource_name, url: session_path(resource_name), local: true, class: "space-y-5" do |f| %>
  <%= render "devise/shared/error_messages", resource: resource %>
  <div class="space-y-2">
    <%= f.label :email, class: "block text-sm font-medium text-ink" %>
    <%= f.email_field :email, autofocus: true, autocomplete: "email",
        class: "w-full px-4 py-3 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-spring text-sm min-h-[48px]",
        placeholder: "you@example.com" %>
  </div>
  <div class="space-y-2">
    <%= f.label :password, class: "block text-sm font-medium text-ink" %>
    <div class="relative" data-controller="password-toggle">
      <%= f.password_field :password, autocomplete: "current-password",
          data: { password_toggle_target: "input" },
          class: "w-full px-4 py-3 pr-12 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-spring text-sm min-h-[48px]",
          placeholder: "Enter your password" %>
      <button type="button" data-action="password-toggle#toggle" class="absolute right-3 top-1/2 -translate-y-1/2 text-steel hover:text-primary transition-spring p-1">
        <svg data-password-toggle-target="icon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
        </svg>
      </button>
    </div>
  </div>
  <%= f.submit "Sign In", class: "w-full py-3.5 bg-primary text-white rounded-xl font-semibold hover:bg-primary-hover transition-spring btn-push shadow-lg shadow-primary/20", data: { controller: "magnetic" } %>
<% end %>
```

```erb
<%# SIGN UP (Registration) %>
<%= form_with model: resource, as: resource_name, url: registration_path(resource_name), local: true, class: "space-y-5" do |f| %>
  <%= render "devise/shared/error_messages", resource: resource %>
  <%= f.text_field :name, autofocus: true %>
  <%= f.email_field :email, autocomplete: "email" %>
  <%= f.password_field :password, autocomplete: "new-password" %>
  <%= f.password_field :password_confirmation, autocomplete: "new-password" %>
  <%= f.submit "Create Account" %>
<% end %>
```

```erb
<%# FORGOT PASSWORD %>
<%= form_with model: resource, as: resource_name, url: password_path(resource_name), method: :post, local: true do |f| %>
  <%= f.email_field :email, autofocus: true %>
  <%= f.submit "Send Reset Link" %>
<% end %>
```

```erb
<%# RESET PASSWORD (from email token) %>
<%= form_with model: resource, as: resource_name, url: password_path(resource_name), method: :patch, local: true do |f| %>
  <%= f.hidden_field :reset_password_token %>
  <%= f.password_field :password, autocomplete: "new-password" %>
  <%= f.password_field :password_confirmation, autocomplete: "new-password" %>
  <%= f.submit "Update Password" %>
<% end %>
```

```erb
<%# EDIT PROFILE / SETTINGS %>
<%= form_with model: resource, as: resource_name, url: registration_path(resource_name), method: :patch, local: true do |f| %>
  <%= f.text_field :name %>
  <%= f.email_field :email %>
  <%= f.password_field :current_password, autocomplete: "current-password" %>
  <%= f.password_field :password, autocomplete: "new-password" %>
  <%= f.submit "Update" %>
<% end %>
```

#### Pattern B: Model CRUD Forms (New/Edit)

```erb
<%# NEW record — form_with infers POST from model.new_record? %>
<%= form_with model: @client, local: true, class: "space-y-6" do |f| %>
  <div class="space-y-2">
    <%= f.label :name, class: "block text-sm font-medium text-ink" %>
    <%= f.text_field :name, class: "w-full px-4 py-3 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm min-h-[48px]" %>
  </div>
  <div class="space-y-2">
    <%= f.label :email, class: "block text-sm font-medium text-ink" %>
    <%= f.email_field :email, class: "w-full px-4 py-3 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm min-h-[48px]" %>
  </div>
  <div class="space-y-2">
    <%= f.label :phone, class: "block text-sm font-medium text-ink" %>
    <%= f.telephone_field :phone, class: "w-full px-4 py-3 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm min-h-[48px]" %>
  </div>
  <div class="space-y-2">
    <%= f.label :notes, class: "block text-sm font-medium text-ink" %>
    <%= f.text_area :notes, rows: 4, class: "w-full px-4 py-3 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm" %>
  </div>
  <%= f.submit class: "w-full py-3.5 bg-primary text-white rounded-xl font-semibold hover:bg-primary-hover transition-spring btn-push shadow-lg shadow-primary/20", data: { controller: "magnetic" } %>
<% end %>
```

```erb
<%# EDIT record — form_with infers PATCH from model.persisted? %>
<%= form_with model: @client, local: true, class: "space-y-6" do |f| %>
  <%# Same fields as new — values auto-filled from @client %>
<% end %>
```

#### Pattern C: Search/Filter Forms (Non-Model, GET)

```erb
<%# Search bar — use form_with with url + method: :get %>
<%= form_with url: clients_path, method: :get, local: true, class: "relative flex-1 max-w-md" do |f| %>
  <svg class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-steel" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
  </svg>
  <%= f.search_field :q, value: params[:q], placeholder: "Search clients...", class: "w-full pl-10 pr-4 py-2 bg-white border border-border rounded-lg text-sm text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-spring" %>
<% end %>

<%# Filter dropdown — use select_tag for non-model selects %>
<%= form_with url: clients_path, method: :get, local: true do |f| %>
  <%= f.select :status, [["All", ""], ["Active", "active"], ["Inactive", "inactive"]], { selected: params[:status] }, class: "..." %>
  <%= f.submit "Filter", class: "..." %>
<% end %>
```

#### Pattern D: Standalone Buttons (Logout, Delete, Actions)

```erb
<%# Logout — use form_with to avoid stringify_keys crash with button_to do blocks %>
<%# WARNING: button_to ... do | ... end with data: { turbo_method: :delete } causes %>
<%# ActionView::Template::Error: undefined method 'stringify_keys' for String %>
<%# Use form_with + button type="submit" instead. %>
<%= form_with url: destroy_user_session_path, method: :delete do |f| %>
  <button type="submit" class="flex items-center gap-2 text-steel hover:text-primary transition-colors">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
    </svg>
    Sign Out
  </button>
<% end %>

<%# Delete record with confirmation — button_to WITHOUT block is safe %>
<%= button_to "Delete", client_path(@client), method: :delete,
    class: "text-error hover:text-error/80",
    data: { turbo_confirm: "Delete this client?" } %>
```

**⚠️ CRITICAL: Never use `button_to ... do | ... end` with `data: { turbo_method: :delete }`.**
The block form of `button_to` combined with a `data:` hash triggers a `stringify_keys` crash in Rails 8 because the first positional argument (the label string) is misinterpreted as an options hash. Use `form_with url: ..., method: :delete` + `<button type="submit">` instead.

### Form Helper Quick Reference

| Stitch HTML | Rails ERB | Notes |
|---|---|---|
| `<form onsubmit="return false;">` | `<%= form_with model: @x do \|f\| %>` | Auto CSRF token |
| `<form action="/search">` | `<%= form_with url: search_path, method: :get do \|f\| %>` | GET for search |
| `<input type="email">` | `<%= f.email_field :email %>` | Auto name + id |
| `<input type="password">` | `<%= f.password_field :password %>` | Masked input |
| `<input type="text">` | `<%= f.text_field :name %>` | Single line |
| `<input type="checkbox">` | `<%= f.check_box :active %>` | + hidden field |
| `<input type="radio">` | `<%= f.radio_button :status, "active" %>` | Group by name |
| `<input type="file">` | `<%= f.file_field :avatar %>` | Auto multipart |
| `<input type="number">` | `<%= f.number_field :quantity %>` | Numeric |
| `<input type="tel">` | `<%= f.telephone_field :phone %>` | Telephone |
| `<input type="url">` | `<%= f.url_field :website %>` | URL validation |
| `<input type="search">` | `<%= f.search_field :q %>` | Search |
| `<input type="hidden">` | `<%= f.hidden_field :token %>` | Hidden |
| `<textarea>` | `<%= f.text_area :notes, rows: 4 %>` | Multi-line |
| `<select>` | `<%= f.select :status, ["Active","Inactive"] %>` | Simple select |
| `<select>` (from DB) | `<%= f.collection_select :city_id, City.all, :id, :name %>` | From collection |
| `<button type="submit">` | `<%= f.submit "Save" %>` | Auto label |
| `<label>` | `<%= f.label :name, "Name" %>` | Auto for attribute |
| `</form>` | `<% end %>` | Block close |

### Advanced Form Helpers (Rails 8)

```erb
<%# Collection select — dropdown from database records %>
<%= f.collection_select :service_id, Service.order(:name), :id, :name,
    { prompt: "Select a service" },
    class: "w-full px-4 py-3 rounded-xl border border-border" %>

<%# Collection checkboxes — for has_many :through %>
<%= f.collection_checkboxes :tag_ids, Tag.order(:name), :id, :name do |b| %>
  <div class="flex items-center gap-2">
    <%= b.check_box class="rounded border-border text-primary" %>
    <%= b.label class="text-sm text-ink" %>
  </div>
<% end %>

<%# Collection radio buttons %>
<%= f.collection_radio_buttons :plan_id, Plan.all, :id, :name do |b| %>
  <div class="flex items-center gap-2">
    <%= b.radio_button class="text-primary" %>
    <%= b.label class="text-sm text-ink" %>
  </div>
<% end %>

<%# Time zone select %>
<%= f.time_zone_select :time_zone, nil, { include_blank: "Select timezone" }, class: "..." %>

<%# Grouped collection select (optgroup) %>
<%= f.grouped_collection_select :city_id, Country.order(:name), :cities, :name, :id, :name, {}, class: "..." %>

<%# Date/time fields %>
<%= f.date_field :starts_on %>
<%= f.time_field :starts_at %>
<%= f.datetime_local_field :scheduled_at %>

<%# Range slider %>
<%= f.range_field :priority, in: 1..10 %>

<%# Color picker %>
<%= f.color_field :brand_color %>

<%# File upload with Active Storage direct upload %>
<%= f.file_field :attachments, multiple: true, direct_upload: true, class: "..." %>

<%# ActionText rich text editor (Trix) %>
<%= f.rich_text_area :body, class: "trix-content" %>

<%# Nested fields (for accepts_nested_attributes_for) %>
<%= f.fields_for :addresses do |address_form| %>
  <%= address_form.text_field :street %>
  <%= address_form.text_field :city %>
<% end %>

<%# Fields without form tags (for nested scopes outside main form) %>
<%= fields :comment do |comment_fields| %>
  <%= comment_fields.text_field :body %>
<% end %>
```

### Devise Path Helpers Reference

| Action | Path Helper | Method |
|---|---|---|
| Sign in | `session_path(resource_name)` | POST |
| Sign up | `registration_path(resource_name)` | POST |
| Edit profile | `registration_path(resource_name)` | PATCH |
| Cancel account | `registration_path(resource_name)` | DELETE |
| Forgot password | `password_path(resource_name)` | POST |
| Reset password | `password_path(resource_name)` | PATCH |
| Confirm email | `confirmation_path(resource_name)` | POST |
| Google OAuth | `user_google_oauth2_omniauth_authorize_path` | POST |
| Apple OAuth | `user_apple_omniauth_authorize_path` | POST |

### Social Auth Pattern (MUST be OUTSIDE form_with)

```erb
<%# INSIDE the view, OUTSIDE the form_with block %>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-6">
  <%= button_to user_google_oauth2_omniauth_authorize_path,
      class: "w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-border bg-white hover:bg-canvas transition-spring btn-push text-sm font-medium text-ink",
      data: { turbo: false } do %>
    <svg class="w-5 h-5" viewBox="0 0 24 24"><!-- Google SVG --></svg>
    <span>Google</span>
  <% end %>

  <%= button_to user_apple_omniauth_authorize_path,
      class: "w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-border bg-white hover:bg-canvas transition-spring btn-push text-sm font-medium text-ink",
      data: { turbo: false } do %>
    <svg class="w-5 h-5 fill-current" viewBox="0 0 24 24"><!-- Apple SVG --></svg>
    <span>Apple</span>
  <% end %>
</div>
```

---

## Rule 3: Color Token Mapping

Stitch uses Material Design 3 tokens. Map to our Tailwind v4 design system:

| Stitch Token | Our Token | Usage |
|---|---|---|
| `primary` (#00685f) | `primary` (#0D9488) | CTAs, active states, focus rings |
| `accent-hover` | `primary-hover` (#0F766E) | Hover on primary buttons |
| `accent-subtle` / `CCFBF1` | `primary-subtle` | Light teal backgrounds |
| `pure-surface` / `FFFFFF` | `white` | Card backgrounds |
| `canvas` / `F8FAFB` | `canvas` | Page background |
| `on-surface` / `171d1c` | `ink` (#18181B) | Primary text |
| `on-secondary-container` / `656467` | `steel` (#71717A) | Secondary text |
| `whisper-border` / `rgba(229,231,235,0.6)` | `border` (rgba(226,232,240,0.5)) | Borders |
| `surface-container` / `eaefed` | `canvas` | Subtle backgrounds |
| `surface-container-highest` | `zinc-100` | Subtle backgrounds (lighter than canvas) |
| `surface-container-high` | `zinc-100` | Subtle backgrounds |
| `surface-container-low` | `primary-subtle/30` | Very subtle backgrounds |
| `surface-variant` | `zinc-200` | Dividers, disabled states |
| `success` / `059669` | `success` | Positive states |
| `warning` / `D97706` | `warning` | Caution states |
| `error` / `DC2626` | `error` | Error states |
| `outline-variant` | `border` | Dividers |
| `tertiary` / `555c6a` | `steel` | Map undefined tertiary to steel |
| `background` / `f5faf8` | `canvas` | Page background |
| `surface-dim` | `zinc-100` | Dimmed surfaces |
| `surface-bright` | `white` | Bright surfaces |
| `inverse-surface` | `ink` | Inverted text |
| `inverse-primary` | `primary` | Inverted accent |
| `info` / `0284C7` | `info` | Informational |

**Replace ALL Stitch color classes.** The class name may be the same (e.g., `bg-primary`) but the hex value differs — our `@theme` block controls the actual color.

---

## Rule 4: Icon Migration

Stitch uses Material Symbols Outlined font icons. Convert ALL to inline SVG (Heroicons outline style):

```html
<!-- Stitch -->
<span class="material-symbols-outlined">visibility</span>

<!-- Rails ERB -->
<svg class="w-5 h-5 text-steel" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
</svg>
```

**Standard SVG wrapper pattern:**
```html
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="..."/>
</svg>
```

See `references/icon-mappings.md` for 100+ icon path mappings.

---

## Rule 5: Spacing & Sizing Token Mapping

| Stitch | Tailwind Standard |
|---|---|
| `p-xs` / `gap-xs` | `p-1` / `gap-1` |
| `p-sm` / `gap-sm` | `p-2` / `gap-2` |
| `p-md` / `gap-md` | `p-3` / `gap-3` |
| `p-lg` / `gap-lg` | `p-4` / `gap-4` |
| `p-xl` / `gap-xl` | `p-6` / `gap-6` |
| `p-xxl` / `gap-xxl` | `p-8` / `gap-8` |
| `mb-xs` | `mb-1` |
| `mb-sm` | `mb-2` |
| `mb-md` | `mb-3` |
| `mb-lg` | `mb-4` |
| `mb-xl` | `mb-6` |
| `mb-xxl` | `mb-8` |
| `h-11` (44px) | `min-h-[48px]` (touch target) |
| `max-w-max-content` | `max-w-7xl` |
| `max-w-[1000px]` | `max-w-4xl` or `max-w-5xl` |
| `w-sidebar-width` | `w-60` |
| `ml-sidebar-width` | `ml-60` |

---

## Rule 6: Typography Token Mapping

| Stitch | Our System |
|---|---|
| `font-page-title text-page-title` | `text-xl font-bold tracking-tight` (or `text-2xl`) |
| `font-section-heading text-section-heading` | `text-lg font-semibold` |
| `font-card-title text-card-title` | `text-sm font-semibold` |
| `font-label-caps text-label-caps` | `text-xs uppercase tracking-wider font-semibold` |
| `font-body-relaxed text-body-relaxed` | `text-sm text-steel` |
| `font-meta-mono text-meta-mono` | `text-xs font-mono text-steel` |

---

## Rule 7: Link Conversion

```erb
<%# Stitch: <a href="#">Clients</a> %>
<%= link_to "Clients", clients_path, class: "text-steel hover:text-primary" %>

<%# Stitch: <a href="dashboard">Dashboard</a> %>
<%= link_to "Dashboard", dashboard_path, class: "..." %>
```

**Full path helper reference:**
| Stitch href | Rails Helper |
|---|---|
| `#clients` | `clients_path` |
| `#client/123` | `client_path(@client)` |
| `#clients/new` | `new_client_path` |
| `#clients/123/edit` | `edit_client_path(@client)` |
| `#bookings` | `bookings_path` |
| `#campaigns` | `campaigns_path` |
| `#dashboard` | `dashboard_path` |
| `#settings` | `settings_path` |
| `#loyalty` | `loyalty_path` |
| `#sign-in` | `new_user_session_path` |
| `#sign-up` | `new_user_registration_path` |
| `#forgot-password` | `new_password_path(resource_name)` |
| `#admin/security` | `admin_security_path` |
| `#user/security` | `user_security_path` |

**Conditional links (Rails 8):**
```erb
<%= link_to_if current_user.admin?, "Admin Panel", admin_root_path do %>
  <span class="text-steel">Standard User Mode</span>
<% end %>

<%= link_to_unless @client.archived?, "Edit", edit_client_path(@client) %>
```

**Turbo-powered links (Rails 8 default):**
```erb
<%# DELETE via link (uses Turbo) %>
<%= link_to "Remove", client_path(@client),
    data: { turbo_method: :delete, turbo_confirm: "Are you sure?" },
    class: "text-error" %>
```

---

## Rule 8: Animation Conversion

Stitch uses custom `<style>` + `<script>` for animations. Convert to our Stimulus-backed system:

```erb
<%# Stitch: <div class="stagger-reveal" style="animation-delay: 200ms;"> %>
<div class="reveal-hidden" data-reveal-delay="200">
```

**Entry animations:**
```erb
<h1 class="animate-fade-up">Welcome back</h1>
<p class="animate-fade-up delay-150">Subtitle text</p>
```

**Interactive:**
- Stitch `active-press:active` → our `btn-push:active`
- Stitch JS hover → `data-controller="magnetic"` on CTAs
- Stitch scroll tracking → `data-controller="appearance"` on body + `reveal-hidden` on elements

**For standalone pages (landing pages) that may not load Tailwind CSS with animation utilities, add inline fallback:**
```erb
<% content_for :head do %>
<style>
.animate-fade-up { animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.btn-push:active { transform: scale(0.98) translateY(1px); transition: transform 0.1s; }
.transition-spring { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.glass { background: rgba(255,255,255,0.8); backdrop-filter: blur(20px); }
.glass-strong { background: rgba(255,255,255,0.95); backdrop-filter: blur(24px); }
.mesh-gradient { background-image: radial-gradient(at 40% 20%, #CCFBF1 0px, transparent 50%), radial-gradient(at 80% 0%, #F8FAFB 0px, transparent 50%); }
</style>
<% end %>
```

---

## Rule 9: Image Handling

```erb
<%# Stitch: <img src="https://lh3.googleusercontent.com/aida/AP1WRL..." alt="..."> %>
<img src="https://picsum.photos/seed/crm-dashboard-preview/600/400" alt="Dashboard preview" class="w-full h-auto object-cover">

<%# User avatars — use initials div as fallback %>
<div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold text-xs">
  <%= user.initials || "AU" %>
</div>

<%# Active Storage image (when model has attached image) %>
<% if @client.avatar.attached? %>
  <%= image_tag @client.avatar, class: "w-10 h-10 rounded-full object-cover" %>
<% else %>
  <div class="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold text-xs">
    <%= @client.initials %>
  </div>
<% end %>
```

---

## Rule 10: Devise Error Messages

```erb
<%# Modern pattern (preferred) %>
<% if resource.errors.any? %>
  <div class="bg-error/5 border border-error/20 rounded-xl p-4 mb-6">
    <h2 class="text-sm font-semibold text-error mb-2">
      <%= pluralize(resource.errors.count, "error") %> prohibited this action:
    </h2>
    <ul class="text-sm text-error/80 space-y-1">
      <% resource.errors.full_messages.each do |msg| %>
        <li><%= msg %></li>
      <% end %>
    </ul>
  </div>
<% end %>

<%# Or use Devise's built-in helper %>
<%= devise_error_messages! %>
```

---

## Rule 11: Conditional Data with Nil Guards

```erb
<%# Static text → instance variable with fallback %>
<%= client.name || "Unnamed Client" %>
<%= number_to_currency(@revenue, precision: 0) || "$0" %>
<%= time_ago_in_words(@last_activity) || "Never" %> ago
<%= pluralize(@clients.count, "Client") %>

<%# Dates %>
<%= booking.starts_at&.strftime("%b %d, %Y at %I:%M %p") || "No date" %>

<%# Numbers %>
<%= number_to_percentage(@growth_rate, precision: 1) || "0%" %>
<%= number_to_human(@total_sent) || "0" %>

<%# Collections with empty state %>
<% if @clients.any? %>
  <% @clients.each do |client| %>
    <%= render client %> <%# shorthand for render partial: "client", client: client %>
  <% end %>
<% else %>
  <div class="text-center py-24">
    <p class="text-steel">No clients yet</p>
    <%= link_to "Add your first client", new_client_path, class: "text-primary font-semibold" %>
  </div>
<% end %>
```

---

## Rule 12: Turbo & Stimulus Integration (Rails 8)

Rails 8 uses Turbo by default. All forms submit via XHR unless `local: true` is set.

```erb
<%# Standard form — submits via Turbo (no full page reload) %>
<%= form_with model: @client do |f| %>
  <%# ... %>
<% end %>

<%# Force full page reload (for non-Turbo flows) %>
<%= form_with model: @client, local: true do |f| %>
  <%# ... %>
<% end %>

<%# Social auth — MUST disable Turbo %>
<%= button_to user_google_oauth2_omniauth_authorize_path,
    data: { turbo: false },
    class: "..." do %>
  Sign in with Google
<% end %>

<%# Delete link with Turbo confirmation %>
<%= link_to "Delete", client_path(@client),
    data: { turbo_method: :delete, turbo_confirm: "Are you sure?" },
    class: "text-error" %>

<%# Stimulus controllers %>
<div data-controller="appearance"> <%# scroll-reveal %>
<div data-controller="magnetic"> <%# hover spring %>
<div data-controller="password-toggle"> <%# password visibility %>
<div data-controller="count-up"> <%# animated numbers %>
```

---

## Rule 13: Partials & Shared Layouts (DRY)

Instead of repeating sidebar/nav in every view, use Rails partials:

```erb
<%# app/views/application/_sidebar.html.erb — shared across all controllers %>
<aside class="w-60 min-h-[100dvh] fixed left-0 top-0 bg-white border-r border-border z-50 flex flex-col p-8">
  <%# ... nav items ... %>
</aside>

<%# In any view, render the shared sidebar %>
<%= render "application/sidebar" %>

<%# Or use content_for for page-specific sidebar highlights %>
<% content_for :sidebar_active, "campaigns" %>
```

**Collection rendering (high-performance):**
```erb
<%# Instead of .each loop %>
<tbody class="divide-y">
  <%= render @clients %> <%# Rails finds _client.html.erb automatically %>
</tbody>

<%# _client.html.erb partial — `client` variable is auto-available %>
<tr class="hover:bg-canvas transition-colors">
  <td><%= client.name %></td>
  <td><%= client.email %></td>
</tr>
```

**Layout injection:**
```erb
<%# In the view — inject page-specific CSS/JS into <head> %>
<% content_for :head do %>
  <%= javascript_include_tag "charts", "data-turbo-track": "reload" %>
<% end %>
```

---

## Rule 14: View Helpers for Formatting

Replace Stitch's hardcoded values with Rails formatting helpers:

```erb
<%# Numbers %>
<%= number_to_currency(@revenue, precision: 0) %>        <%# $45,000 %>
<%= number_to_percentage(@rate, precision: 1) %>         <%# 64.2 %>
<%= number_to_human(@total) %>                           <%# 428.5k %>
<%= number_to_human_size(@file_size) %>                  <%# 2.5 MB %>
<%= number_to_phone(@phone) %>                           <%# (555) 123-4567 %>

<%# Time %>
<%= time_ago_in_words(@last_seen) %> ago                 <%# 3 hours ago %>
<%= time_tag(@created_at) %>                             <%# <time datetime="..."> %>
<%= distance_of_time_in_words(@start, @end) %>           <%# 2 days %>

<%# Text %>
<%= pluralize(@clients.count, "client") %>               <%# 42 clients %>
<%= truncate(@description, length: 100) %>               <%# truncated... %>
<%= highlight(@text, params[:q]) %>                      <%# <mark>highlighted</mark> %>
<%= simple_format(@notes) %>                             <%# wraps in <p> tags %>
<%= strip_tags(@html_content) %>                         <%# plain text %>
<%= sanitize(@user_content) %>                           <%# safe HTML only %>

<%# URLs %>
<%= mail_to @email %>                                    <%# <a href="mailto:..."> %>
<%= phone_to @phone %>                                   <%# <a href="tel:..."> %>
<%= auto_link(@text_with_urls) %>                        <%# links URLs in text %>
```

---

## Conversion Process (Step by Step)

1. **Read** the Stitch HTML source file fully
2. **Strip** the HTML wrapper (Rule 1)
3. **Convert forms** using Rule 2 (most critical — use correct Devise path helpers)
4. **Map colors** using Rule 3
5. **Replace icons** using Rule 4
6. **Fix spacing** using Rule 5
7. **Fix typography** using Rule 6
8. **Convert links** using Rule 7
9. **Convert animations** using Rule 8
10. **Replace images** using Rule 9
11. **Add Devise errors** using Rule 10
12. **Add nil guards + formatting** using Rule 11
13. **Add Turbo/Stimulus** using Rule 12
14. **Extract partials** where appropriate (Rule 13)
15. **Add `content_for :title`** at the top
16. **Verify** with the checklist below

---

## Verification Checklist (Post-Conversion)

```bash
# No raw HTML form/input tags
grep -rn '<form' app/views/ | grep -v '<%='
grep -rn '<input' app/views/ | grep -v '<%='

# No Stitch color tokens
grep -rn 'pure-surface\|whisper-border\|on-surface\|surface-container\|accent-subtle\|accent-hover\|on-primary-container\|on-secondary-container' app/views/

# No Material Symbols
grep -rn 'material-symbols-outlined' app/views/

# No h-screen
grep -rn 'h-screen\|min-h-screen' app/views/

# No Stitch typography tokens
grep -rn 'font-page-title\|font-section-heading\|font-card-title\|font-label-caps\|font-body-relaxed\|font-meta-mono' app/views/

# No external Google images — they are INTENTIONAL design elements from Stitch
# DO NOT remove them. If a view has 0 images but the Stitch source has images, that's a bug.
grep -c '<img' /path/to/stitch.html
grep -c '<img' /path/to/rails.html.erb
# These numbers should match (or be very close)

# Every view has content_for :title
grep -rL 'content_for :title' app/views/**/*.erb
```

---

## Lessons Learned (Session 2026-06-27 — Updated 2026-06-27)

### Running in Circles Trap
⚠️ **User explicitly called this out.** The assistant hit the same error 6+ times on `rails db:seed` because it kept retrying the same command without changing the root cause. The seed failure (`Account must exist` for acts_as_tenant) required explicitly passing `account: account` on every seeded record — not just setting `Current.account`.

**Rule:** After 2+ identical failures, DIAGNOSE before retrying. Read the actual exception, identify root cause, fix the code/config, then retry.

**⚠️ "Running in circles after fixing the skill"** — Fixing the skill that should make you more effective means NOTHING if the actual views still fail. After skill fixes, RE-RUN the failing steps immediately. The skill is the means, the working pages are the end.

### Rails 8 + acts_as_tenant Seed Pattern
When using `acts_as_tenant`, seeds need either:
1. `Current.account = account` set early in seed file, AND
2. Every tenant-scoped record must have `account: account` passed explicitly (Current.account is not always available in seed context)

### User Workflow Preferences
- User wants CLI commands run FIRST before any manual file editing
- User wants skills to be loaded and followed — "don't ignore the skills"
- User wants screenshots taken with lightpanda when done
- User prefers subagents for parallel work, NOT sequential explanation
- User dislikes long explanations — "just give me the answer"
- User corrects quickly: "you single handedly ruined it", "you are using mcp stitch"

### Devise + Rails 8 Pitfalls
- Running `rails g devise User` twice creates a duplicate `AddDeviseToUsers` migration — check `db/migrate/` before running again
- The first `rails g devise User` creates the email column; the second tries to add it again → `SQLite3::SQLException: duplicate column name: email`

### SQLite vs User Preference
User explicitly said "postgresql should be replaced with sqlite" — confirming their preference for SQLite for local dev simplicity.

### Subagent Delegation for View Conversion

Subagents CAN be used for view conversion, but with strict limits:
- **Max 3-4 views per subagent** — 8+ views times out at 600s
- When converting role-based dashboards (4-5 pages), dispatch ONE subagent with all requirements explicitly listed in the context
- Include ALL 5 requirements in a single dispatch:
  1. Create all partial files
  2. Update controller with role-specific data loading
  3. Fix routes.rb for full CRUD
  4. Wire ALL buttons to real paths (never `href="#"`)
  5. Extract shared partials (sidebar, etc.)
- **If subagent times out:** DO NOT re-dispatch. Do the remaining work directly in the parent session.
- **Always verify ALL roles after completion** — test each role's login → dashboard HTTP 200

### The Fidelity Failure
Naive section omission **always fails review** because:
1. Landing pages have 6+ sections that must ALL be converted
2. `<img>` tags are intentional design elements — not replaceable with placeholders
3. Asymmetric grids (bento, 12-column) must match the Stitch layout exactly
4. Animation CSS (float, shimmer, pulse-ring, mesh-gradient) must be written to the Tailwind input

**Rule 15 (Section Completeness Fidelity):** Read the ENTIRE HTML. Count sections. Convert 1:1. Preserve all `<img>` tags.

### The Critical Failure Mode
Naive `sed` replacement **always fails** because:
1. ERB form helpers span multiple lines
2. `sed` can't handle block forms (`form_with ... do |f| ... end`)
3. Material Symbols need exact icon → SVG mapping

**NEVER use sed to convert Stitch HTML.**

### Common Pitfalls
- **⚠️ `button_to ... do | ... end` with `data:` hash**: `button_to "Label", path, data: { turbo_method: :delete } do %>` triggers `ActionView::Template::Error: undefined method 'stringify_keys' for String` in Rails 8. The block form + data hash causes Rails to misinterpret the label as an options hash. **Fix:** Use `form_with url: ..., method: :delete` + `<button type="submit">` for block-style buttons, or `button_to` without a block. When the user says "reactive UI" or "real-time updates", the answer is **Hotwire** (Turbo Drive, Turbo Frames, Turbo Streams, Stimulus controllers). Never research Livewire docs for a Rails project. Key docs: `turbo.hotwired.dev` and `stimulus.hotwired.dev`.
- **⚠️ Stitch MCP API key redaction**: When calling Stitch MCP via `execute_code` (Python), the API key gets redacted by the system. Use **bash scripts** (`terminal()`) to call Stitch MCP endpoints instead. The key is in `~/.mcp_servers.json` under `mcpServers.stitch.headers['X-Goog-Api-Key']`.
- **Stitch `get_screen` response structure**: The `get_screen` tool returns screen data directly in `structuredContent` (with `htmlCode`, `screenshot`, `name`, etc.) — NOT nested under `structuredContent.design.screens[0]`. Check the actual response structure before parsing.
- **Leaving `<%= ... %>` tags visible**: Malformed helpers render as text
- **Missing `|f|` block variable**: Every `form_with ... do |f|` needs it
- **Nested forms**: Invalid HTML. Social buttons go OUTSIDE the Devise form
- **Mixed comment styles**: Stitch `<!-- -->` → Rails `<%# %>`
- **Sidebar inconsistency**: Keep identical across all app views — extract to partial
- **`divide-border` with rgba**: Use `divide-y divide-zinc-200` instead
- **`scrollbar-hide`**: Not built-in — add to CSS
- **`text-tertiary`**: Undefined — map to `text-steel`
- **Landing page animations**: Add inline `<style>` fallback for `animate-fade-up`
- **Turbo on social auth**: Always use `data: { turbo: false }` for OAuth buttons
- **`data-confirm` → `data-turbo-confirm`**: Rails 8 uses Turbo, not rails-ujs
- **Inline sidebar duplication**: Repeating 60+ lines of sidebar HTML across views violates DRY. Extract to `app/views/application/_sidebar.html.erb` with `<% content_for :sidebar_active, "page_name" %>` for active state highlighting
- **`h-[100dvh]` vs `min-h-[100dvh]`**: Use `min-h-[100dvh]` to allow content to expand beyond viewport. `h-[100dvh]` clips long content
- **Double sidebar render**: If the layout (`application.html.erb`) renders `<%= render "application/sidebar" %>` when `user_signed_in?`, AND individual views also render it, you get TWO sidebars. Fix: remove sidebar from layout, let each authenticated view render it explicitly. Public pages (landing, auth) should NOT render the sidebar.
- **Delegation batch sizing for view conversion**: When using subagents to convert views in parallel, limit to **3-4 views per subagent**. 8+ views per batch hits the 10-minute timeout. Break large page sets into batches of 3.
- **Auth wall blocks verification**: After converting authenticated pages, all routes return 302 (redirect to sign-in) when accessed without a session. You cannot verify rendered content via `curl` without authenticating first. Solution: use `curl` + cookie jar to authenticate, then verify HTTP 200:
```bash
T*** -s -c /tmp/cookies.txt http://localhost:3000/users/sign_in | grep -oP 'name="authenticity_token" value="\K[^"]+')
curl -s -b /tmp/cookies.txt -c /tmp/cookies.txt -X POST http://localhost:3000/users/sign_in -d "authenticity_token=$TOKEN&user[email]=owner@glowhair.com&user[password]=password123" -L -o /dev/null
curl -s -b /tmp/cookies.txt http://localhost:3000/dashboard -o /dev/null -w "%{http_code}"
```

### gcloud CLI Cannot Create OAuth Client Credentials
When setting up Google OAuth for social auth, `gcloud` CLI cannot create OAuth client credentials. It manages projects, APIs, and service accounts — but OAuth client IDs/secrets MUST be created via the Google Cloud Console web UI:
1. Go to https://console.cloud.google.com/apis/credentials?project=YOUR_PROJECT
2. + CREATE CREDENTIALS → OAuth client ID → Desktop app
3. Add redirect URI: `http://localhost:3000/users/auth/google_oauth2/callback`
4. Copy Client ID + Client Secret into Rails credentials or `~/.openclaw/credentials/google-oauth.json`
5. Use `prompt: 'select_account'` in OmniAuth config to force account picker (critical for shared desktops)

### Debugging Discipline (USER PREFERENCE — CRITICAL)
⚠️ **Do NOT loop on the same error.** The user explicitly called out "you single handedly ruined it" after watching the same 500 error repeat across multiple restarts.

**If the same exception appears more than once:**
1. **STOP** — restarting won't fix code/config issues
2. **Read the full stack trace** — `tail -40 log/development.log` (Rails logs to file, not stdout!)
3. **Identify root cause** — gem bug? missing generator? wrong path? env var?
4. **Fix in source** — edit the actual file that has the bug
5. **Restart** — kill + restart the server process
6. **Verify** — `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000`

**⚠️ Rails logs to `log/development.log`, NOT stdout.** When running `rails server` in background, errors don't appear in the terminal output — you MUST read `log/development.log` to see the actual exception.

**Common 500 Root Causes (check in this order):**
| Error | Fix |
|-------|-----|
| `undefined method 'stringify_keys' for String` in view | `button_to ... do` with `data:` hash — use `form_with` instead |
| `ActionView::Template::Error: undefined method 'stringify_keys' in _stylist.html.erb:83` | `do |service, i)|` has stray `)` — close with `do |service, i| %>` |
| `syntax error unexpected ','` in controller | Combined hash+raw-sql in single `where()`: chain `.where(user: u).where("sql = ?", val)` |
| `NameError: uninitialized constant Ahoy::Store` | Run `bin/rails generate ahoy:install` then `bin/rails db:migrate` |
| 500 on asset load | Check `app/assets/builds/tailwind.css` exists and layout references `"tailwind"` not `"application.tailwind"` |

### Role-Specific Dashboard Architecture (Multiple Pages)

When a project requires **different dashboard layouts per user role** (owner, manager, stylist, receptionist, admin):

**itch HTML as role-specific *partials*, NOT a single shared view. Each role has its own Stitch-designed HTML page with different widgets, data, and button placements.

```
app/views/dashboard/
├── index.html.erb          # Router: renders partial based on current_user.role_name
├── _owner.html.erb
├── _manager.html.erb
├── _stylist.html.erb
├── _receptionist.html.erb
└── _admin.html.erb
```

**Router Pattern (`dashboard_controller.rb`):**
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
      # ... owner-specific queries
    when "manager"
      # ... manager-specific queries (revenue, staff roster, schedule)
    when "stylist"
ings = Booking.where(user: current_user)
      # ... stylist-specific queries
    when "receptionist"
      @todays_bookings = Booking.where("date(starts_at) = ?", Date.today)
      @stylists = User.joins(:roles).where(roles: { name: "stylist" })
    end
  end
end
```

**index.html.erb:**
```erb
<% content_for :title, "#{@role.titleize} Dashboard - CRM Hub" %>
/sidebar" %>
<%= render "dashboard/#{@role}" %>
```

**CRITICAL DIFFERENCES between role dashboards:**
- **Stylist** sees ONLY their own data (Bookings where user: current_user, their clients, their commissions)
- **Manager** sees ALL shop data (aggregate revenue, all staff, full schedule)
- **Receptionist** sees booking grid with Check-in/Check-out actions + walk-in form
- **Owner** sees high-level metrics + security tab

**⚠️ Common Data Query Pattern Pitfall:**
When combining hash conditions with raw SQL `where` clauses, do NOT mix them in a single `where` call:
```ruby
# WRONG — causes SyntaxError: unexpected ','; expected a value in the hash literal
Booking.where(user: current_user, "date(starts_at) = ?", Date.today)
#         ^           ^                                  ^
#         key: value  "raw SQL with ?"                   Date.today
# Rails can't parse this — it's mixing hash key:value with positional arg

# CORRECT — chain two where calls
Booking.where(user: current_user).where("date(starts_at) = ?", Date.today)
```

**⚠️ Role-specific buttons have different targets:**
- "New Appointment" (manager) → `new_booking_path`
- "New Booking" FAB (stylist) → `new_booking_path`
- "Check-in/Check-out" (receptionist) → `button_to booking_path(b), method: :patch, params: { booking: { status: :confirmed } }`
- "View All" / "View Roster" → respective index paths (`bookings_path`, `staff_path`)
- "View Full Report" → `analytics_path`

**Sidebar Role Visibility:**
The sidebar should show DIFFERENT items per role:
```erb
<% if %w[owner manager].include?(@role) %>
  Analytics, Staff, Settings -->
<% end %>
<% if %w[owner manager stylist].include?(@role) %>
  <!-- Loyalty -->
<% end %>
```

**⚠️ Verify ALL roles load, not just HTTP status:**
```bash
for email in owner@test.com manager@test.com stylist@test.com receptionist@test.com; do
  TOKEN=$(curl -s -c /tmp/crm.txt http://localhost:3000/users/sign_in | grep -oP 'authenticity_token" value="\K[^"]+')
  curl -s -b /tmp/crm.txt -c /tmp/crm.txt -X POST http://localhost:3000/users/sign_in -d "authenticity_token=$TOKEN&user[email]=${email}&user[password]=password123" -L -o /dev/null -w ""
  CODE=$(curl -s -b /tmp/crm.txt http://localhost:3000/dashboard -o /dev/null -w "%{http_code}")
  echo "${email}: HTTP ${CODE}"
done
```

### Decorative vs Real Buttons (CRITICAL USER COMPLAINT)

**❌ Decorative buttons (WRONG):** `href="#"` or buttons with no action do NOT work. The user explicitly flagged "most buttons don't work."
```html
<button class="...">Check-in</button>  <!-- does nothing -->
<a href="#">New Booking</a>            <!-- does nothing -->
```

**✅ Real buttons with Turbo (CORRECT):**
```erb
<%# Action button with PATCH — updates booking status %>
<%= button_to "Check-in", booking_path(booking), method: :patch,
    class: "w-full bg-accent-subtle text-primary rounded-lg uppercase font-bold text-xs hover:bg-primary/20 transition-colors",
    params: { booking: :confirmed } %>

<%# Navigation button with explicit path %>
<%= link_to new_booking_path, class: "flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-semibold" do %>
  <span class="material-symbols-outlined">add</span>
  New Booking
<% end %>

<%# Walk-in form with real POST %>
<%= form_with model: Booking.new, url: bookings_path, method: :post, local: true do |f| %>
  <%= f.text_field :client_name %>
  <%= f.collection_select :service_id, @services, :id, :name %>
  <%= f.submit "Confirm Walk-in" %>
<% end %>
```

### Subagent Timeout for Large View Sets

When delegating view conversion to subagents, **limit to 3-4 views per batch**.

**Failed pattern (timeout at 600s):**
- 8+ views dispatched → subagent processes slowly → 600s timeout → partial delivery

**Working pattern:**
- Dispatch ONE role at a time or 3-4 views max
- Include ALL requirements (view files, controller data, route wiring, button wiring) in a SINGLE dispatch
- Verify each role before moving to next
- If subagent times out, DO NOT re-dispatch — do it directly in the parent session

### Project Audit Patterns (CRM Hub)

When auditing an existing Rails project for conversion quality, check for these patterns:

```bash
# 1. Find inline sidebar duplication (should be a partial)
grep -l 'aside class.*w-60' app/views/**/*.erb | wc -l
# If > 1, extract to shared partial

# 2. Check for divide-border (rgba issue with Tailwind divide)
grep -rn 'divide-border' app/views/
# Fix: replace with divide-zinc-200 or divide-y with inline --tw-divide-opacity

# 3. Verify all views use min-h-[100dvh] not h-[100dvh]
grep -rn 'h-\[100dvh\]' app/views/
# Fix: change to min-h-[100dvh]

# 4. Check for content_for :title coverage
grep -rL 'content_for :title' app/views/**/*.erb
# All views should have this (except special files like manifests)

# 5. Verify Turbo attributes (no legacy data-method/data-confirm/data-remote)
grep -rn 'data-method=' app/views/
grep -rn 'data-confirm=' app/views/
grep -rn 'data-remote=' app/views/

# 6. Check OmniAuth buttons have turbo: false
grep -rn 'omniauth' app/views/ | grep -v 'turbo: false'
```

---

## Rule 15: Section Completeness Fidelity (CRITICAL)

⚠️ **User explicitly called this out.** When converting a Stitch HTML page to Rails ERB, you MUST convert ALL sections with perfect integrity. Do NOT omit, summarize, or cherry-pick sections.

**Common omissions that fail review:**
- Pricing section (even if it has 2+ cards with feature lists)
- "How It Works" / Process section (3-step grids, numbered cards)
- Testimonials with `<img>` avatar elements (must render the actual image tag)
- CTA sections (dark background variants with radial gradients)
- Footer with full multi-column grid + social icons
- Sparkline charts, shimmer animations, floating badges
- `<picture>` elements and `<img>` tags from Stitch (render with same src)

**Rule:** If the Stitch HTML has a `<section>`, `<nav>`, `<footer>`, or distinct content block, it MUST appear in the Rails ERB output. Read the ENTIRE HTML file before converting. Count the sections. Match them 1:1.

**For landing pages specifically:**
1. Read the full Stitch HTML (can be 400+ lines)
2. Identify every top-level section: nav, hero, features, process, testimonials, pricing, CTA, footer
3. Convert each section with its exact layout (asymmetric grids, bento cards, dark full-width cards)
4. Preserve all `<img src="...">`, `<picture>`, and `<source>` tags — they are intentional design elements
5. Preserve all SVG sparklines, progress bars, and animation classes
6. Add any missing CSS animation keyframes to `app/assets/tailwind/application.css`

**⚠️ PICTURE ELEMENTS ARE CRITICAL:** Stitch designs use `<picture>` with `<source srcset>` for responsive images and preview/illustration assets. These MUST be converted as-is. Do NOT replace with placeholder images. The exact `<img>` tag must render in the ERB output (not commented out or hidden via `class="hidden"`). If the Stitch HTML has an `<img>`, your ERB must have an `<img>` with the same `src` at the same nesting depth.

**Checklist before declaring a page "done":**
```bash
# Count sections in source vs output
grep -c '<section' /path/to/stitch.html
grep -c '<section' /path/to/rails.html.erb
# Numbers should match

# Count images in source vs output — MUST match
grep -c '<img' /path/to/stitch.html
grep -c '<img' /path/to/rails.html.erb
```

---

## Rule 16: Local Docker Development

When running the converted Rails 8 app locally for verification:

### docker-compose.yml Add an `app` Service for Local Dev

Kamal's `config/deploy.yml` only targets remote servers. Add this to `docker-compose.yml` for local running:

```yaml
app:
  build:
    context: .
    dockerfile: Dockerfile
  environment:
    RAILS_ENV: development
    SECRET_KEY_BASE: dev_secret_for_local_only
    DB_HOST: postgres
    DB_PORT: 5432
    DB_USER: your_app
    DB_PASSWORD: password
    RAILS_SERVE_STATIC_FILES: "true"
    RAILS_LOG_TO_STDOUT: "true"
  ports:
    - "3000:3000"
  depends_on:
    - postgres
    - redis
  command: bash -c "rm -f tmp/pids/server.pid && bundle exec rails server -b 0.0.0.0 -p 3000"
  volumes:
    - .:/rails
    - bundle_cache:/rails/vendor/bundle
```

### Common Boot Failures & Fixes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| `NameError: uninitialized constant Ahoy::Store` | `ahoy_matey` 5.x references `Ahoy::Store` but only defines `Ahoy::DatabaseStore` | Create `config/initializers/ahoy.rb` with `require "ahoy/database_store"; Ahoy::Store = Ahoy::DatabaseStore unless defined?(Ahoy::Store)` |
| `ArgumentError: unknown keyword: :aliases` | `YAML.unsafe_load` in older Psych versions doesn't support `aliases:` kwarg | Don't add `aliases: true` — Psych enables aliases by default in `unsafe_load` |
| Tailwind input not found | `tailwindcss-rails` expects CSS at `app/assets/tailwind/application.css`, not `app/assets/stylesheets/` | Move Tailwind input file to `app/assets/tailwind/application.css` |
| `secret_key_base missing` | Not set in container env | Set `SECRET_KEY_BASE` in docker-compose env or `.env` |
| ERB in `database.yml` not rendering | Rails parses ERB before YAML — `<<: *default` alias must be preserved and env vars must be quoted | Quote `<%=` lines; don't replace `<%=` with `***` or `<%` |
| Volume mount not hot-reloading initializers | Docker composer caches image; need `--force-recreate` | `docker kill <container> && docker compose up -d --force-recreate app` |

### Verification Flow

```bash
# 1. Start infrastructure
docker compose up -d postgres redis

# 2. Build + run app (first time slow — bundle install + asset compile)
docker compose up -d app

# 3. Wait for Rails boot, then test
sleep 8 && curl -s -w "\n%{http_code}" http://localhost:3000

# 4. For deeper debugging, run a one-off command
docker compose exec app bundle exec rails runner 'puts "Boot OK"'

# 5. Force-recreate after code changes that don't hot-reload
docker kill crm_hub-app-1 && docker compose up -d --force-recreate app
```

### Key Pitfall: Don't Loop on the Same Error

If the same error appears 3+ times across restarts, **stop and change approach**. Restarting Docker won't fix code/config issues. Read the full stack trace (`docker compose logs app --no-log-prefix`), identify the actual exception, fix the root cause in the source file, then rebuild. The `Ahoy::Store` error looked like it was persisting because the web server process was caching state — but the real issue was that the initializer was being defined too late in the boot cycle (database_store wasn't autoloaded yet when the initializer ran).

### Host Ruby ≠ Docker Gems

The host system Ruby and Docker container gems are **completely separate**. If the host is missing gems (e.g., `debug/prelude`), you cannot run `bundle exec rails` or `rails server` on the host. All Rails commands MUST run inside the container via `docker compose exec app` or `docker compose run --rm app`.

### Tailwind CSS Asset Path (CRITICAL)
⚠️ **The `tailwindcss-rails` gem outputs `tailwind.css`, NOT `application.tailwind.css`.**

When the input file is at `app/assets/tailwind/application.css`, running `bin/rails tailwindcss:build` produces `app/assets/builds/tailwind.css`. The layout MUST reference:
```erb
<%= stylesheet_link_tag "tailwind", "data-turbo-track": "reload" %>
```
NOT:
```erb
<%= stylesheet_link_tag "application.tailwind", "data-turbo-track": "reload" %>
```

The latter causes a 500 error because Propshaft can't find `application.tailwind.css` in the asset pipeline.

---

## Rule 17: SPA Navigation with Turbo Frames (Rails 8)

For CRM-style layouts with sidebars, use Turbo Frames to update only the content area when navigating via sidebar links. This avoids full page reloads and preserves sidebar state.

**Architecture:**
```
┌─────────────────────────────────────────────┐
│  Layout (application.html.erb)              │
│  ┌──────────┬────────────────────────────┐  │
│  │ Sidebar  │  <%= yield %>              │  │
│  │ (partial)│  (each view wraps content  │  │
│  │          │   in turbo_frame_tag)       │  │
│  │          │                            │  │
│  │ Links    │  Content here updates      │  │
│  │ use data: │  without full reload       │  │
│  │ turbo_   │                            │  │
│  │ frame:   │                            │  │
│  │ "main"   │                            │  │
│  └──────────┴────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**Step 1: Create shared sidebar partial**

```erb
<%# app/views/application/_sidebar.html.erb %>
<aside class="w-60 min-h-[100dvh] fixed left-0 top-0 bg-white border-r border-border z-50 flex flex-col p-8">
  <div class="px-6 mb-8">
    <h1 class="text-xl font-bold tracking-tight text-primary">CRM Admin</h1>
    <p class="text-steel text-[12px] opacity-70">Enterprise Tier</p>
  </div>
  <nav class="flex-1 space-y-1 px-2 overflow-y-auto scrollbar-hide">
    <%= link_to dashboard_path, class: sidebar_nav_class(dashboard_path), data: { turbo_frame: "main_content" } do %>
      <svg>...</svg>
      <span class="text-sm text-steel">Dashboard</span>
    <% end %>
    <%= link_to clients_path, class: sidebar_nav_class(clients_path), data: { turbo_frame: "main_content" } do %>
      ...
    <% end %>
  </nav>
  <div class="px-6 mt-8 border-t border-border pt-6 flex items-center gap-3">
    <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold text-[12px]">AU</div>
    <div>
      <p class="text-sm font-semibold text-ink leading-tight">Admin User</p>
      <p class="text-steel text-[11px]">System Owner</p>
    </div>
  </div>
</aside>
```

**Step 2: Create helper for active state**

```ruby
# app/helpers/application_helper.rb
module ApplicationHelper
  def sidebar_nav_class(path)
    is_active = request.path.start_with?(path.gsub(/\?.*$/, ""))
    if is_active
      "flex items-center gap-3 px-3 py-2 rounded-lg bg-primary-subtle text-primary border-l-4 border-primary font-bold group"
    else
      "flex items-center gap-3 px-3 py-2 rounded-lg text-steel hover:bg-canvas transition-colors group"
    end
  end
end
```

**Step 3: Wrap each view's main content**

```erb
<%# In each view file %>
<%= render "application/sidebar" %>

<%= turbo_frame_tag "main_content" do %>
  <main class="ml-60 flex flex-col min-h-[100dvh]">
    ...page content...
  </main>
  <% end %>
<% end %>
```

**Step 4: Handle nested turbo_frame_tag in views that already wrap content**

⚠️ **PITFALL**: Do NOT put `turbo_frame_tag "main_content"` in both the layout AND individual views. Choose one:
- **Option A (recommended)**: Put `turbo_frame_tag` in each view, keep layout clean (`<%= yield %>`)
- **Option B**: Put `turbo_frame_tag` in layout, don't wrap in views

**Step 5: Add real-time updates via Solid Cable (optional)**

```ruby
# app/channels/dashboard_channel.rb
class DashboardChannel < ApplicationCable::Channel
  def subscribed
    stream_from "dashboard"
  end
end
```

```erb
<%# In the view that needs live updates %>
<% content_for :head do %>
  <%= turbo_stream_from "dashboard" %>
<% end %>
```

**Broadcasting from controller:**
```ruby
# In controller action:
ActionCable.server.broadcast("dashboard", {
  type: "new_booking",
  booking: render_to_string(partial: "bookings/card", locals: { booking: @booking })
})
```

**Key Turbo Frame rules:**
| Pattern | Usage |
|---------|-------|
| `data: { turbo_frame: "main_content" }` | On sidebar links — updates frame instead of full page |
| `<%= turbo_frame_tag "main_content" do %>` | Wraps view content — replaced on navigation |
| `turbo_stream_from "channel"` | Subscribes view to real-time updates |
| `data: { turbo: false }` | Disables Turbo (external links, OmniAuth) |
| `data: { turbo_method: :delete }` | DELETE via link (replaces `data-method`) |
| `data: { turbo_confirm: "..." }` | Confirmation dialog (replaces `data-confirm`) |

---

## Related Skills

## Support Files

- `references/icon-mappings.md` — Material Symbol → Heroicons SVG path database (100+ icons)
- `references/scavenger-hunt-checklist.md` — Before creating any skill or capability from scratch, check Gemini imports first
- `references/crm-layout-patterns.md` — Standard sidebar, mobile nav, main content area patterns
- `references/crm-hub-audit.md` — Project audit checklist and fix patterns for CRM view refactoring
- `references/docker-debugging.md` — Docker Compose + Rails 8 deployment debugging cookbook (boot failures, gem issues, volume mounts)
- `references/acts_as_tenant-seeds.md` — Seed patterns for acts_as_tenant (duplicate migration avoidance, Current.account pitfalls)
- `references/landing-page-fidelity.md` — Landing page conversion: section completeness, image handling, animation CSS patterns, verification script
- `scripts/password-toggle-controller.js` — Stimulus controller for password visibility toggle
- `scripts/verify-views.sh` — Convert ERB → standalone HTML and screenshot at 1440px + 375px
- `templates/_sidebar.html.erb` — Starter sidebar partial template with Turbo Frame nav
