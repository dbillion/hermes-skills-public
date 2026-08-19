# Rails 8 + Tailwind CSS v4 Integration Guide

## When to use this

When a Ruby on Rails 8 project needs taste-skill-quality animated landing pages with Tailwind CSS v4, and the `tailwindcss-rails` gem has bundler version conflicts.

## The bundler conflict problem

`tailwindcss-rails` 4.6+ requires `tailwindcss-ruby` which expects Bundler 2.x. If your project was generated with Bundler 4.x (or the lockfile was), `bundle install` fails with version mismatches cascading through railties, propshaft, and all gems. Each `gem install X` pulls 5-10 dependencies manually until you hit another conflict.

## The workaround: standalone Tailwind CLI

Bypass the gem. Build CSS directly with the official CLI.

```bash
# 1. Install Tailwind v4 locally (no gem needed)
npm install tailwindcss @tailwindcss/cli

# 2. Create your design-system CSS file
#    app/assets/stylesheets/application.tailwind.css
cat > app/assets/stylesheets/application.tailwind.css << 'EOF'
@import "tailwindcss";

@theme {
  --color-primary: #0D9488;
  --color-primary-hover: #0F766E;
  --color-primary-subtle: #CCFBF1;
  --color-ink: #18181B;
  --color-steel: #71717A;
  --color-border: rgba(226, 232, 240, 0.5);
  --font-geist: "Geist", system-ui, sans-serif;
  --radius-DEFAULT: 12px;
}

/* Spring physics animations */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-up {
  animation: fade-up 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
}
/* Stagger: .delay-150 { animation-delay: 150ms; } etc. */

/* Scroll reveal (driven by IntersectionObserver) */
.reveal-hidden {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}
.reveal-visible { opacity: 1; transform: translateY(0); }

/* Tactile push */
.btn-push:active { transform: translateY(1px) scale(0.98); }

/* Glassmorphism */
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .animate-fade-up, .reveal-hidden { animation: none !important; opacity: 1 !important; transform: none !important; transition: none !important; }
}
EOF

# 3. Build CSS (run during deployment or as a dev task)
npx @tailwindcss/cli -i app/assets/stylesheets/application.tailwind.css \
  -o app/assets/stylesheets/application.css --minify

# 4. Rails layout: serve the built CSS via stylesheet_link_tag
#    No need for tailwindcss-rails gem in production.
```

## Stimulus controllers for taste-skill motion

Create these in `app/javascript/controllers/`:

**appearance_controller.js** - Scroll-reveal + nav scroll state:
```javascript
import { Controller } from "@hotwired/stimulus"
export default class extends Controller {
  static targets = ["reveal", "nav"]
  connect() {
    this.revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const delay = parseInt(entry.target.dataset.revealDelay || "0")
          setTimeout(() => {
            entry.target.classList.remove("reveal-hidden")
            entry.target.classList.add("reveal-visible")
          }, delay)
          this.revealObserver.unobserve(entry.target)
        }
      })
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" })
    this.revealTargets.forEach(el => this.revealObserver.observe(el))
    if (this.hasNavTarget) {
      window.addEventListener("scroll", () => {
        if (window.scrollY > 20) this.navTarget.classList.add("nav-scrolled")
        else this.navTarget.classList.remove("nav-scrolled")
      }, { passive: true })
    }
  }
  disconnect() { this.revealObserver.disconnect() }
}
```

**magnetic_controller.js** - CTA magnetic hover:
```javascript
import { Controller } from "@hotwired/stimulus"
export default class extends Controller {
  connect() {
    this.onMove = (e) => {
      const rect = this.element.getBoundingClientRect()
      const x = e.clientX - rect.left - rect.width / 2
      const y = e.clientY - rect.top - rect.height / 2
      this.element.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`
      this.element.style.transition = ""
    }
    this.onLeave = () => {
      this.element.style.transform = "translate(0,0)"
      this.element.style.transition = "transform 0.4s cubic-bezier(0.175,0.885,0.32,1.275)"
    }
    this.element.addEventListener("mousemove", this.onMove)
    this.element.addEventListener("mouseleave", this.onLeave)
  }
  disconnect() {
    this.element.removeEventListener("mousemove", this.onMove)
    this.element.removeEventListener("mouseleave", this.onLeave)
  }
}
```

Register in `app/javascript/controllers/index.js`:
```javascript
import { Application } from "@hotwired/stimulus"
import AppearanceController from "./appearance_controller"
import MagneticController from "./magnetic_controller"
const application = Application.start()
application.register("appearance", AppearanceController)
application.register("magnetic", MagneticController)
application.debug = false
window.Stimulus = application
```

## Importmap (config/importmap.rb)

```ruby
pin "@hotwired/stimulus", to: "stimulus.js"   # copy from node_modules to vendor/javascript/
pin "application", to: "controllers/index.js"
pin "controllers/appearance_controller", to: "controllers/appearance_controller.js"
pin "controllers/magnetic_controller", to: "controllers/magnetic_controller.js"
```

Install Stimulus locally: `npm install @hotwired/stimulus` then copy `node_modules/@hotwired/stimulus/dist/stimulus.js` to `vendor/javascript/`.

## ERB-to-standalone-HTML for visual verification

To screenshot a Rails ERB view without running the full Rails server:

```bash
# Convert ERB to plain HTML, inline all CSS, append JS
cd your_rails_project

CSS=$(cat .stitch/output.css)
BODY=$(cat app/views/pages/landing.html.erb | sed \
  -e 's/<%= new_user_session_path %>/#sign-in/g' \
  -e 's/<%= new_user_registration_path %>/#sign-up/g' \
  -e 's/<%= csrf_meta_tags %>//g' \
  -e 's/<%= csp_meta_tag %>//g' \
  -e 's/<%= yield :head %>//g' \
  -e 's/<%= content_for :title, .* %>//g')

cat > /tmp/standalone.html << HTMLEOF
<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CRM Hub</title>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@100..900&family=Geist+Mono:wght@100..800&display=swap" rel="stylesheet">
<style>${CSS}</style></head>
<body class="font-geist antialiased bg-canvas text-ink">${BODY}
<script>
// Paste Stimulus controller logic as vanilla JS here
</script></body></html>
HTMLEOF

# Screenshot with Chromium
chromium --headless --disable-gpu --screenshot=output.png \
  --window-size=1440,2400 --virtual-time-budget=8000 \
  http://localhost:3100/landing-standalone.html
```

## Key pitfalls

1. **Bundler 2.x vs 4.x mismatch** manifests as cascading "An error occurred while installing X" failures that look like gem bugs but are bundler version incompatibility. Using `npm` to build Tailwind sidesteps this entirely.
2. **ERB path helpers** must be replaced with static URLs when converting to standalone HTML for screenshots.
3. **`prefers-reduced-motion`** must be respected on ALL animations (scroll-reveal, float, shimmer, magnetic). Use the `@media (prefers-reduced-motion: reduce)` CSS block or `useReducedMotion()` JS hook.
4. **Scroll-linked animations** MUST use IntersectionObserver or ScrollTrigger, never `window.addEventListener('scroll', ...)` which is jank-prone.
5. **Fonts**: Use `<link>` tags (not `@import`) for Google Fonts in production. `font-display: swap` is implicit with Google Fonts URLs.
