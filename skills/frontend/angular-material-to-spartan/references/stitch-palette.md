# Stitch Design Palette (ks-knowledge-sharing "Momentum" dark)

Extracted from stitch-designs/*.json. Use as the `:root` CSS vars + `@layer components` values.

## Colors
| Token | Hex | Use |
|-------|-----|-----|
| background | #051424 | App body bg, inputs |
| card | #0b1a30 | hlmCard surface |
| sidebar | #0a1322 | header/sidebar/footer bg |
| primary | #5C6BC0 | buttons, links, active states |
| primary-foreground | #ffffff | text on primary |
| primary-strong | #2f3f92 | borders, dividers |
| primary-deep | #4858ab | hover/active fills |
| muted | #111a2e | chip/secondary fills |
| muted-foreground | #9aa4bf | secondary text |
| border | #2f3f92 | card/input borders |
| destructive | #ba1a1a | errors |
| tints | #bac3ff #dee0ff #f8f6ff #d4e4fa | light accents |
| neutrals | #ffffff #f8f9fa #c6c5d3 #e1e3e4 #767683 #454651 | text/dividers |
| accent-green | #43A047 | success |
| error-bg | #ffdad6 / #93000a | error surfaces |

## Typography
- Font: Inter (load via index.html Google Fonts link; set `font-family` on :root).
- Headings: 600–700 weight, tight tracking (-0.02em).
- Body: 1rem / 1.6 line-height, color muted-foreground on cards.

## Radius / spacing
- Cards: rounded-2xl (1rem) to rounded-3xl (1.5rem).
- Buttons: rounded-xl (0.75rem).
- Inputs: rounded-xl, py-2.5/py-3, pl-11 when icon-prefixed.
- Consistent max-width container 1100–1200px, centered.

## Mapping to SpartAN semantic classes
bg-background→#051424 · bg-card→#0b1a30 · bg-sidebar→#0a1322 · bg-primary→#5C6BC0 · border-border→#2f3f92 · text-foreground→#ffffff · text-muted-foreground→#9aa4bf · bg-muted→#111a2e · bg-primary/15 (hover)→ rgba(92,107,192,.15)
