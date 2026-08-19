# Tailwind v4 Design System Reference

> **For CRMHub Rails 8 + Hotwire project**
> Tailwind CSS v4.3.1 — CSS-first `@theme` tokens, no `tailwind.config.js`

---

## 1. Theme Tokens (`app/assets/tailwind/application.css`)

```css
@import "tailwindcss";

@theme {
  /* Brand Colors */
  --color-primary: #0D9488;
  --color-primary-hover: #0F766E;
  --color-primary-subtle: #CCFBF1;
  --color-primary-fixed: #89F5E7;

  /* Surface Colors */
  --color-canvas: #F8FAFB;
  --color-surface: #FFFFFF;

  /* Text Colors */
  --color-ink: #18181B;
  --color-steel: #71717A;

  /* Border */
  --color-border: rgba(226, 232, 240, 0.5);

  /* Semantic Colors */
  --color-success: #059669;
  --color-warning: #D97706;
  --color-error: #DC2626;
  --color-info: #0284C7;

  /* Typography */
  --font-geist: "Geist", "system-ui", sans-serif;
  --font-mono: "Geist Mono", "JetBrains Mono", monospace;

  /* Border Radius */
  --radius-DEFAULT: 12px;
  --radius-lg: 8px;
  --radius-xl: 16px;
}
```

---

## 2. Color Class Map

| Design Token | Tailwind Class | Hex Value | Usage |
|---|---|---|---|
| primary | `bg-primary` / `text-primary` | `#0D9488` | CTAs, active states, focus rings, avatar backgrounds |
| primary-hover | `hover:bg-primary-hover` | `#0F766E` | Hover state on primary buttons |
| primary-subtle | `bg-primary-subtle` | `#CCFBF1` | Active nav items, light teal backgrounds |
| canvas | `bg-canvas` | `#F8FAFB` | Page background |
| surface / white | `bg-white` | `#FFFFFF` | Card backgrounds, modals |
| ink | `text-ink` | `#18181B` | Primary text, headings |
| steel | `text-steel` | `#71717A` | Secondary text, metadata, timestamps |
| border | `border-border` | `rgba(226,232,240,0.5)` | Card borders, dividers |
| success | `bg-success/10` `text-success` | `#059669` | Confirmed, active, positive states |
| warning | `bg-warning/10` `text-warning` | `#D97706` | Pending, caution states |
| error | `bg-error/10` `text-error` | `#DC2626` | Delete, failed, error states |
| info | `bg-info/10` `text-info` | `#0284C7` | Informational badges |

---

## 3. Typography

| Element | Class | Notes |
|---|---|---|
| Body | `font-geist` (set on body) | Geist via Google Fonts |
| Page title | `text-2xl font-bold tracking-tight text-ink` | Main page headings |
| Section heading | `text-lg font-semibold text-ink` | Card titles, section headers |
| Card title | `text-sm font-semibold text-ink` | Smaller headings |
| Label | `text-xs uppercase tracking-wider font-semibold text-steel` | Table headers, form labels |
| Body text | `text-sm text-steel` | Descriptions, secondary text |
| Mono / metrics | `text-xs font-mono text-steel` | Prices, timestamps, phone numbers, IDs |

**Font Loading (layout head):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@100..900&family=Geist+Mono:wght@100..800&display=swap" rel="stylesheet">
```

---

## 4. Spacing & Sizing

| Element | Value | Class |
|---|---|---|
| Sidebar width | 240px | `w-60` |
| Sidebar collapsed | 64px | `w-16` |
| Max content width | 1280px | `max-w-7xl` |
| Card padding | 20px | `p-5` |
| Section gap | 32px | `gap-8` |
| Card gap | 16px | `gap-4` |
| Form field gap | 16px | `space-y-5` → 20px |
| Touch target minimum | 48px | `min-h-[48px]` |

---

## 5. Border Radius

| Usage | Class | Pixels |
|---|---|---|
| Inputs | `rounded-lg` | 8px |
| Buttons | `rounded-xl` | 12px |
| Cards, panels | `rounded-xl` | 12px |
| Large hero cards | `rounded-2xl` | 16px |
| Status badges, pills | `rounded-full` | 9999px |
| Avatar | `rounded-full` | 9999px |

---

## 6. Component Patterns

### Cards
```erb
<div class="bg-white rounded-xl border border-border p-6 shadow-sm hover:shadow-md transition-shadow">
  <!-- content -->
</div>
```

### Sidebar Nav Item (Active)
```erb
"flex items-center gap-3 px-3 py-2 rounded-lg bg-primary-subtle text-primary border-l-4 border-primary font-bold transition-spring group"
```

### Sidebar Nav Item (Inactive)
```erb
"flex items-center gap-3 px-3 py-2 rounded-lg text-steel hover:bg-canvas transition-colors group"
```

### Primary Button
```erb
class: "px-4 py-2.5 bg-primary text-white rounded-xl font-medium hover:bg-primary-hover transition-spring btn-push"
```

### Ghost/Secondary Button
```erb
class: "px-4 py-2.5 border border-border text-ink rounded-xl font-medium hover:bg-canvas transition-spring"
```

### Destructive Button
```erb
class: "px-4 py-2.5 bg-error text-white rounded-xl font-medium hover:bg-error/90 transition-spring"
```

### Status Badges
```erb
# Confirmed/Active: "bg-success/10 text-success"
# Pending:         "bg-warning/10 text-warning"
# Completed:       "bg-primary/10 text-primary"
# Cancelled/Error: "bg-error/10 text-error"
# Draft/Inactive:  "bg-zinc-100 text-steel"

<span class="text-xs px-2.5 py-1 rounded-full font-medium bg-success/10 text-success">
  <%= status %>
</span>
```

### Data Tables
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

### Form Inputs
```erb
<div class="space-y-2">
  <%= f.label :field, class: "block text-sm font-medium text-ink" %>
  <%= f.text_field :field,
      class: "w-full px-4 py-3 rounded-xl border border-border bg-white text-ink focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm" %>
</div>
```

### Avatar Initials
```erb
<div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white font-bold text-xs">
  <%= user.initials %>
</div>
```

### Flash Messages
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

---

## 7. Animation Utilities

```css
/* In app/assets/tailwind/application.css */

@keyframes fade-up {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-up {
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.btn-push:active {
  transform: scale(0.98) translateY(1px);
  transition: transform 0.1s;
}

.transition-spring {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
```

---

## 8. Stitch-to-ERB Token Mapping

| Stitch Token/Value | → Rails ERB / Tailwind |
|---|---|
| `primary` (#00685f) | `primary` (#0D9488) |
| `accent-hover` | `primary-hover` (#0F766E) |
| `accent-subtle` / #CCFBF1 | `primary-subtle` |
| `pure-surface` / #FFFFFF | `white` / `bg-white` |
| `canvas` / #F8FAFB | `canvas` / `bg-canvas` |
| `on-surface` / #171d1c | `ink` (#18181B) |
| `on-secondary-container` / #656467 | `steel` (#71717A) |
| `whisper-border` / rgba(229,231,235,0.6) | `border` (rgba(226,232,240,0.5)) |
| `surface-container` / #eaefed | `canvas` |
| `success` / #059669 | `success` |
| `warning` / #D97706 | `warning` |
| `error` / #DC2626 | `error` |
| `tertiary` / #555c6a | `steel` |
| `font-page-title` | `text-2xl font-bold tracking-tight` |
| `font-section-heading` | `text-lg font-semibold` |
| `font-card-title` | `text-sm font-semibold` |
| `font-label-caps` | `text-xs uppercase tracking-wider font-semibold` |
| `font-body-relaxed` | `text-sm text-steel` |
| `font-meta-mono` | `text-xs font-mono text-steel` |
| `material-symbols-outlined` | Heroicons SVG (inline) |
| `h-screen` | `min-h-[100dvh]` |
| `divide-border` (rgba) | `divide-y divide-zinc-200` |
| `scrollbar-hide` (not built-in) | Add CSS utility class |
| `text-tertiary` (undefined) | `text-steel` |
| `h-11` (44px) | `min-h-[48px]` |
| `w-sidebar-width` | `w-60` |
| `ml-sidebar-width` | `ml-60` |
| `max-w-max-content` | `max-w-7xl` |
| `border-radius: 12px` | `rounded-xl` |
| `border-radius: 8px` | `rounded-lg` |
| `p-xs` through `p-xxl` | `p-1` through `p-8` |

---

## 9. Common Mistakes to Avoid

| Mistake | Fix |
|---|---|
| Using `text-[11px]`, `text-[32px]`, etc. in ERB | Tailwind v4 scanner drops arbitrary values. Replace ALL with standard classes — see replacement table below |
| Using `active:scale-[0.98]` in ERB | Replace with `active:scale-95` |
| Using `active:translate-y-[1px]` | Replace with `active:translate-y-px` |
| Forgetting to rebuild CSS after editing `application.css` | Always run `bundle exec bin/rails tailwindcss:build` then restart server |
| Using `h-screen` | Use `min-h-[100dvh]` — allows content to expand |
| Using `divide-border` with rgba | Use `divide-y divide-zinc-200` |
| Using `data-method=` / `data-confirm=` | Use `data-turbo-method=` / `data-turbo-confirm=` |
| Using `devise_error_messages!` (Devise 5 removed it) | Use `devise/shared/error_messages` partial |
| Using `enum status: {...}` (Rails 7 syntax) | Use `enum :status, {...}` (Rails 8 syntax) |
| Manually creating model files | Always use `rails g model` first, then edit |
| Running `rails g devise User` twice | Check `db/migrate/` — creates duplicate email column |
| Not setting `account:` in seeds with acts_as_tenant | Always pass `account: account` explicitly in seeds |
| Using `sed` to convert HTML→ERB | Never works — use stitch-to-rails-erb skill rules |
| Using `rounded-lg` for cards | Cards use `rounded-xl` (12px), inputs use `rounded-lg` (8px) |
| Forgetting `min-h-[48px]` on touch targets | All clickable elements must be ≥48px |

### Arbitrary Value → Standard Class Replacement Table

Use this when converting or fixing any ERB view. Run via Python execute_code for bulk fixes:

```python
patterns = [
    # text sizes
    ('text-[9px]', 'text-xs'), ('text-[10px]', 'text-xs'), ('text-[11px]', 'text-xs'), ('text-[12px]', 'text-xs'),
    ('text-[13px]', 'text-sm'), ('text-[14px]', 'text-sm'), ('text-[15px]', 'text-sm'), ('text-[16px]', 'text-sm'),
    ('text-[18px]', 'text-lg'), ('text-[20px]', 'text-xl'), ('text-[24px]', 'text-2xl'), ('text-[28px]', 'text-2xl'),
    ('text-[32px]', 'text-3xl'),
    # scale / translate
    ('active:scale-[0.98]', 'active:scale-95'), ('active:scale-[0.97]', 'active:scale-97'),
    ('active:translate-y-[1px]', 'active:translate-y-px'),
]
```

### CSS Rebuild Verification

```bash
# After any change to application.css:
cd /home/deeone/projects/crm_hub
bundle exec bin/rails tailwindcss:build

# Verify custom classes are in compiled output:
grep -o "page-title\|section-heading\|accent-hover\|on-surface-variant" app/assets/builds/tailwind.css | sort | uniq -c

# Restart server to pick up new asset hash:
kill $(cat tmp/pids/server.pid) && sleep 1 && bundle exec rails server -b 0.0.0.0 -p 3000 &
```
