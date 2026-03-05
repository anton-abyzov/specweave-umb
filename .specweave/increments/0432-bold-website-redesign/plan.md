# Implementation Plan: Bold Website Redesign

## Overview

A comprehensive redesign of the SpecWeave website (spec-weave.com), a Docusaurus 3.9.2 static site at `repositories/anton-abyzov/specweave/docs-site/`. The redesign expands the existing ~200-token design system to 350+ tokens, replaces the monolithic 5-section landing page with 11 modular sections built from 15 reusable components, introduces a zero-bundle-cost animation system using CSS @keyframes + IntersectionObserver, and redesigns navigation with a mega-menu navbar and custom footer via Docusaurus swizzle.

All work targets `repositories/anton-abyzov/specweave/docs-site/` within the umbrella repo.

## Architecture

### 1. File Structure and Component Organization

The current structure is a flat monolith: one 400-line `index.tsx` with inline SVG icons, one 1000-line `index.module.css`, a 211-line `tokens.css`, and 4 existing MDX components (Accordion, Callouts, CardGroup, Steps).

The target structure decomposes the system into three tiers: tokens (foundation), primitives (atoms), and compositions (sections).

```
docs-site/src/
  css/
    tokens.css                    # Expanded to 350+ custom properties
    animations.css                # @keyframes definitions (extracted)
    custom.css                    # Global Docusaurus overrides (existing)
  components/
    ui/                           # Tier 1: UI Primitives
      Button/
        index.tsx                 # variant: primary|secondary|ghost|outline
        Button.module.css
      Badge/
        index.tsx                 # variant: default|success|warning|info|primary
        Badge.module.css
      Icon/
        index.tsx                 # Wraps Lucide + brand SVGs
        brands/                   # Brand SVG files (github.svg, jira.svg, etc.)
      CodeBlock/
        index.tsx                 # Syntax highlight + copy button
        CodeBlock.module.css
      Divider/
        index.tsx
        Divider.module.css
    layout/                       # Tier 2: Section Layout
      Section/
        index.tsx                 # variant: default|dark|gradient|accent
        Section.module.css
      SectionHeader/
        index.tsx                 # label + title + subtitle composition
        SectionHeader.module.css
    cards/                        # Tier 3: Card Components
      FeatureCard/
        index.tsx
        FeatureCard.module.css
      ContentCard/
        index.tsx                 # Academy course listings
        ContentCard.module.css
      StatCard/
        index.tsx                 # Large display value + label
        StatCard.module.css
      IntegrationCard/
        index.tsx
        IntegrationCard.module.css
      PricingCard/
        index.tsx                 # Built but no pricing page this increment
        PricingCard.module.css
    animation/                    # Tier 4: Animation Wrappers
      AnimateOnScroll/
        index.tsx                 # IntersectionObserver + CSS class toggle
        AnimateOnScroll.module.css
      WordAnimation/
        index.tsx                 # Staggered word-by-word reveal
        WordAnimation.module.css
      CountUp/
        index.tsx                 # Number animation on scroll
    Accordion/                    # Existing (preserved)
    Callouts/                     # Existing (preserved)
    CardGroup/                    # Existing (preserved)
    Steps/                        # Existing (preserved)
  hooks/
    useIntersectionObserver.ts    # Shared IO hook (single instance)
    useReducedMotion.ts           # prefers-reduced-motion detection
  pages/
    index.tsx                     # Landing page (11 sections, imports from sections/)
    index.module.css              # DELETED — styles move to per-section modules
    sections/                     # Landing page section components
      HeroSection.tsx
      HeroSection.module.css
      TrustedBySection.tsx
      TrustedBySection.module.css
      DemoVideoSection.tsx
      DemoVideoSection.module.css
      HowItWorksSection.tsx
      HowItWorksSection.module.css
      CapabilitiesSection.tsx
      CapabilitiesSection.module.css
      AcademyPromoSection.tsx
      AcademyPromoSection.module.css
      StatsSection.tsx
      StatsSection.module.css
      IntegrationsSection.tsx
      IntegrationsSection.module.css
      VerifiedSkillsSection.tsx
      VerifiedSkillsSection.module.css
      CTASection.tsx
      CTASection.module.css
      FooterSection.tsx           # NOT a section — handled via swizzle (see below)
  theme/                          # Docusaurus swizzle overrides
    BlogTagsPostsPage/            # Existing (preserved)
    MDXComponents.tsx             # Existing (preserved, extended with new components)
    NavbarItem/
      index.tsx                   # WRAP mode — extends default NavbarItem
    Footer/
      index.tsx                   # EJECT mode — full custom replacement
      Footer.module.css
```

**Key principle**: Each component owns its `.module.css`. No shared CSS module files between components. Tokens provide consistency via CSS custom properties, not via shared class names.

**Max 1500 lines per file**: The current `index.module.css` at ~1000 lines is already near the limit. Decomposing into per-section modules ensures no file exceeds 300 lines.

### 2. Token System Architecture

#### Current State

The existing `tokens.css` (211 lines) defines ~120 CSS custom properties organized into: colors (primary 50-900, semantic, neutral, surface, text, border), typography (2 font families, 9 sizes as static rem, 5 weights, 4 line heights), spacing (13 values on 4px grid), border radius (6 values), shadows (6 values), transitions (3 values), and Infima mappings.

Dark mode overrides exist in a `[data-theme='dark']` block covering primary palette inversion, semantic light variants, surfaces, text, and borders.

#### Target State (350+ tokens)

Expand to ~380 unique properties across light and dark modes by adding the following categories:

```
NEW CATEGORIES                          ESTIMATED PROPERTIES
--------------------------------------------------------------------
Fluid typography (clamp() display)      8 (display-1 through h6)
Letter spacing scale                    6 (tighter through widest)
Extended spacing (32-96px gaps)         4 (--sw-space-32/40/48/64)
Glass morphism shadows                  3 (glass-sm, glass-md, glass-lg)
Elevation shadows (1-5)                 5
Gradient definitions                    6 (primary, hero, cta, dark, accent, text)
Motion tokens                          8 (duration, easing, stagger-base, stagger-step)
Surface glass tokens                    3 (glass-bg, glass-border, glass-blur)
Z-index scale                           6 (base, dropdown, sticky, modal, overlay, max)
Grid tokens                             4 (columns, gutter, max-width, margin)
Color accent secondary                  5 (emerald accent for trust sections)

EXPANDED FROM EXISTING
--------------------------------------------------------------------
Primary palette                         remains 10 per mode = 20
Semantic colors                         add dark variants = +5
Neutral scale                           remains 10
Surface                                 add glass = +3
Text                                    remains 5
Border                                  add focus-ring = +1
Typography sizes                        replace static with clamp() for 5 display sizes
Shadows                                 add elevation + glass = +8
Transitions                             add spring = +1
```

**Token naming convention**: `--sw-{category}-{variant}` (established, maintained).

**Flow from tokens to components**:

```
tokens.css
  |
  +--> custom.css (@import tokens.css first line)
  |       |
  |       +--> Infima vars (--ifm-*) reference --sw-* tokens
  |       +--> Global element styles (.navbar, .card, etc.)
  |
  +--> animations.css (NEW — references motion tokens)
  |       |
  |       +--> @keyframes use --sw-motion-duration-* and --sw-motion-easing-*
  |       +--> .sw-animate-* utility classes for IntersectionObserver
  |
  +--> Component.module.css files
          |
          +--> Reference --sw-* tokens directly (var(--sw-color-primary-500))
          +--> NO intermediate CSS variables per component
          +--> Dark mode via [data-theme='dark'] .componentClass selectors
```

**Infima bridge strategy**: The existing Infima mapping section in `:root` continues to map `--ifm-*` to `--sw-*` tokens. This ensures default Docusaurus components (sidebar, navbar base, admonitions, code blocks) inherit the design system without swizzle. The dark mode `[data-theme='dark']` block overrides `--ifm-color-primary*` with appropriate dark palette values.

**New `custom.css` import order** (critical):
```css
@import './tokens.css';       /* Foundation — must be first */
@import './animations.css';   /* Keyframes — depends on motion tokens */
/* Rest of custom.css global overrides */
```

### 3. Animation System Architecture

#### Design Principles

1. **Zero bundle cost**: All animations defined as CSS @keyframes in `animations.css`. No Framer Motion, no GSAP.
2. **Progressive enhancement**: Content visible at `opacity: 1` by default (SSR-safe). Animation classes applied only after client-side hydration via `useEffect`.
3. **Accessibility**: All animations respect `prefers-reduced-motion: reduce` via a single media query guard.
4. **Performance**: Use `transform` and `opacity` only (GPU-composited properties). No `height`, `width`, or `top/left` animations.

#### Keyframe Definitions (animations.css)

```css
/* animations.css — extracted from component styles for single-source management */

/* Reduced motion guard — wraps ALL keyframe-triggered classes */
@media (prefers-reduced-motion: reduce) {
  .sw-animate-fade-up,
  .sw-animate-fade-in,
  .sw-animate-word,
  .sw-animate-marquee { /* etc. */
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}

/* Fade up (scroll reveal) */
@keyframes sw-fade-up {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Fade in (no movement) */
@keyframes sw-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* Word reveal stagger */
@keyframes sw-word-reveal {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Marquee infinite scroll (Trusted By) */
@keyframes sw-marquee {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}

/* Count pulse (subtle scale on number change) */
@keyframes sw-count-pulse {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.02); }
  100% { transform: scale(1); }
}

/* Glow pulse (hero background) */
@keyframes sw-glow-pulse {
  0%, 100% { opacity: 0.15; }
  50%      { opacity: 0.25; }
}
```

#### IntersectionObserver System

A single shared hook manages all scroll-triggered animations:

```
useIntersectionObserver.ts
  |
  +--> Creates ONE IntersectionObserver instance (threshold: 0.1)
  +--> Returns a ref callback
  +--> On intersect: adds CSS class, disconnects observer for that element
  +--> Respects prefers-reduced-motion (skip animation, show final state)
```

**AnimateOnScroll component** wraps any child and toggles a CSS class:

```
<AnimateOnScroll animation="fade-up" delay={200}>
  <FeatureCard ... />
</AnimateOnScroll>
```

Implementation:
1. Render children with `opacity: 0; transform: translateY(24px)` (initial state via CSS module)
2. On mount (`useEffect`), register element with IntersectionObserver
3. On intersect, add `.animated` class which triggers `animation: sw-fade-up 600ms ease-out forwards`
4. SSR fallback: if `typeof window === 'undefined'`, render with `.animated` class already applied (visible)

**WordAnimation component** splits text into `<span>` per word, each with staggered `animation-delay`:

```
<WordAnimation text="Ship Features While You Sleep" />
```

Each word gets `animation-delay: calc(var(--sw-motion-stagger-base) + var(--sw-motion-stagger-step) * N)`.

**CountUp component** uses `requestAnimationFrame` with ease-out interpolation:

```
<CountUp target={500} suffix="+" duration={2000} />
```

Triggers on IntersectionObserver entry. Uses `useReducedMotion` hook to skip animation and show final value immediately.

### 4. Docusaurus Swizzle Strategy

#### Components to Swizzle

| Component | Mode | Rationale |
|-----------|------|-----------|
| `NavbarItem` | **Wrap** | Extend default dropdown behavior with mega-menu panels. Preserves Docusaurus navbar logic (mobile hamburger, search, color mode toggle) |
| `Footer` | **Eject** | Full replacement needed for 4-column layout with social icons. Default Footer component structure too rigid |

#### NavbarItem Wrap Strategy

```
src/theme/NavbarItem/index.tsx
  |
  +--> Import original NavbarItem from @theme-original/NavbarItem
  +--> For items with `customProps.megaMenu === true`:
  |       +--> Render a MegaMenuPanel on hover/click
  |       +--> Panel content defined in docusaurus.config.ts customProps
  |       +--> 12-column grid layout inside the panel
  |       +--> Mobile: accordion-style within hamburger drawer
  +--> For all other items:
          +--> Pass through to original NavbarItem unchanged
```

**Why wrap, not eject**: The navbar has significant complexity (mobile drawer, search integration, color mode toggle, scroll behavior, announcement bar interaction). Ejecting would copy ~500 lines of Docusaurus internal code that changes between minor versions. Wrapping intercepts only the specific items that need mega-menu behavior.

**ARIA compliance**: The mega-menu panel implements `role="menu"`, `aria-haspopup="true"`, `aria-expanded`, focus trap within panel, Escape to close, arrow key navigation between menu items.

#### Footer Eject Strategy

```
src/theme/Footer/index.tsx
  |
  +--> Custom 4-column layout (Product, Docs, Community, Company)
  +--> Social icons row (GitHub, Discord, YouTube, X/Twitter)
  +--> Copyright line
  +--> Reads themeConfig.footer for link data (backward compatible)
  +--> Dark background always (not theme-dependent)
```

**Why eject, not wrap**: The default Footer renders a specific HTML structure (3-column with rigid CSS classes) that cannot be meaningfully extended by wrapping. A 4-column layout with social icons and the visual treatment specified requires full control.

#### Swizzle Maintenance Risk Mitigation

1. **Pin Docusaurus 3.9.x** in `package.json` (`"@docusaurus/core": "3.9.2"` — already pinned)
2. **Wrap over eject** wherever possible (only Footer is ejected)
3. **Minimal imports from internals**: Only import `@theme-original/NavbarItem`, not deep internal modules
4. **Document swizzled versions**: Add a comment header in each swizzled file noting the Docusaurus version it was swizzled from
5. **Upgrade checklist**: When upgrading Docusaurus, check:
   - `NavbarItem` — diff the original component for API changes
   - `Footer` — compare themeConfig.footer schema for breaking changes
6. **Docusaurus 4.0 migration**: The `future: { v4: true }` flag is already set in config. When 4.0 releases, swizzled components are the primary risk area. The wrap-mode NavbarItem should survive unless the NavbarItem API changes fundamentally. The ejected Footer will need a manual port.

### 5. Component Dependency Graph

```
tokens.css ──────────────────────────────────────┐
  |                                               |
  v                                               v
animations.css                               custom.css
  |                                               |
  v                                               v
useIntersectionObserver ◄── useReducedMotion   Infima vars
  |
  v
AnimateOnScroll ─────────┐
WordAnimation ──────────┐|
CountUp ───────────────┐||
  |                    |||
  v                    vvv
Icon ◄── Lucide React   |
  |                      |
  v                      v
Badge ──► Button     Section ──► SectionHeader
  |         |            |            |
  v         v            v            v
FeatureCard              HeroSection (Section + SectionHeader + WordAnimation + Button + Badge)
ContentCard              TrustedBySection (Section + Icon + CSS marquee)
StatCard ◄── CountUp     DemoVideoSection (Section + useIntersectionObserver)
IntegrationCard          HowItWorksSection (Section + SectionHeader + CodeBlock + AnimateOnScroll)
PricingCard              CapabilitiesSection (Section + SectionHeader + FeatureCard + AnimateOnScroll)
  |                      AcademyPromoSection (Section + SectionHeader + ContentCard + Badge)
  v                      StatsSection (Section + SectionHeader + StatCard + CountUp)
CodeBlock                IntegrationsSection (Section + SectionHeader + IntegrationCard)
                         VerifiedSkillsSection (Section + SectionHeader + Badge + Icon)
                         CTASection (Section + CodeBlock + Button)

NavbarItem (wrap) ──► MegaMenuPanel ──► Icon
Footer (eject) ──► Icon
Academy page ──► ContentCard + Badge
```

**Circular dependency prevention**: No component imports from a "higher" tier. The tiers are strictly: tokens -> hooks -> ui primitives -> layout -> cards -> animation wrappers -> sections -> pages.

### 6. Landing Page Section Architecture

The landing page (`pages/index.tsx`) becomes a thin orchestrator importing 11 section components:

```tsx
// pages/index.tsx — final structure
import Layout from '@theme/Layout';
import HeroSection from './sections/HeroSection';
import TrustedBySection from './sections/TrustedBySection';
import DemoVideoSection from './sections/DemoVideoSection';
import HowItWorksSection from './sections/HowItWorksSection';
import CapabilitiesSection from './sections/CapabilitiesSection';
import AcademyPromoSection from './sections/AcademyPromoSection';
import StatsSection from './sections/StatsSection';
import IntegrationsSection from './sections/IntegrationsSection';
import VerifiedSkillsSection from './sections/VerifiedSkillsSection';
import CTASection from './sections/CTASection';

export default function Home() {
  return (
    <Layout title="..." description="...">
      <HeroSection />
      <main>
        <TrustedBySection />
        <DemoVideoSection />
        <HowItWorksSection />
        <CapabilitiesSection />
        <AcademyPromoSection />
        <StatsSection />
        <IntegrationsSection />
        <VerifiedSkillsSection />
        <CTASection />
      </main>
    </Layout>
  );
}
```

#### Section-by-Section Breakdown

| # | Section | Variant | Key Components | Animation |
|---|---------|---------|----------------|-----------|
| 1 | Hero | Custom dark (full viewport) | WordAnimation, Button, Badge | Glow pulse, word reveal, pill fade-in |
| 2 | Trusted By | Default (light) | Icon (brand SVGs) | CSS-only marquee (no JS) |
| 3 | Demo Video | Dark | useIntersectionObserver | Lazy video load, play-on-visible |
| 4 | How It Works | Default (light) | SectionHeader, CodeBlock, AnimateOnScroll | Staggered fade-up per step |
| 5 | Capabilities | Default (light) | SectionHeader, FeatureCard, AnimateOnScroll | Staggered card reveals |
| 6 | Academy Promo | Dark | SectionHeader, ContentCard, Badge | Fade-up |
| 7 | Stats | Gradient | SectionHeader, StatCard, CountUp | Number animation on scroll |
| 8 | Integrations | Default (light) | SectionHeader, IntegrationCard | Staggered grid reveal |
| 9 | Verified Skills | Dark | SectionHeader, Badge, Icon | Fade-up |
| 10 | CTA | Gradient (violet) | CodeBlock, Button | Fade-in |
| 11 | Footer | N/A (swizzled) | Icon, Link | None |

#### Section Data Architecture

Section content (feature lists, stats values, integration data) is co-located with each section component as `const` arrays, not in a separate data file. Rationale: each section is self-contained; there is no data reuse across sections. This avoids an indirection layer that adds complexity without benefit for a static site.

### 7. Remotion Theme Alignment Strategy

The current Remotion video uses a separate theme (`remotion/lib/theme.ts`) with hardcoded colors:
- `purpleDark: '#0f0a1e'` (close to `--sw-surface-dark: #0b0816`)
- `purple: '#7c3aed'` (different from `--sw-color-primary-500: #6b58b8`)
- Resolution: 1280x720

#### Alignment Plan

1. **Update `remotion/lib/theme.ts`** to reference the same hex values as the expanded token system:
```ts
export const COLORS = {
  surfaceDark:    '#0b0816',  // --sw-surface-dark
  primary500:     '#6b58b8',  // --sw-color-primary-500
  primary400:     '#8f7dce',  // --sw-color-primary-400
  primary300:     '#b0a3de',  // --sw-color-primary-300
  primary200:     '#d1c9ed',  // --sw-color-primary-200
  success:        '#10b981',  // --sw-color-success
  danger:         '#ef4444',  // --sw-color-danger
  warning:        '#f59e0b',  // --sw-color-warning
  white:          '#ffffff',
  textSecondary:  '#94a3b8',  // --sw-gray-400
};

export const CONFIG = {
  width: 1920,    // UP from 1280
  height: 1080,   // UP from 720
  fps: 30,
  durationInFrames: 1350,
};
```

2. **Scale typography**: All Remotion scene font sizes multiplied by ~1.5x (proportional to resolution increase from 720p to 1080p). Exact values determined per scene.

3. **Replace inline SVG icons in scenes** with Lucide React equivalents where applicable. Remotion renders React components, so Lucide imports work directly.

4. **Gradient backgrounds**: Update scene backgrounds to use richer gradients matching the new token palette.

5. **Render script update** (`package.json`): Already renders both MP4 and WebM. No script change needed, only the resolution change in CONFIG.

**Remotion does NOT use CSS custom properties** (it runs in a separate Remotion Player context, not the Docusaurus DOM). Therefore, the theme file uses hardcoded hex values that must be manually kept in sync with `tokens.css`. A comment block in `theme.ts` cross-references each value to its `--sw-*` token name.

### 8. Build and Deployment Considerations

#### Build Pipeline

```
npm run build (docusaurus build)
  |
  +--> Compiles TSX/MDX to static HTML + JS bundles
  +--> CSS Modules compiled and hashed
  +--> tokens.css and animations.css included as global CSS
  +--> Lucide React tree-shaken (only imported icons in bundle)
  +--> Output: build/ directory
  |
npm run remotion:render (separate step, manual)
  |
  +--> Renders SpecWeaveHero composition at 1920x1080
  +--> Outputs: static/video/hero.mp4 + static/video/hero.webm
  +--> These are committed to the repo (static assets)
```

#### Performance Budget

| Metric | Target | Strategy |
|--------|--------|----------|
| Lighthouse Performance | 90+ | Lazy video, CSS-only animations, tree-shaken icons |
| Lighthouse Accessibility | 90+ | ARIA menubar, alt text, focus management, motion respect |
| Lighthouse Best Practices | 90+ | HTTPS, no mixed content, proper image formats |
| Lighthouse SEO | 90+ | Schema.org already present, meta tags, semantic HTML |
| First Contentful Paint | < 1.5s | No animation blocking render, content visible by default |
| Total Blocking Time | < 200ms | IntersectionObserver is non-blocking, no heavy JS |
| Cumulative Layout Shift | < 0.1 | Fixed dimensions on video, static section layouts |

#### New Dependency: Lucide React

```
lucide-react (tree-shakable)
  Bundle impact: ~200 bytes per icon (SVG paths only, no React wrapper overhead)
  Estimated usage: 20-25 icons across components
  Total cost: ~5KB gzipped
```

No other new runtime dependencies. The animation system uses only browser APIs (IntersectionObserver, requestAnimationFrame, CSS @keyframes).

#### Deployment

GitHub Pages (existing). No infrastructure changes. The `docusaurus build` output deploys as static files. Video files are committed to `static/video/` and served directly.

### 9. Risk Mitigation

#### Risk 1: Docusaurus Swizzle Breakage on Upgrade

**Probability**: Medium (Docusaurus 4.0 is coming)
**Impact**: High (broken navbar or footer)
**Mitigation**:
- Pin `@docusaurus/core` to `3.9.2` (already done)
- Use wrap mode for NavbarItem (survives most minor version changes)
- Eject only Footer (smallest surface area of the two options)
- `future: { v4: true }` flag already enabled for forward compatibility
- Document exact swizzle version in file headers
- Before upgrading: `npx docusaurus swizzle --list` to verify component API stability

#### Risk 2: IntersectionObserver Browser Compatibility

**Probability**: Low (supported in all modern browsers since 2019)
**Impact**: Low (graceful degradation — content just appears without animation)
**Mitigation**:
- Progressive enhancement: content visible by default, animations are additive
- Browserslist in `package.json` already targets `>0.5%, not dead`
- No polyfill needed; unsupported browsers simply see static content

#### Risk 3: CSS Custom Property Performance at 350+ Tokens

**Probability**: Very Low
**Impact**: None measurable
**Mitigation**:
- CSS custom properties are resolved at computed-value time, not on every frame
- No re-calculation unless a property actually changes (theme toggle is the only trigger)
- Docusaurus Infima already defines ~100 custom properties; adding 250 more is negligible

#### Risk 4: Monolithic Landing Page File Size

**Probability**: Medium (11 sections could bloat index.tsx)
**Impact**: Medium (maintenance burden, hard to review PRs)
**Mitigation**:
- Section components are self-contained files (150-250 lines each)
- `index.tsx` is a thin orchestrator (~40 lines)
- CSS modules are per-section (no single large CSS file)
- Max 1500 lines per file enforced

#### Risk 5: Remotion Theme Drift

**Probability**: Medium (manual sync between tokens.css and theme.ts)
**Impact**: Low (video colors slightly off from site)
**Mitigation**:
- Comment block in `theme.ts` maps each hex to its `--sw-*` token name
- Both files touched in the same increment, verified side-by-side
- Future: could add a build script to extract hex values from tokens.css, but not worth the complexity for this increment

#### Risk 6: Dark Mode Flash (FOUC)

**Probability**: Low (Docusaurus handles theme persistence via localStorage)
**Impact**: Medium (jarring visual flash on page load)
**Mitigation**:
- Docusaurus injects `data-theme` attribute before first paint via inline script
- All dark mode tokens use `[data-theme='dark']` selector (no JS-dependent class toggle)
- The `colorMode.respectPrefersColorScheme: true` config handles OS-level preference

## Technology Stack

- **Framework**: Docusaurus 3.9.2 (pinned)
- **Language**: TypeScript (strict, existing tsconfig)
- **Styling**: CSS Custom Properties + CSS Modules (no Tailwind, no CSS-in-JS)
- **Animation**: CSS @keyframes + IntersectionObserver + requestAnimationFrame
- **Icons**: Lucide React (new dependency, tree-shakable)
- **Video**: Remotion 4.x (existing, resolution upgrade only)
- **Fonts**: Inter via Google Fonts (existing)
- **Build**: Docusaurus CLI (existing)
- **Deploy**: GitHub Pages (existing)

**Architecture Decisions**:
- **CSS Custom Properties over Tailwind**: Infima uses CSS custom properties internally; adding Tailwind would create two competing property systems and require PostCSS configuration that conflicts with Docusaurus's built-in CSS pipeline. The token system provides the same consistency benefits without the tooling overhead.
- **CSS @keyframes over Framer Motion**: Framer Motion adds ~30KB to the JS bundle for functionality that CSS can handle natively. The animations in this redesign (fade, slide, scale) are all expressible as CSS @keyframes. The IntersectionObserver trigger is ~50 lines of custom hook code vs. adding a dependency.
- **Wrap over Eject for NavbarItem**: Docusaurus navbar internals are complex (~500 lines) and change between versions. Wrapping lets us intercept specific items for mega-menu treatment while preserving all default behavior (mobile drawer, search, scroll behavior).
- **Per-section CSS modules over shared stylesheet**: Prevents cascade conflicts, enables dead-code elimination per section, and keeps each file under the 1500-line limit.

## Implementation Phases

### Phase 1: Foundation (Tokens + Hooks + Animation System)
- Expand `tokens.css` to 350+ properties (fluid typography, motion, glass, elevation, gradients, grid)
- Create `animations.css` with all @keyframes definitions
- Build `useIntersectionObserver` and `useReducedMotion` hooks
- Build `AnimateOnScroll`, `WordAnimation`, `CountUp` animation components
- Update `custom.css` import order

### Phase 2: UI Primitives
- Build `Button` component (4 variants + disabled + dark mode)
- Build `Badge` component (5 variants + dark mode)
- Build `Icon` component (Lucide wrapper + brand SVG support)
- Build `CodeBlock` component (syntax highlight + copy-to-clipboard)
- Build `Divider` component
- Build `Section` component (4 variants + responsive padding)
- Build `SectionHeader` component (label + title + subtitle)

### Phase 3: Card Components
- Build `FeatureCard` (icon + title + description + hover shadow)
- Build `ContentCard` (image + tag + title + description + metadata)
- Build `StatCard` (large value + label + CountUp integration)
- Build `IntegrationCard` (logo + name + description)
- Build `PricingCard` (built for future use, not wired to a page)

### Phase 4: Landing Page Sections (1-5)
- Build `HeroSection` (full viewport dark, gradient text, WordAnimation, CTAs, pills)
- Build `TrustedBySection` (CSS-only logo marquee)
- Build `DemoVideoSection` (browser chrome frame, lazy load, play-on-visible)
- Build `HowItWorksSection` (horizontal timeline, 3 steps, CodeBlock examples)
- Build `CapabilitiesSection` (alternating left-right, 6 features, AnimateOnScroll)
- Refactor `pages/index.tsx` to import sections (delete monolithic `index.module.css`)

### Phase 5: Landing Page Sections (6-11)
- Build `AcademyPromoSection` (dark variant, 3 ContentCards, difficulty badges)
- Build `StatsSection` (4 StatCards with CountUp)
- Build `IntegrationsSection` (4-column grid, IntegrationCards)
- Build `VerifiedSkillsSection` (three-tier trust ladder visual)
- Build `CTASection` (violet gradient, install command CodeBlock, CTAs)

### Phase 6: Navigation Redesign
- Swizzle `NavbarItem` in wrap mode (mega-menu panels)
- Implement mega-menu panel component (12-column grid, categorized links)
- Mobile accordion adaptation for mega-menu
- ARIA menubar implementation (focus management, keyboard nav)
- Swizzle `Footer` in eject mode (4-column layout, social icons, copyright)

### Phase 7: Academy Enhancement
- Enhance academy index page with ContentCard grid
- Add frontmatter fields (reading_time, difficulty, prerequisites)
- Style difficulty badges (green/amber/purple via Badge variants)
- Mobile single-column collapse

### Phase 8: Remotion Video Overhaul
- Update `remotion/lib/theme.ts` (1920x1080, aligned colors)
- Scale typography across all 5 scenes (~1.5x)
- Replace inline SVG icons with Lucide React in scenes
- Enhance gradient backgrounds
- Render MP4 + WebM at 1920x1080

### Phase 9: Cross-Browser Polish and Accessibility
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Lighthouse audit and optimization (target 90+ all metrics)
- prefers-reduced-motion verification
- Screen reader testing (landmark roles, alt text, ARIA patterns)
- Viewport testing (320px to 2560px, no horizontal overflow, 44x44px touch targets)

## Testing Strategy

### Unit Tests (Vitest)
- Token count validation (parse tokens.css, assert >= 350 unique properties)
- Animation components: render with SSR simulation (no window), verify content visible
- CountUp: mock requestAnimationFrame, verify interpolation
- useReducedMotion: mock matchMedia, verify behavior
- Button/Badge/Card: snapshot tests for each variant
- CodeBlock: copy-to-clipboard mock

### Integration Tests
- Landing page render: verify all 11 sections present in DOM
- Dark mode toggle: verify token overrides apply
- Mega-menu: keyboard navigation, focus management
- IntersectionObserver: mock observer, verify class toggle

### E2E Tests (Playwright)
- Landing page scroll: verify animations trigger on scroll
- Mega-menu: hover open, keyboard navigate, escape close
- Mobile responsive: hamburger menu, section stacking
- Dark mode: toggle and verify no FOUC
- Video lazy load: scroll to video section, verify play begins
- Lighthouse CI: automated score assertions

### Accessibility Tests
- axe-core integration in Playwright
- Tab navigation through mega-menu
- Screen reader landmark verification

## Technical Challenges

### Challenge 1: Mega-Menu Focus Management
**Problem**: ARIA menubar pattern requires complex focus management (roving tabindex, arrow key navigation, escape to close) while coexisting with Docusaurus's own navbar keyboard handling.
**Solution**: Implement focus trap within the mega-menu panel component. Use `role="menubar"` on the nav, `role="menu"` on panels, `role="menuitem"` on links. Intercept keydown events only when a panel is open.
**Risk**: Potential conflict with Docusaurus's built-in keyboard handling for mobile drawer.
**Mitigation**: The wrap mode means our code only activates for mega-menu items. Standard navbar items retain Docusaurus default behavior entirely.

### Challenge 2: CSS Marquee Performance
**Problem**: The Trusted By section uses an infinite CSS scroll animation. On lower-end devices, continuous animation can cause jank.
**Solution**: Use `will-change: transform` on the marquee container and `transform: translateX()` (GPU-composited). The animation uses a duplicated set of logos for seamless looping without JS intervention.
**Risk**: `will-change` can consume GPU memory if applied too broadly.
**Mitigation**: Apply `will-change` only to the single marquee element, not globally.

### Challenge 3: Video Lazy Loading Without Layout Shift
**Problem**: The demo video section needs lazy loading with a poster frame, but loading the video after the poster can cause layout shift.
**Solution**: Set explicit `width` and `height` attributes (or `aspect-ratio: 16/9` in CSS) on the video container. The poster image fills the same dimensions. When the video loads, it replaces the poster with zero layout shift.
**Risk**: None significant — this is a standard pattern.

### Challenge 4: Fluid Typography and Infima Conflicts
**Problem**: Infima defines its own heading sizes via `--ifm-h1-font-size` etc. The new fluid typography system uses `clamp()` which could conflict.
**Solution**: Override Infima heading size variables in `tokens.css` to reference `clamp()` values. Only the landing page uses the fluid display sizes; docs pages continue using Infima defaults for their headings.
**Risk**: Unintended side effects on docs page headings.
**Mitigation**: The fluid display tokens (`--sw-font-size-display-*`) are separate from Infima heading tokens. Landing page sections use display tokens directly; Infima heading tokens are not overridden.
