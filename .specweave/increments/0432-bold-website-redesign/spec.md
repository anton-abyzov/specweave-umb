---
increment: 0432-bold-website-redesign
title: "Bold Website Redesign"
type: feature
priority: P1
status: active
created: 2026-03-05
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Bold Website Redesign

## Problem Statement

The SpecWeave website (spec-weave.com) currently presents a functional but visually modest Docusaurus site with ~200 CSS tokens, 4 custom components, static rem-based typography, and a basic 5-section landing page. This falls short of the professional quality bar set by best-in-class developer tool sites like Anthropic.com and Claude Code docs. For developers evaluating SpecWeave, engineering managers comparing tools, and enterprise buyers assessing maturity, the current site does not convey the sophistication of the product itself.

## Goals

- Establish a world-class design system foundation with 350+ tokens, fluid typography, and a 12-column CSS Grid system
- Build a 15-component library covering UI primitives, section wrappers, cards, and animation components
- Rewrite the landing page from 5 sections to 11 sections with professional scroll animations, gradient text, and Anthropic-inspired word-by-word reveals
- Redesign navigation with a mega-menu navbar and custom multi-column footer
- Enhance the academy index with metadata-rich course cards and skill-level badges
- Overhaul the Remotion video to 1920x1080 with aligned branding and professional SVG icons
- Achieve Lighthouse 90+ on all metrics with cross-browser, mobile, dark mode, and accessibility support

## User Personas

- **Developer** evaluating SpecWeave for their project -- needs to quickly understand value, see code examples, find docs
- **Engineering Manager** comparing tools for their team -- needs professional credibility signals, stats, integration proof
- **Existing User** looking for docs, academy, and references -- needs efficient navigation, clear information architecture
- **Enterprise Buyer** assessing professional quality and maturity -- needs polished visuals, trust signals, security info

## User Stories

### US-001: Design Token System Expansion
**Project**: specweave
**As a** developer working on the SpecWeave website
**I want** an expanded design token system with 350+ CSS custom properties covering colors, typography, spacing, shadows, motion, and glass morphism
**So that** all components share a consistent, maintainable visual language

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the tokens.css file, when inspected, then it contains organized token sections for: colors (primary 50-900, semantic, neutral, surface, text, border), typography (font families, fluid sizes, weights, line heights, letter spacing), spacing (4px grid 0-96px+), border radius, shadows (xs through glow plus elevation and glass morphism shadows), transitions (fast/base/slow/spring), and motion (duration, easing curves, stagger delays)
- [x] **AC-US1-02**: Given a dark mode toggle, when the user switches themes, then all surface, text, border, and shadow tokens update via [data-theme='dark'] overrides without flash of unstyled content
- [x] **AC-US1-03**: Given the token file, when the Infima mapping section is reviewed, then all --ifm-* variables correctly reference --sw-* tokens so Docusaurus default components inherit the design system
- [x] **AC-US1-04**: Given the token file, when counted, then there are at least 350 unique CSS custom properties defined across light and dark modes combined

---

### US-002: Fluid Typography System
**Project**: specweave
**As a** site visitor on any device
**I want** typography that scales fluidly between mobile and desktop viewport widths
**So that** headings and body text are always optimally sized without breakpoint jumps

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given display headings (hero title, section titles), when the viewport is resized from 375px to 1440px, then font sizes scale fluidly using CSS clamp() from a mobile minimum to a desktop maximum (display sizes ranging 48px to 80px)
- [x] **AC-US2-02**: Given body text and UI text, when the viewport is resized, then base font sizes remain readable at all widths with appropriate line-height adjustments
- [x] **AC-US2-03**: Given the typography token definitions, when reviewed, then they use clamp() functions referencing viewport units (e.g., clamp(3rem, 2.5rem + 2vw, 5rem)) rather than static rem values for display and heading sizes
- [x] **AC-US2-04**: Given the 12-column CSS Grid system, when a layout is viewed at any viewport width, then content respects max-width constraints and columns collapse gracefully on mobile

---

### US-003: UI Primitive Components
**Project**: specweave
**As a** developer building landing page sections
**I want** a set of reusable UI primitive components (Button, Badge, Icon, Divider, CodeBlock)
**So that** I can compose sections with consistent styling and behavior

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the Button component, when rendered with variant prop (primary, secondary, ghost, outline), then each variant displays correct colors, borders, hover/focus states, and disabled state using design tokens
- [x] **AC-US3-02**: Given the Badge component, when rendered with variant prop (default, success, warning, info, primary), then each displays the correct background, text color, and border-radius from tokens
- [x] **AC-US3-03**: Given the Icon component, when rendered with a Lucide icon name or a brand SVG slug, then it renders the correct SVG at the specified size with currentColor inheritance
- [x] **AC-US3-04**: Given the CodeBlock component, when rendered with code content and an optional copy button, then it displays syntax-highlighted code in a styled container with a one-click copy-to-clipboard action and visual feedback
- [x] **AC-US3-05**: Given any UI primitive, when rendered in dark mode, then all colors, borders, and shadows adapt correctly via token overrides

---

### US-004: Section Layout Components
**Project**: specweave
**As a** developer assembling landing page sections
**I want** Section wrapper and SectionHeader components with multiple layout variants
**So that** every section has consistent padding, max-width, and heading hierarchy

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the Section component, when rendered with variant prop (default, dark, gradient, accent), then the background, padding, and inner max-width are applied from tokens with correct light/dark mode behavior
- [x] **AC-US4-02**: Given the SectionHeader component, when rendered with label, title, and subtitle props, then it displays an uppercase label, a large title using fluid typography, and a muted subtitle paragraph beneath
- [x] **AC-US4-03**: Given a Section with variant="dark", when rendered, then the section uses --sw-surface-dark background with light text tokens and the SectionHeader label uses the primary accent color
- [x] **AC-US4-04**: Given sections on mobile viewport (375px), when viewed, then section vertical padding reduces proportionally and content stacks vertically

---

### US-005: Card Components
**Project**: specweave
**As a** developer populating content grids on the landing page
**I want** a set of card components (FeatureCard, ContentCard, StatCard, IntegrationCard, PricingCard)
**So that** content is presented in visually rich, consistent card layouts

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the FeatureCard component, when rendered with icon, title, and description props, then it displays a 64px icon area, bold title, and body text in a bordered card with hover shadow elevation
- [x] **AC-US5-02**: Given the ContentCard component, when rendered with image, tag, title, description, and link props, then it displays a card suitable for academy course listings with reading time and difficulty metadata
- [x] **AC-US5-03**: Given the StatCard component, when rendered with value, label, and optional suffix props, then it displays the value in a large display font with the label beneath, suitable for a stats section
- [x] **AC-US5-04**: Given the IntegrationCard component, when rendered with logo SVG, name, and description props, then it shows the integration logo at 48px, the integration name, and a short description in a card layout
- [x] **AC-US5-05**: Given any card component, when viewed in dark mode, then backgrounds use elevated surface tokens and borders use dark-mode border tokens

---

### US-006: Animation Components
**Project**: specweave
**As a** site visitor scrolling the landing page
**I want** smooth scroll-triggered animations and number counters
**So that** the page feels polished and professional without excessive loading weight

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the AnimateOnScroll component wrapping a child element, when the element enters the viewport (IntersectionObserver threshold 0.1), then it transitions from opacity 0 / translateY(24px) to opacity 1 / translateY(0) over 600ms with an ease-out curve
- [x] **AC-US6-02**: Given the WordAnimation component, when rendered with a text string, then it reveals words one at a time with staggered delays (Anthropic-style word-by-word), completing the full reveal within 2 seconds
- [x] **AC-US6-03**: Given the CountUp component, when its container scrolls into view, then it animates a number from 0 to the target value over 2 seconds using an ease-out interpolation
- [x] **AC-US6-04**: Given any animation component, when the user has prefers-reduced-motion enabled, then all animations are disabled and content displays immediately at its final state
- [x] **AC-US6-05**: Given SSR (Docusaurus build), when the page is server-rendered, then all animated content is visible by default (opacity: 1, no transform) and animations are only applied after client-side hydration via useEffect

---

### US-007: Landing Page Sections 1-5 (Hero through Capabilities)
**Project**: specweave
**As a** first-time visitor arriving at spec-weave.com
**I want** a visually striking hero, trusted-by marquee, demo video, how-it-works timeline, and capabilities showcase
**So that** I immediately understand what SpecWeave does and why it matters

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given the Hero section, when rendered, then it fills the full viewport height with a dark background, displays gradient text on the headline using WordAnimation, shows two CTAs (primary "Get Started" and secondary "Watch Demo"), and includes animated pill badges
- [x] **AC-US7-02**: Given the Trusted By section, when rendered, then it displays a horizontal logo marquee with CSS scroll animation (no JS) showing technology and community logos with seamless infinite loop
- [x] **AC-US7-03**: Given the Demo Video section, when rendered, then it shows the Remotion video inside a browser chrome frame with a glow shadow, using lazy loading with a poster frame and play-on-visible via IntersectionObserver
- [x] **AC-US7-04**: Given the How It Works section, when rendered, then it displays a horizontal timeline with 3 steps (64px numbered circles), each showing a command, title, description, and a CodeBlock example, connected by a progress line
- [x] **AC-US7-05**: Given the Capabilities section, when rendered, then it uses an alternating left-right layout showing 6 features with icons, titles, descriptions, and optional code snippets, each wrapped in AnimateOnScroll

---

### US-008: Landing Page Sections 6-11 (Academy through Footer)
**Project**: specweave
**As a** visitor evaluating SpecWeave for adoption
**I want** academy promotion, stats, integrations, verified skills, CTA, and footer sections
**So that** I see social proof, ecosystem breadth, and clear next steps

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given the Academy Promo section, when rendered, then it uses a dark variant with 3 ContentCards showing featured courses with reading time, difficulty badges, and links to the academy
- [x] **AC-US8-02**: Given the Stats section, when rendered, then it displays 4 StatCards with CountUp animations showing key metrics (e.g., skills count, autonomous hours, increments shipped, community size)
- [x] **AC-US8-03**: Given the Integrations section, when rendered, then it shows IntegrationCards in a 4-column grid for GitHub, JIRA, Azure DevOps, and Claude/Cursor/Copilot with logos and descriptions
- [x] **AC-US8-04**: Given the Verified Skills section, when rendered as a full-width section, then it displays the three-tier trust ladder (Scanned, Verified, Certified) with visual progression and link to verified-skill.com
- [x] **AC-US8-05**: Given the CTA section, when rendered, then it shows a violet gradient background, a compelling headline, a CodeBlock with the install command (including copy button), and primary/secondary CTA buttons

---

### US-009: Navigation Redesign (Mega-Menu and Footer)
**Project**: specweave
**As a** visitor navigating the site
**I want** a mega-menu navbar with rich dropdown panels and a custom multi-column footer
**So that** I can discover all site areas efficiently and the navigation matches the site's professional quality

**Acceptance Criteria**:
- [x] **AC-US9-01**: Given the navbar, when a top-level item (Docs, Skills, Learn) is hovered or clicked, then a mega-menu dropdown panel opens with a 12-column grid layout showing categorized links, descriptions, and optional featured content
- [x] **AC-US9-02**: Given the mega-menu implementation, when inspected, then it uses Docusaurus swizzle wrap mode for NavbarItem to extend (not replace) the default navbar behavior
- [x] **AC-US9-03**: Given the custom footer, when rendered, then it displays a 4-column layout (Product, Docs, Community, Company) with styled links, social icons, and copyright, implemented via Docusaurus swizzle eject mode for the Footer component
- [x] **AC-US9-04**: Given the mega-menu on mobile (viewport < 768px), when tapped, then dropdowns convert to an accordion-style expandable menu within the mobile hamburger drawer
- [x] **AC-US9-05**: Given keyboard navigation, when a user tabs through the mega-menu, then focus management follows ARIA menubar patterns with escape-to-close and arrow-key navigation within panels

---

### US-010: Academy Enhancement
**Project**: specweave
**As an** existing SpecWeave user exploring the academy
**I want** an enhanced academy index page with rich course cards showing metadata and skill-level badges
**So that** I can quickly find courses matching my experience level and time availability

**Acceptance Criteria**:
- [x] **AC-US10-01**: Given the academy index page, when rendered, then it displays courses as a grid of ContentCards showing title, description, estimated reading time, difficulty level (beginner/intermediate/advanced), and prerequisites
- [x] **AC-US10-02**: Given course metadata, when a course frontmatter includes reading_time, difficulty, and prerequisites fields, then the ContentCard renders these as styled badges and metadata line items
- [x] **AC-US10-03**: Given the difficulty badges, when rendered, then beginner shows green, intermediate shows amber, and advanced shows purple, using Badge component variants
- [x] **AC-US10-04**: Given the academy page on mobile, when viewed at 375px, then the card grid collapses to a single column with cards stacking vertically

---

### US-011: Remotion Video Overhaul
**Project**: specweave
**As a** visitor watching the demo video
**I want** a professional 1920x1080 video with updated branding, larger typography, and polished SVG icons
**So that** the video matches the redesigned site's visual quality

**Acceptance Criteria**:
- [x] **AC-US11-01**: Given the Remotion config, when inspected, then the video resolution is set to 1920x1080 (up from 1280x720)
- [x] **AC-US11-02**: Given the Remotion theme, when inspected, then colors reference the new token values (--sw-color-primary-500 equivalent hex values) and font sizes are scaled approximately 1.5x from current values
- [x] **AC-US11-03**: Given the video scenes, when rendered, then text elements use professional SVG icons from Lucide (replacing inline text elements where applicable) with richer gradient backgrounds
- [x] **AC-US11-04**: Given the rendered video, when exported, then both MP4 (H.264) and WebM (VP9) formats are produced and placed in static/video/
- [x] **AC-US11-05**: Given the remotion:render script, when executed, then it outputs both formats at 1920x1080 resolution

---

### US-012: Cross-Browser Polish and Accessibility
**Project**: specweave
**As a** site visitor using any modern browser, device, or assistive technology
**I want** the redesigned site to work flawlessly across browsers, viewports, color modes, and screen readers
**So that** no visitor encounters a broken or inaccessible experience

**Acceptance Criteria**:
- [ ] **AC-US12-01**: Given Chrome, Firefox, Safari, and Edge (latest 2 versions), when the landing page is loaded, then all sections render correctly without layout breaks, missing animations, or visual glitches
- [ ] **AC-US12-02**: Given a Lighthouse audit on the landing page, when run in production mode, then all four metrics (Performance, Accessibility, Best Practices, SEO) score 90 or above
- [ ] **AC-US12-03**: Given prefers-reduced-motion: reduce media query, when active, then all CSS @keyframes animations and JS-driven scroll animations are disabled, showing content in its final state
- [ ] **AC-US12-04**: Given a screen reader (VoiceOver, NVDA), when navigating the landing page, then all sections have appropriate landmark roles, images have alt text, interactive elements have accessible names, and the mega-menu follows ARIA patterns
- [ ] **AC-US12-05**: Given viewports from 320px to 2560px, when the landing page is resized, then no horizontal scrollbar appears, no content overflows, and touch targets meet 44x44px minimum

## Out of Scope

- **Tailwind CSS or CSS-in-JS adoption** -- staying with CSS Custom Properties to avoid Infima conflicts
- **Framer Motion or GSAP** -- using CSS @keyframes + IntersectionObserver for zero bundle cost animations
- **Migration off Docusaurus 3** -- too many docs pages; staying on 3.9.x and accepting manual 4.0 migration
- **CMS or headless content backend** -- all content remains in MDX/TSX files
- **Pricing page implementation** -- PricingCard component is built but no pricing page in this increment
- **Blog redesign** -- blog layout remains default Docusaurus
- **i18n / multi-language support** -- English only
- **CDN image optimization or Cloudflare Polish** -- GitHub Pages serves static files directly
- **Custom search UI redesign** -- existing search plugin retained as-is

## Technical Notes

### Architecture Decisions
- **CSS Custom Properties over Tailwind**: Avoids conflicts with Docusaurus Infima variables; all tokens live in tokens.css
- **CSS @keyframes + IntersectionObserver over Framer Motion**: Zero runtime JS bundle cost for animations; progressive enhancement via useEffect
- **Lucide React for icons**: Tree-shakable, 1000+ icons, consistent 24px grid
- **Inter font retained**: Already loaded via Google Fonts, used by best-in-class sites (Anthropic, Vercel)
- **Docusaurus swizzle strategy**: Navbar uses wrap mode (extend), Footer uses eject mode (replace)
- **Progressive enhancement for SSR**: All content visible by default (opacity: 1); animation classes added client-side via useEffect

### Dependencies
- Docusaurus 3.9.2 (pinned)
- Remotion 4.x (existing)
- Lucide React (new dependency)
- No new runtime CSS/animation libraries

### Constraints
- All SVGs for icons and logos (no raster images except video poster)
- Lazy-load video with poster frame, play on visible (IntersectionObserver)
- MP4 H.264 + WebM VP9 dual format for video
- Max 1500 lines per file -- extract components before exceeding

## Success Metrics

- **Lighthouse scores**: 90+ on Performance, Accessibility, Best Practices, SEO for landing page
- **Token count**: 350+ CSS custom properties in tokens.css
- **Component count**: 15 new reusable components in src/components/
- **Section count**: 11 landing page sections (up from 5)
- **Video resolution**: 1920x1080 (up from 1280x720)
- **Cross-browser**: No visual regressions on Chrome, Firefox, Safari, Edge (latest 2)
- **Mobile**: Fully responsive from 320px to 2560px with no horizontal overflow
- **Dark mode**: Complete token coverage, no unstyled flashes
- **Accessibility**: WCAG 2.1 AA compliance, ARIA menubar for mega-menu, prefers-reduced-motion support
