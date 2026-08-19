# Angular Material 3 + Taste Skill: concrete recipe

Companion to SKILL.md Section 2.C. Use when applying the taste skill to an
Angular (standalone components, signals) + Angular Material 3 project.

## Design tokens in SCSS (theme-aware, no hardcoded light/dark hex)
```scss
:host {
  --ks-accent: #5c6bc0;                      // ONE accent, locked
  --ks-accent-soft: rgba(92, 107, 192, 0.12);
}
.bento-cell {
  background: var(--mat-sys-surface-container);
  border: 1px solid var(--mat-sys-outline-variant);
  border-radius: 20px;                       // ONE radius scale
}
.section-sub { color: var(--mat-sys-on-surface-variant); }
```
Material 3 exposes `--mat-sys-*` tokens that flip automatically with
`document.documentElement.style.colorScheme = 'light' | 'dark'` (set in a
ThemeService, persisted to localStorage). Using these means one SCSS block
renders correctly in both themes.

## GSAP scroll-reveal directive (with fallback so content is never stuck invisible)
```ts
@Directive({ selector: '[appReveal]', standalone: true })
export class RevealDirective implements OnInit, OnDestroy {
  @Input() revealDelay = 0;
  private el = inject(ElementRef);
  private obs?: IntersectionObserver;
  private fallback?: ReturnType<typeof setTimeout>;
  ngOnInit() {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const node = this.el.nativeElement as HTMLElement;
    node.style.opacity = '0';
    this.obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          gsap.to(node, { opacity: 1, y: 0, duration: 0.7, delay: this.revealDelay, ease: 'power2.out' });
          this.obs?.disconnect();
        }
      });
    }, { threshold: 0.15 });
    this.obs.observe(node);
    // Fallback: reveal even if the observer never fires (headless, already-in-view)
    this.fallback = setTimeout(() => gsap.set(node, { opacity: 1, y: 0 }), 1200);
  }
  ngOnDestroy() { this.obs?.disconnect(); if (this.fallback) clearTimeout(this.fallback); }
}
```
Key pitfalls caught in practice:
- Without the fallback timeout, content stays `opacity:0` if IntersectionObserver
  does not fire (e.g. headless `scrollIntoView` does not trigger a real scroll).
- Without the reduced-motion early-return, you animate for users who asked not to.

## Three.js hero with graceful WebGL fallback
Wrap `new THREE.WebGLRenderer(...)` in try/catch inside `ngOnInit`. On failure
(set `canvas.hidden = true`, log a warning, keep the CSS gradient hero). An
unhandled WebGL error throws and can blank the whole page in headless/old
browsers. Always `renderer.dispose()` + remove the resize listener in `ngOnDestroy`.

## Headless verification (Puppeteer + system Chrome)
Do NOT trust `ng build` alone. The build passes even when runtime throws.
```js
const puppeteer = require('puppeteer');
const browser = await puppeteer.launch({
  headless: 'new',
  executablePath: '/usr/local/bin/google-chrome',   // system chrome, not bundled
  args: ['--no-sandbox', '--use-gl=swiftshader'],   // swiftshader = software WebGL
});
const page = await browser.newPage();
const pageErrors = [];
page.on('pageerror', (e) => pageErrors.push(String(e)));
await page.goto('http://localhost:4200/', { waitUntil: 'networkidle0' });
// Seed mock auth if routes are guard-gated
await page.evaluate(() => {
  localStorage.setItem('currentUser', JSON.stringify({ id:'u1', username:'admin', firstName:'A', lastName:'U', role:'admin', isActive:true, createdAt:new Date().toISOString() }));
  localStorage.setItem('access_token', 'tok');
});
await page.reload({ waitUntil: 'networkidle0' });
await new Promise(r => setTimeout(r, 2500));
const result = await page.evaluate(() => ({
  heroText: document.querySelector('.hero-section h1')?.textContent?.trim(),
  bentoCells: document.querySelectorAll('.bento-cell').length,
  picsum: getComputedStyle(document.querySelector('.cell-image')).backgroundImage.includes('picsum'),
}));
console.log(JSON.stringify({ pageErrors, result }, null, 2));
```
Assertions to check:
- `pageErrors` is empty (graceful WebGL fallback means no thrown errors even
  when `hasWebGL` is false).
- Theme toggle flips `document.documentElement.style.colorScheme`.
- Real images (picsum) actually load (`backgroundImage` contains the URL).

## image_gen fallback
If `image_generate` returns "Image generation is unavailable (no FAL_KEY)",
use `https://picsum.photos/seed/{descriptive}/{w}/{h}` for section imagery.
This satisfies the skill's "real images second" tier without fake divs.
