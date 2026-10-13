# Landing Page Conversion: Fidelity Patterns

## The Pitfall

When converting a Stitch landing page (400+ lines) to Rails ERB, it's easy to:
1. Omit entire sections (pricing, process, testimonials)
2. Replace `<img>` tags with placeholder text instead of preserving them
3. Simplify asymmetric grid layouts into generic cards
4. Skip animation CSS keyframes referenced by classes in the HTML

**Rule:** Match sections 1:1. Every `<section>`, `<nav>`, `<footer>` in the Stitch source MUST appear in the Rails output.

## Typical Landing Page Structure (Stitch)

```
<nav>                    — Fixed glassmorphism nav with logo + links + CTA
<section #hero>          — Asymmetric 2-column (copy + dashboard card with sparkline)
<section #features>      — Bento grid (varied sizes, dark full-width cards)
<section #process>       — 3-step asymmetric numbered grid with progress bars
<section #testimonials>  — Quote cards with <img> avatar photos
<section #pricing>       — 2-3 column cards with feature lists + "Most Popular" badge
<section #cta>           — Full-width dark section with radial gradient + CTA button
<footer>                 — Multi-column grid + social icons + copyright
```

## Image Handling

Stitch uses `https://picsum.photos/seed/...` for design images. These should be PRESERVED as-is in the Rails ERB. They are real images that render in production.

```erb
<%# KEEP these — they render actual images %>
<img src="https://picsum.photos/seed/crm-booking-calendar/600/300" alt="Booking calendar" class="...">
<img src="https://picsum.photos/seed/elena-rodriguez/96/96" alt="Elena Rodriguez" class="rounded-full object-cover">
```

## Animation Classes Requiring CSS

These classes are used in Stitch landing pages but NOT part of Tailwind core. They must be defined in `app/assets/tailwind/application.css`:

```css
/* Mesh gradient background for hero */
.mesh-gradient {
  background:
    radial-gradient(ellipse at 20% 50%, rgba(13, 148, 136, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(13, 148, 136, 0.05) 0%, transparent 50%),
    radial-gradient(ellipse at 40% 80%, rgba(20, 184, 166, 0.04) 0%, transparent 50%),
    var(--color-canvas, #F8FAFB);
}

/* Floating animation for badges */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}
.animate-float { animation: float 3s ease-in-out infinite; }

/* Pulse ring for status indicators */
@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(2.5); opacity: 0; }
}

/* Shimmer loading bars */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.animate-shimmer {
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.05) 75%);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

/* Navigation scroll state */
.nav-scrolled {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.95);
}

/* Reveal on scroll */
.reveal-hidden { opacity: 0; transform: translateY(24px); }
.reveal-visible { opacity: 1; transform: translateY(0); transition: opacity 0.6s, transform 0.6s; }
```

## Verification Script

After converting a landing page, verify section count parity:

```bash
# Count source sections (Stitch)
grep -c '<section' /path/to/stitch-landing.html

# Count output sections (Rails)
grep -c '<section' /path/to/app/views/pages/landing.html.erb

# Should match. If lower in Rails, you omitted something.

# Verify all images preserved
grep -c '<img' /path/to/stitch-landing.html
grep -c '<img' /path/to/app/views/pages/landing.html.erb

# Should match exactly.
```

## Session Learning (2026-06-27)

The assistant converted a CRM Hub landing page but:
- Omitted the Process ("How It Works") section entirely
- Omitted the Pricing section entirely  
- Replaced testimonial avatar images with text initials
- Simplified the bento grid features into generic cards

User feedback: *"you omitted the pricing part and how it works, the html has picture element you could have rendered with perfect integrity"*

**Root cause:** The assistant read only partial HTML and improvised the rest instead of reading the full file and converting section-by-section.
