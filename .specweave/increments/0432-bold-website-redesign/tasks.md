---
increment: 0432-bold-website-redesign
title: "Bold Website Redesign"
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005, T-006, T-007, T-008]
  US-004: [T-009, T-010]
  US-005: [T-011, T-012, T-013, T-014]
  US-006: [T-015, T-016, T-017, T-018]
  US-007: [T-019, T-020, T-021, T-022, T-023]
  US-008: [T-024, T-025, T-026, T-027]
  US-009: [T-028, T-029, T-030]
  US-010: [T-031, T-032]
  US-011: [T-033, T-034]
  US-012: [T-035, T-036]
total_tasks: 36
completed: 23
---

# Tasks: Bold Website Redesign

---

## User Story: US-001 - Design Token System Expansion

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed

### T-001: Expand tokens.css to 350+ CSS Custom Properties

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `docs-site/src/css/tokens.css` file
- **When** the file is inspected programmatically
- **Then** it contains organized token sections for colors, fluid typography, spacing, border-radius, shadows (elevation + glass morphism), transitions, motion, gradient definitions, z-index scale, and grid tokens, plus the Infima mapping section where all `--ifm-*` variables reference `--sw-*` tokens, and the total unique property count is at least 350

**Test Cases**:
1. **Unit**: `docs-site/src/css/__tests__/tokens.test.ts`
   - testTokenCount(): Parse tokens.css and count unique `--sw-*` and `--ifm-*` properties; assert >= 350
   - testTokenSections(): Verify presence of required category comments (colors, typography, spacing, shadows, motion, grid, gradients, z-index)
   - testInfimaMappings(): Assert all `--ifm-color-primary*` vars reference `--sw-color-primary*` values
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/docs-site/src/css/tokens.css`
2. Add new token categories after existing sections: fluid typography clamp() display sizes (display-1 through h6), letter-spacing scale (6 values), extended spacing (--sw-space-32/40/48/64/80/96), glass morphism shadows (glass-sm/md/lg), elevation shadows (elevation-1 through elevation-5), gradient definitions (6: primary, hero, cta, dark, accent, text), motion tokens (duration-*, easing-*, stagger-base, stagger-step), surface glass tokens (glass-bg, glass-border, glass-blur), z-index scale (6 values), grid tokens (columns, gutter, max-width, margin), secondary accent colors (emerald, 5 values)
3. Add dark mode counterparts for new semantic tokens in `[data-theme='dark']` block
4. Ensure `--ifm-*` mappings reference `--sw-*` tokens
5. Run token count test to verify >= 350

---

### T-002: Create animations.css and Update custom.css Import Order

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a page with the `[data-theme='dark']` attribute applied
- **When** CSS custom properties are read via `getComputedStyle`
- **Then** all surface, text, border, and shadow tokens reflect dark-mode values, and the `animations.css` @keyframes are available globally via the updated `custom.css` import order

**Test Cases**:
1. **Unit**: `docs-site/src/css/__tests__/animations.test.ts`
   - testKeyframeNames(): Assert animations.css exports sw-fade-up, sw-fade-in, sw-word-reveal, sw-marquee, sw-count-pulse, sw-glow-pulse keyframes
   - testImportOrder(): Assert custom.css imports tokens.css first, then animations.css
   - **Coverage Target**: 85%

2. **E2E**: `docs-site/e2e/dark-mode.spec.ts`
   - testDarkModeNoFOUC(): Toggle theme, verify no flash of unstyled content; check that `--sw-surface-*` resolves to dark value
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Create `repositories/anton-abyzov/specweave/docs-site/src/css/animations.css` with @keyframes: sw-fade-up, sw-fade-in, sw-word-reveal, sw-marquee, sw-count-pulse, sw-glow-pulse
2. Add `@media (prefers-reduced-motion: reduce)` guard at top disabling all `.sw-animate-*` classes
3. Add utility classes `.sw-animate-fade-up`, `.sw-animate-fade-in`, `.sw-animate-word`, `.sw-animate-marquee` that apply corresponding keyframes
4. Update `custom.css`: move `@import './tokens.css'` to first line, add `@import './animations.css'` as second line

---

## User Story: US-002 - Fluid Typography System

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 2 completed

### T-003: Implement Fluid Typography Tokens with clamp()

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** the typography token definitions in `tokens.css`
- **When** the display and heading size tokens are inspected
- **Then** they use `clamp()` functions referencing viewport units (e.g., `clamp(3rem, 2.5rem + 2vw, 5rem)`) for display-1 through h4, covering the 48px to 80px range for display sizes

**Test Cases**:
1. **Unit**: `docs-site/src/css/__tests__/tokens.test.ts`
   - testFluidTypographyClamp(): Parse tokens.css, find all `--sw-font-size-display-*` and `--sw-font-size-h*` tokens, assert each value contains `clamp(` with a `vw` unit
   - testTypographyRange(): For `--sw-font-size-display-1`, assert min >= 3rem and max >= 5rem (matching 48px-80px spec)
   - **Coverage Target**: 90%

2. **E2E**: `docs-site/e2e/typography.spec.ts`
   - testFluidScaling(): At 375px viewport, assert hero title font-size >= 48px and <= 56px; at 1440px, assert >= 72px
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. In tokens.css, replace static rem values for display-1 through h4 with clamp() expressions:
   - `--sw-font-size-display-1: clamp(3rem, 2.5rem + 2.5vw, 5rem)` (48-80px)
   - `--sw-font-size-display-2: clamp(2.5rem, 2rem + 2vw, 4rem)` (40-64px)
   - `--sw-font-size-h1: clamp(2rem, 1.75rem + 1.25vw, 3rem)` (32-48px)
   - `--sw-font-size-h2: clamp(1.5rem, 1.25rem + 1vw, 2.25rem)` (24-36px)
2. Retain static rem values for h5, h6, body, small (no scaling needed)
3. Add letter-spacing tokens: --sw-letter-spacing-tighter through --sw-letter-spacing-widest

---

### T-004: Implement 12-Column CSS Grid System

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** a Section component rendered in a browser
- **When** the layout is viewed at any viewport width from 375px to 1440px
- **Then** content respects the max-width constraint from `--sw-grid-max-width`, uses column-based gap from `--sw-grid-gutter`, and collapses correctly on mobile

**Test Cases**:
1. **Unit**: `docs-site/src/css/__tests__/tokens.test.ts`
   - testGridTokens(): Assert tokens.css contains --sw-grid-columns, --sw-grid-gutter, --sw-grid-max-width, --sw-grid-margin
   - **Coverage Target**: 85%

2. **E2E**: `docs-site/e2e/layout.spec.ts`
   - testNoHorizontalOverflow(): At 375px viewport, assert `document.body.scrollWidth <= window.innerWidth`
   - testMaxWidth(): At 1440px, assert main content container width <= 1280px (or the configured max-width)
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Add grid tokens to tokens.css: `--sw-grid-columns: 12`, `--sw-grid-gutter: 24px`, `--sw-grid-max-width: 1280px`, `--sw-grid-margin: 24px`
2. Add responsive grid margin override in `@media (min-width: 1024px)`: `--sw-grid-margin: 48px`
3. Add `.sw-container` utility class in custom.css: `max-width: var(--sw-grid-max-width)`, `padding-inline: var(--sw-grid-margin)`, `margin-inline: auto`

---

## User Story: US-003 - UI Primitive Components

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 4 total, 4 completed

### T-005: Build Button Component (4 Variants + Dark Mode)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** the Button component rendered with each variant (primary, secondary, ghost, outline)
- **When** inspected in both light and dark mode
- **Then** each variant displays correct colors, borders, hover/focus states, and disabled state using design tokens; in dark mode, all colors adapt via token overrides

**Test Cases**:
1. **Unit**: `docs-site/src/components/ui/Button/__tests__/Button.test.tsx`
   - testPrimaryVariant(): Render Button with variant="primary", assert className includes primary style
   - testSecondaryVariant(): Render Button with variant="secondary", assert expected class applied
   - testGhostVariant(): Render Button with variant="ghost", assert correct class
   - testOutlineVariant(): Render Button with variant="outline", assert correct class
   - testDisabledState(): Render Button with disabled prop, assert aria-disabled and visual class
   - testHoverState(): Simulate hover, assert focus-visible styles present
   - **Coverage Target**: 95%

2. **Integration**: `docs-site/src/components/ui/Button/__tests__/Button.integration.test.tsx`
   - testButtonClick(): Render Button, simulate click, assert onClick called
   - testButtonAsLink(): Render Button with href prop, assert rendered as anchor
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/ui/Button/index.tsx` with props: `variant: 'primary' | 'secondary' | 'ghost' | 'outline'`, `size: 'sm' | 'md' | 'lg'`, `href?: string`, `disabled?: boolean`, `onClick?: () => void`, `children: ReactNode`
2. Create `docs-site/src/components/ui/Button/Button.module.css` with `.btn`, `.primary`, `.secondary`, `.ghost`, `.outline` classes using `var(--sw-*)` tokens
3. Add hover/focus states using CSS `:hover`, `:focus-visible` selectors
4. Add `[data-theme='dark'] .primary` etc. overrides for dark mode
5. Add disabled state with `opacity: 0.5; cursor: not-allowed`

---

### T-006: Build Badge and Icon Components

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** the Badge component rendered with each variant (default, success, warning, info, primary)
- **When** inspected
- **Then** each displays the correct background, text color, and border-radius from tokens; and the Icon component renders the correct Lucide SVG at the specified size with currentColor inheritance

**Test Cases**:
1. **Unit**: `docs-site/src/components/ui/Badge/__tests__/Badge.test.tsx`
   - testDefaultVariant(): Render Badge variant="default", assert rendered with default style class
   - testSuccessVariant(): Assert success class applied
   - testWarningVariant(): Assert warning class applied
   - testInfoVariant(): Assert info class applied
   - testPrimaryVariant(): Assert primary class applied
   - **Coverage Target**: 95%

2. **Unit**: `docs-site/src/components/ui/Icon/__tests__/Icon.test.tsx`
   - testLucideIcon(): Render Icon with name="check", assert SVG rendered
   - testBrandIcon(): Render Icon with brand="github", assert brand SVG rendered
   - testSizeInheritance(): Render Icon with size={32}, assert width/height attribute = 32
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/ui/Badge/index.tsx` with variants: default, success, warning, info, primary
2. Create `docs-site/src/components/ui/Badge/Badge.module.css` using `var(--sw-color-*)` tokens
3. Add dark mode overrides for Badge in CSS module
4. Install lucide-react: `cd repositories/anton-abyzov/specweave/docs-site && npm install lucide-react`
5. Create `docs-site/src/components/ui/Icon/index.tsx` that imports named Lucide icons dynamically and renders brand SVGs from `brands/` directory
6. Create `docs-site/src/components/ui/Icon/brands/` directory with github.svg, jira.svg, azure.svg, claude.svg, cursor.svg, copilot.svg

---

### T-007: Build CodeBlock Component with Copy Button

**User Story**: US-003
**Satisfies ACs**: AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** the CodeBlock component rendered with code content
- **When** the user clicks the copy button
- **Then** the code is copied to clipboard and the button shows visual feedback (checkmark icon) for 2 seconds; the component renders correctly in dark mode

**Test Cases**:
1. **Unit**: `docs-site/src/components/ui/CodeBlock/__tests__/CodeBlock.test.tsx`
   - testRendersCode(): Render CodeBlock with code="npm install", assert code text visible
   - testCopyButton(): Mock clipboard API, click copy button, assert writeText called with code value
   - testCopyFeedback(): After click, assert button shows confirmation state for 2 seconds
   - testDarkMode(): Render with data-theme="dark" on parent, assert background uses dark token
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/ui/CodeBlock/index.tsx` with props: `code: string`, `language?: string`, `showCopy?: boolean`
2. Implement copy-to-clipboard using `navigator.clipboard.writeText()`
3. Track copied state with `useState` + `useEffect` timeout reset after 2000ms
4. Show Lucide `Check` icon when copied, `Copy` icon otherwise
5. Create `docs-site/src/components/ui/CodeBlock/CodeBlock.module.css` with pre/code styling using `var(--sw-*)` tokens for bg, border, text colors
6. Add dark mode overrides

---

### T-008: Build Divider Component

**User Story**: US-003
**Satisfies ACs**: AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** the Divider component rendered
- **When** inspected in light and dark mode
- **Then** it renders an `<hr>` styled with border-color from `--sw-border-*` tokens, adapting correctly in dark mode

**Test Cases**:
1. **Unit**: `docs-site/src/components/ui/Divider/__tests__/Divider.test.tsx`
   - testRenders(): Render Divider, assert hr element present in DOM
   - testVariants(): Render with variant="subtle" and variant="strong", assert different class applied
   - **Coverage Target**: 85%

**Implementation**:
1. Create `docs-site/src/components/ui/Divider/index.tsx` with props: `variant?: 'subtle' | 'strong'`, `orientation?: 'horizontal' | 'vertical'`
2. Create `docs-site/src/components/ui/Divider/Divider.module.css` using `var(--sw-border-*)` tokens
3. Add dark mode overrides via `[data-theme='dark']` selector

---

## User Story: US-004 - Section Layout Components

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 2 completed

### T-009: Build Section Component (4 Variants + Responsive Padding)

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** the Section component rendered with each variant (default, dark, gradient, accent)
- **When** inspected at both desktop (1440px) and mobile (375px) viewport widths
- **Then** the correct background and inner max-width are applied; variant="dark" uses `--sw-surface-dark` background with light text; on mobile, vertical padding reduces proportionally

**Test Cases**:
1. **Unit**: `docs-site/src/components/layout/Section/__tests__/Section.test.tsx`
   - testDefaultVariant(): Render Section, assert default class applied to wrapper
   - testDarkVariant(): Render Section variant="dark", assert dark class applied
   - testGradientVariant(): Render Section variant="gradient", assert gradient class applied
   - testAccentVariant(): Render Section variant="accent", assert accent class applied
   - testChildrenRendered(): Render Section with children, assert children visible in output
   - **Coverage Target**: 90%

2. **E2E**: `docs-site/e2e/sections.spec.ts`
   - testMobileStacking(): At 375px, assert section padding-top and padding-bottom are less than desktop values
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Create `docs-site/src/components/layout/Section/index.tsx` with props: `variant?: 'default' | 'dark' | 'gradient' | 'accent'`, `children: ReactNode`, `className?: string`, `id?: string`
2. Create `docs-site/src/components/layout/Section/Section.module.css` with `.section`, `.dark`, `.gradient`, `.accent` classes
3. Inner container with `max-width: var(--sw-grid-max-width)` and `padding-inline: var(--sw-grid-margin)`
4. Responsive padding: `padding-block: var(--sw-space-16)` on mobile, `var(--sw-space-24)` on tablet, `var(--sw-space-32)` on desktop
5. `.dark` variant: `background: var(--sw-surface-dark); color: var(--sw-text-on-dark)`

---

### T-010: Build SectionHeader Component

**User Story**: US-004
**Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** the SectionHeader component rendered with label, title, and subtitle props
- **When** inspected
- **Then** it displays an uppercase label in primary accent color, a large fluid-typography title, and a muted subtitle paragraph; in a dark section context, the label uses the primary accent color

**Test Cases**:
1. **Unit**: `docs-site/src/components/layout/SectionHeader/__tests__/SectionHeader.test.tsx`
   - testRendersLabel(): Render with label="Features", assert uppercase text visible
   - testRendersTitle(): Render with title="Ship Faster", assert h2 contains text
   - testRendersSubtitle(): Render with subtitle="Build better", assert paragraph visible
   - testOptionalSubtitle(): Render without subtitle, assert no empty paragraph rendered
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/layout/SectionHeader/index.tsx` with props: `label?: string`, `title: string`, `subtitle?: string`, `centered?: boolean`
2. Create `docs-site/src/components/layout/SectionHeader/SectionHeader.module.css`
3. Label: `text-transform: uppercase; letter-spacing: var(--sw-letter-spacing-widest); color: var(--sw-color-primary-500); font-size: var(--sw-font-size-sm); font-weight: var(--sw-font-weight-semibold)`
4. Title: `font-size: var(--sw-font-size-h2); font-weight: var(--sw-font-weight-bold)`
5. Subtitle: `color: var(--sw-text-secondary); font-size: var(--sw-font-size-lg)`

---

## User Story: US-005 - Card Components

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 4 total, 4 completed

### T-011: Build FeatureCard and StatCard Components

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-03, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the FeatureCard component rendered with icon, title, and description props
- **When** hovered in light and dark mode
- **Then** it displays a 64px icon area, bold title, body text, bordered card with hover shadow elevation; StatCard displays the value in a large display font with label beneath; both adapt correctly in dark mode

**Test Cases**:
1. **Unit**: `docs-site/src/components/cards/FeatureCard/__tests__/FeatureCard.test.tsx`
   - testRendersIcon(): Render FeatureCard with icon="Zap", assert Icon component present
   - testRendersTitle(): Render with title="Fast", assert title text in DOM
   - testRendersDescription(): Render with description="Speed matters", assert text visible
   - testHoverClass(): Simulate mouse enter, assert hover class or style changes
   - **Coverage Target**: 90%

2. **Unit**: `docs-site/src/components/cards/StatCard/__tests__/StatCard.test.tsx`
   - testRendersValue(): Render StatCard with value="500", assert value text visible
   - testRendersLabel(): Render with label="Skills", assert label text visible
   - testRendersSuffix(): Render with suffix="+", assert suffix appended
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/cards/FeatureCard/index.tsx` with props: `icon: string`, `title: string`, `description: string`, `className?: string`
2. Create `docs-site/src/components/cards/FeatureCard/FeatureCard.module.css`: icon area 64x64px, border `1px solid var(--sw-border-default)`, hover: `box-shadow: var(--sw-shadow-md); border-color: var(--sw-color-primary-300)`
3. Create `docs-site/src/components/cards/StatCard/index.tsx` with props: `value: string | number`, `label: string`, `suffix?: string`
4. Create `docs-site/src/components/cards/StatCard/StatCard.module.css`: value uses `var(--sw-font-size-display-2)`, bold weight
5. Add dark mode overrides for both cards using `[data-theme='dark']`

---

### T-012: Build ContentCard Component

**User Story**: US-005
**Satisfies ACs**: AC-US5-02, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the ContentCard component rendered with image, tag, title, description, and link props including reading_time and difficulty
- **When** inspected
- **Then** it displays a card suitable for academy course listings with reading time and difficulty metadata rendered as styled elements; dark mode adapts via elevated surface tokens

**Test Cases**:
1. **Unit**: `docs-site/src/components/cards/ContentCard/__tests__/ContentCard.test.tsx`
   - testRendersTitle(): Render ContentCard with title="Intro to SpecWeave", assert title visible
   - testRendersTag(): Render with tag="Beginner", assert tag text in DOM
   - testRendersReadingTime(): Render with readingTime="5 min", assert reading time visible
   - testRendersLink(): Render with href="/academy/intro", assert anchor with href present
   - testDarkMode(): With dark theme, assert background uses elevated surface class
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/cards/ContentCard/index.tsx` with props: `title: string`, `description: string`, `tag?: string`, `readingTime?: string`, `difficulty?: 'beginner' | 'intermediate' | 'advanced'`, `href: string`, `image?: string`
2. Create `docs-site/src/components/cards/ContentCard/ContentCard.module.css`: card layout with image area at top, metadata row with reading time and difficulty badge, title, description, link
3. Import Badge component for difficulty badge
4. Add dark mode overrides using elevated surface token

---

### T-013: Build IntegrationCard Component

**User Story**: US-005
**Satisfies ACs**: AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the IntegrationCard component rendered with logo SVG slug, name, and description
- **When** inspected in light and dark mode
- **Then** it shows the integration logo at 48px, the integration name, and a short description in a card layout; dark mode uses elevated surface and dark border tokens

**Test Cases**:
1. **Unit**: `docs-site/src/components/cards/IntegrationCard/__tests__/IntegrationCard.test.tsx`
   - testRendersLogo(): Render IntegrationCard with brand="github", assert Icon brand rendered
   - testRendersName(): Render with name="GitHub", assert name text visible
   - testRendersDescription(): Render with description="Source control", assert description visible
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/cards/IntegrationCard/index.tsx` with props: `brand: string`, `name: string`, `description: string`, `href?: string`
2. Create `docs-site/src/components/cards/IntegrationCard/IntegrationCard.module.css`: brand logo 48x48px area, name in semibold, description in secondary text color
3. Import Icon component for brand logo rendering
4. Add dark mode overrides

---

### T-014: Build PricingCard Component

**User Story**: US-005
**Satisfies ACs**: AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the PricingCard component rendered with plan, price, features, and CTA props
- **When** inspected in light and dark mode
- **Then** it renders a complete pricing card structure; dark mode uses elevated surface tokens

**Test Cases**:
1. **Unit**: `docs-site/src/components/cards/PricingCard/__tests__/PricingCard.test.tsx`
   - testRendersPlan(): Render PricingCard with plan="Pro", assert plan name visible
   - testRendersPrice(): Render with price="$29", assert price text visible
   - testRendersFeatures(): Render with features array, assert all feature items visible
   - testHighlighted(): Render with highlighted prop, assert highlighted class applied
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/cards/PricingCard/index.tsx` with props: `plan: string`, `price: string`, `period?: string`, `features: string[]`, `cta: string`, `href: string`, `highlighted?: boolean`
2. Create `docs-site/src/components/cards/PricingCard/PricingCard.module.css`
3. Note: component is built but not wired to any page in this increment (per out-of-scope spec)
4. Add dark mode overrides

---

## User Story: US-006 - Animation Components

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Tasks**: 4 total, 4 completed

### T-015: Build Shared Hooks (useIntersectionObserver + useReducedMotion)

**User Story**: US-006
**Satisfies ACs**: AC-US6-04, AC-US6-05
**Status**: [x] completed

**Test Plan**:
- **Given** the `useReducedMotion` hook
- **When** called in an environment where `window.matchMedia('(prefers-reduced-motion: reduce)').matches` is true
- **Then** it returns `true`; when false, returns `false`; and `useIntersectionObserver` returns a ref callback that, when an element enters the viewport, adds the animated class and disconnects the observer for that element

**Test Cases**:
1. **Unit**: `docs-site/src/hooks/__tests__/useReducedMotion.test.ts`
   - testReducedMotionTrue(): Mock matchMedia to return true, assert hook returns true
   - testReducedMotionFalse(): Mock matchMedia to return false, assert hook returns false
   - testSSRSafe(): In environment without window, assert hook returns false without error
   - **Coverage Target**: 95%

2. **Unit**: `docs-site/src/hooks/__tests__/useIntersectionObserver.test.ts`
   - testCallbackOnIntersect(): Mock IntersectionObserver, trigger intersection, assert callback called
   - testDisconnectsAfterIntersect(): After intersection, assert observer.unobserve called on element
   - testSSRSafe(): In environment without window.IntersectionObserver, assert no error thrown
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/hooks/useReducedMotion.ts`: use `window.matchMedia('(prefers-reduced-motion: reduce)')` with SSR guard (`typeof window === 'undefined'` returns false)
2. Create `docs-site/src/hooks/useIntersectionObserver.ts`: returns a `ref` callback; on intersection, calls provided `onIntersect` callback and unobserves the element; threshold: 0.1; SSR guard

---

### T-016: Build AnimateOnScroll Component

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-04, AC-US6-05
**Status**: [x] completed

**Test Plan**:
- **Given** the AnimateOnScroll component wrapping a child element
- **When** the element enters the viewport (IntersectionObserver threshold 0.1)
- **Then** it transitions from opacity 0 / translateY(24px) to opacity 1 / translateY(0) over 600ms; prefers-reduced-motion disables animation and shows final state immediately; SSR renders content visible by default

**Test Cases**:
1. **Unit**: `docs-site/src/components/animation/AnimateOnScroll/__tests__/AnimateOnScroll.test.tsx`
   - testSSRVisible(): Render without window, assert child rendered with opacity 1 (no hidden initial state)
   - testInitialHidden(): In browser environment, assert wrapper has initial hidden class before intersection
   - testAnimatedOnIntersect(): Mock IO, trigger intersection, assert animated class added
   - testReducedMotion(): With prefers-reduced-motion=reduce, assert animated class applied immediately on mount
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/animation/AnimateOnScroll/index.tsx` with props: `children: ReactNode`, `animation?: 'fade-up' | 'fade-in'`, `delay?: number`, `className?: string`
2. In `useEffect`, register element with `useIntersectionObserver`; check `useReducedMotion` - if true, skip animation class toggling and show content immediately
3. SSR fallback: if `typeof window === 'undefined'`, render with final visible state
4. Create `docs-site/src/components/animation/AnimateOnScroll/AnimateOnScroll.module.css`: `.initial { opacity: 0; transform: translateY(24px) }`, `.animated { animation: sw-fade-up 600ms ease-out forwards }`

---

### T-017: Build WordAnimation Component

**User Story**: US-006
**Satisfies ACs**: AC-US6-02, AC-US6-04, AC-US6-05
**Status**: [x] completed

**Test Plan**:
- **Given** the WordAnimation component rendered with a text string of 5 words
- **When** it mounts in the browser
- **Then** it reveals words one at a time with staggered delays, completing the full reveal within 2 seconds; prefers-reduced-motion shows all words immediately; SSR renders all words visible

**Test Cases**:
1. **Unit**: `docs-site/src/components/animation/WordAnimation/__tests__/WordAnimation.test.tsx`
   - testSplitsIntoWords(): Render with text="Hello World Now", assert 3 span elements rendered
   - testStaggeredDelays(): Assert each word span has increasing animation-delay inline style
   - testReducedMotion(): With prefers-reduced-motion, assert no animation-delay applied
   - testSSRAllVisible(): SSR render, assert all word spans visible (no opacity: 0)
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/animation/WordAnimation/index.tsx` with props: `text: string`, `className?: string`
2. Split text by spaces, render each word as `<span>` with `animation-delay: calc(var(--sw-motion-stagger-base) + var(--sw-motion-stagger-step) * N)`
3. In browser, apply animation class via `useEffect`; check `useReducedMotion`
4. Create `docs-site/src/components/animation/WordAnimation/WordAnimation.module.css`: `.word { display: inline-block; animation: sw-word-reveal 400ms ease-out forwards; opacity: 0 }`

---

### T-018: Build CountUp Component

**User Story**: US-006
**Satisfies ACs**: AC-US6-03, AC-US6-04, AC-US6-05
**Status**: [x] completed

**Test Plan**:
- **Given** the CountUp component with target={500} and duration={2000}
- **When** its container scrolls into view
- **Then** it animates from 0 to 500 over 2 seconds using ease-out interpolation; prefers-reduced-motion shows final value immediately; SSR renders the final value

**Test Cases**:
1. **Unit**: `docs-site/src/components/animation/CountUp/__tests__/CountUp.test.tsx`
   - testSSRShowsTarget(): SSR render with target=500, assert "500" in DOM
   - testReducedMotionShowsTarget(): With prefers-reduced-motion, assert target value shown immediately without animation
   - testAnimatesOnIntersect(): Mock IO and rAF, trigger intersection, assert count progresses from 0 toward target
   - testSuffixAppended(): Render with target=500, suffix="+", assert "500+" in final state
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/components/animation/CountUp/index.tsx` with props: `target: number`, `duration?: number`, `suffix?: string`, `prefix?: string`
2. Use `useIntersectionObserver` to trigger animation start
3. Animate using `requestAnimationFrame` with ease-out interpolation: `value = target * (1 - Math.pow(1 - progress, 3))`
4. `useReducedMotion`: if true, set to target immediately on intersect
5. SSR: render target value directly

---

## User Story: US-007 - Landing Page Sections 1-5

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Tasks**: 5 total, 0 completed

### T-019: Build HeroSection

**User Story**: US-007
**Satisfies ACs**: AC-US7-01
**Status**: [x] completed

**Test Plan**:
- **Given** the HeroSection component rendered
- **When** inspected in a browser at full viewport height
- **Then** it fills the full viewport height with a dark background, the headline uses WordAnimation and gradient text, two CTAs are present (primary "Get Started" and secondary "Watch Demo"), and animated pill badges are visible

**Test Cases**:
1. **Unit**: `docs-site/src/pages/sections/__tests__/HeroSection.test.tsx`
   - testFullViewportHeight(): Render HeroSection, assert wrapper has min-height: 100vh style or class
   - testCTAsPresent(): Assert "Get Started" and "Watch Demo" buttons in DOM
   - testWordAnimation(): Assert WordAnimation component rendered with headline text
   - testPillBadges(): Assert badge pill elements present
   - **Coverage Target**: 90%

2. **E2E**: `docs-site/e2e/landing.spec.ts`
   - testHeroRendered(): Navigate to homepage, assert hero section visible above fold
   - testHeroGradientText(): Assert hero title element has gradient text styling
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Create `docs-site/src/pages/sections/HeroSection.tsx`
2. Structure: full-viewport dark section, glow background orb (CSS), pill badges row (2-3 badge components), headline with `<WordAnimation>`, subheading paragraph, CTA row with primary Button ("Get Started") and ghost Button ("Watch Demo")
3. Create `docs-site/src/pages/sections/HeroSection.module.css`: `.hero { min-height: 100vh; background: var(--sw-surface-dark); display: flex; align-items: center }`, gradient text via `background-clip: text; -webkit-background-clip: text; color: transparent; background-image: var(--sw-gradient-text)`
4. Glow pulse via `sw-glow-pulse` keyframe on an absolutely positioned orb div

---

### T-020: Build TrustedBySection and DemoVideoSection

**User Story**: US-007
**Satisfies ACs**: AC-US7-02, AC-US7-03
**Status**: [x] completed

**Test Plan**:
- **Given** the TrustedBySection rendered
- **When** inspected
- **Then** a horizontal logo marquee with CSS-only scroll animation (no JS) is visible with duplicated logos for seamless looping; the DemoVideoSection shows the video in a browser chrome frame with glow shadow and lazy loading via IntersectionObserver

**Test Cases**:
1. **Unit**: `docs-site/src/pages/sections/__tests__/TrustedBySection.test.tsx`
   - testMarqueePresent(): Assert marquee container with CSS animation class present
   - testLogosPresent(): Assert at least 4 brand Icon components rendered
   - testDuplicatedForLoop(): Assert logos rendered twice (for seamless CSS loop)
   - **Coverage Target**: 85%

2. **Unit**: `docs-site/src/pages/sections/__tests__/DemoVideoSection.test.tsx`
   - testVideoElement(): Assert video element present with poster attribute
   - testBrowserChrome(): Assert browser chrome frame wrapper element present
   - testLazyLoad(): Assert video has loading="lazy" or is controlled by IO hook
   - **Coverage Target**: 85%

**Implementation**:
1. Create `docs-site/src/pages/sections/TrustedBySection.tsx`: two sets of logos duplicated, wrapper with `overflow: hidden`, inner track with `animation: sw-marquee 30s linear infinite`
2. Create `docs-site/src/pages/sections/TrustedBySection.module.css`: `will-change: transform` on marquee track, `@media (prefers-reduced-motion: reduce) { animation: none }`
3. Create `docs-site/src/pages/sections/DemoVideoSection.tsx`: browser chrome div (header bar with traffic light dots), video element with `src`, `poster`, `aspect-ratio: 16/9`, `muted`, `loop`, `playsInline`; use `useIntersectionObserver` to call `video.play()` when visible
4. Create `docs-site/src/pages/sections/DemoVideoSection.module.css`: browser chrome styling, `box-shadow: var(--sw-shadow-glow)`

---

### T-021: Build HowItWorksSection

**User Story**: US-007
**Satisfies ACs**: AC-US7-04
**Status**: [x] completed

**Test Plan**:
- **Given** the HowItWorksSection rendered
- **When** inspected
- **Then** it displays a horizontal timeline with 3 steps using 64px numbered circles, each showing a command, title, description, and CodeBlock example, connected by a progress line; each step is wrapped in AnimateOnScroll

**Test Cases**:
1. **Unit**: `docs-site/src/pages/sections/__tests__/HowItWorksSection.test.tsx`
   - testThreeSteps(): Render, assert 3 step containers present
   - testNumberedCircles(): Assert elements with step numbers 1, 2, 3 visible
   - testCodeBlockPerStep(): Assert 3 CodeBlock components rendered
   - testAnimateOnScrollWrapping(): Assert AnimateOnScroll wrapper around each step
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/pages/sections/HowItWorksSection.tsx`: SectionHeader + 3-column grid, each column has numbered circle (64x64px), step title, description, CodeBlock with example command
2. Steps content: (1) "Describe" - `/sw:increment "feature"`, (2) "Build" - `/sw:do`, (3) "Ship" - `/sw:done 0001`
3. Progress line: absolutely positioned horizontal line connecting circles via CSS
4. Wrap each step in `<AnimateOnScroll delay={N * 150}>`
5. Create `docs-site/src/pages/sections/HowItWorksSection.module.css`

---

### T-022: Build CapabilitiesSection

**User Story**: US-007
**Satisfies ACs**: AC-US7-05
**Status**: [x] completed

**Test Plan**:
- **Given** the CapabilitiesSection rendered
- **When** inspected
- **Then** it shows 6 features in an alternating left-right layout with icons, titles, descriptions, and optional code snippets; each feature block is wrapped in AnimateOnScroll

**Test Cases**:
1. **Unit**: `docs-site/src/pages/sections/__tests__/CapabilitiesSection.test.tsx`
   - testSixFeatures(): Render, assert 6 capability block containers
   - testAlternatingLayout(): Assert even and odd items have different CSS classes for left/right positioning
   - testAnimateOnScroll(): Assert AnimateOnScroll present for each capability
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/pages/sections/CapabilitiesSection.tsx`: SectionHeader + array of 6 feature objects (icon, title, description, optional code snippet); map to alternating row layouts
2. Each row: 2-column grid with text side and code/visual side; even rows reverse order
3. Wrap each row in `<AnimateOnScroll>`
4. Create `docs-site/src/pages/sections/CapabilitiesSection.module.css`

---

### T-023: Refactor pages/index.tsx to Import Sections 1-5

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Status**: [x] completed

**Test Plan**:
- **Given** the refactored `pages/index.tsx` with sections 1-5
- **When** rendered
- **Then** it imports and renders HeroSection, TrustedBySection, DemoVideoSection, HowItWorksSection, and CapabilitiesSection; the file is under 60 lines

**Test Cases**:
1. **Unit**: `docs-site/src/pages/__tests__/index.test.tsx`
   - testFirstFiveSectionsPresent(): Render Home component, assert Hero, TrustedBy, DemoVideo, HowItWorks, Capabilities sections in DOM
   - **Coverage Target**: 85%

**Implementation**:
1. Begin refactoring `docs-site/src/pages/index.tsx` to import and render the first 5 section components
2. Move any inline styles or shared styles to per-section CSS modules
3. Delete `docs-site/src/pages/index.module.css` after migrating all styles (or defer until T-027 completes)
4. Verify `npm run build` compiles without errors for the partial refactor

---

## User Story: US-008 - Landing Page Sections 6-11

**Linked ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05
**Tasks**: 4 total, 0 completed

### T-024: Build AcademyPromoSection and StatsSection

**User Story**: US-008
**Satisfies ACs**: AC-US8-01, AC-US8-02
**Status**: [x] completed

**Test Plan**:
- **Given** the AcademyPromoSection rendered
- **When** inspected
- **Then** it uses Section variant="dark" with 3 ContentCards showing featured courses with reading time, difficulty badges, and links; the StatsSection displays 4 StatCard components with CountUp animations triggered on scroll

**Test Cases**:
1. **Unit**: `docs-site/src/pages/sections/__tests__/AcademyPromoSection.test.tsx`
   - testDarkVariant(): Assert Section with variant="dark" in DOM
   - testThreeContentCards(): Assert 3 ContentCard components rendered
   - testDifficultyBadges(): Assert Badge components with difficulty values present
   - **Coverage Target**: 90%

2. **Unit**: `docs-site/src/pages/sections/__tests__/StatsSection.test.tsx`
   - testFourStatCards(): Assert 4 StatCard components rendered
   - testCountUpComponents(): Assert CountUp components within StatsSection
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/pages/sections/AcademyPromoSection.tsx`: Section variant="dark", SectionHeader, 3-column ContentCard grid with hardcoded course data (title, description, readingTime, difficulty, href)
2. Create `docs-site/src/pages/sections/AcademyPromoSection.module.css`
3. Create `docs-site/src/pages/sections/StatsSection.tsx`: Section variant="gradient", SectionHeader, 4-column StatCard grid: skills count (~500+), autonomous hours (~10K+), increments shipped (~25K+), community (~2K+)
4. Wrap each StatCard in AnimateOnScroll; integrate CountUp component inside StatCard for value animation
5. Create `docs-site/src/pages/sections/StatsSection.module.css`

---

### T-025: Build IntegrationsSection and VerifiedSkillsSection

**User Story**: US-008
**Satisfies ACs**: AC-US8-03, AC-US8-04
**Status**: [x] completed

**Test Plan**:
- **Given** the IntegrationsSection rendered
- **When** inspected
- **Then** it shows IntegrationCards in a 4-column grid for GitHub, JIRA, Azure DevOps, and AI tools with logos and descriptions; the VerifiedSkillsSection displays the three-tier trust ladder with visual progression and link to verified-skill.com

**Test Cases**:
1. **Unit**: `docs-site/src/pages/sections/__tests__/IntegrationsSection.test.tsx`
   - testFourIntegrationCards(): Assert 4 IntegrationCard components rendered
   - testGitHubCard(): Assert card with brand="github" present
   - testJiraCard(): Assert card with brand="jira" present
   - **Coverage Target**: 90%

2. **Unit**: `docs-site/src/pages/sections/__tests__/VerifiedSkillsSection.test.tsx`
   - testThreeTiers(): Assert 3 tier containers (Scanned, Verified, Certified) present
   - testVerifiedSkillLink(): Assert anchor with href containing "verified-skill.com" present
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/pages/sections/IntegrationsSection.tsx`: Section variant="default", SectionHeader, 4-column grid of IntegrationCards (GitHub, JIRA, Azure DevOps, Claude/Cursor/Copilot); wrap in AnimateOnScroll
2. Create `docs-site/src/pages/sections/VerifiedSkillsSection.tsx`: Section variant="dark", three-tier visual (Scanned to Verified to Certified) with icon, heading, description for each tier, visual progression arrow between tiers, CTA link to verified-skill.com
3. Create CSS modules for both sections

---

### T-026: Build CTASection

**User Story**: US-008
**Satisfies ACs**: AC-US8-05
**Status**: [x] completed

**Test Plan**:
- **Given** the CTASection rendered
- **When** inspected
- **Then** it shows a violet gradient background, a compelling headline, a CodeBlock with the install command (with copy button), and primary/secondary CTA buttons

**Test Cases**:
1. **Unit**: `docs-site/src/pages/sections/__tests__/CTASection.test.tsx`
   - testGradientBackground(): Assert section has gradient variant class or inline gradient style
   - testInstallCommand(): Assert CodeBlock with "npx" or "npm" content
   - testCopyButton(): Assert CodeBlock rendered with showCopy prop
   - testCTAButtons(): Assert primary and secondary Button components present
   - **Coverage Target**: 90%

**Implementation**:
1. Create `docs-site/src/pages/sections/CTASection.tsx`: Section with violet gradient background (inline style using `--sw-gradient-cta`), centered SectionHeader, CodeBlock with `npx specweave init` command and showCopy, row of Buttons: primary ("Get Started Free") and ghost ("View on GitHub")
2. Create `docs-site/src/pages/sections/CTASection.module.css`

---

### T-027: Complete pages/index.tsx with All 10 Sections

**User Story**: US-008
**Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05
**Status**: [x] completed

**Test Plan**:
- **Given** the final `pages/index.tsx`
- **When** a full build is run (`npm run build`)
- **Then** it compiles without errors and the built HTML contains all 10 section components rendered in sequence

**Test Cases**:
1. **Integration**: `docs-site/src/pages/__tests__/index.test.tsx`
   - testAllTenSectionsPresent(): Render Home, assert AcademyPromo, Stats, Integrations, VerifiedSkills, and CTA section wrappers present alongside sections 1-5
   - **Coverage Target**: 85%

2. **E2E**: `docs-site/e2e/landing.spec.ts`
   - testAllSectionsVisible(): Scroll full page, assert each of 10 sections enters viewport
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Add imports for AcademyPromoSection, StatsSection, IntegrationsSection, VerifiedSkillsSection, CTASection to `pages/index.tsx`
2. Insert all 5 sections in order after CapabilitiesSection in JSX
3. Delete `index.module.css` if not already done in T-023
4. Run `npm run build` in docs-site to confirm no compilation errors

---

## User Story: US-009 - Navigation Redesign

**Linked ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04, AC-US9-05
**Tasks**: 3 total, 3 completed

### T-028: Swizzle NavbarItem in Wrap Mode with Mega-Menu

**User Story**: US-009
**Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-04, AC-US9-05
**Status**: [x] completed

**Test Plan**:
- **Given** the swizzled NavbarItem component loaded in a browser
- **When** a top-level item with `customProps.megaMenu === true` is hovered or clicked
- **Then** a mega-menu dropdown opens with a 12-column grid showing categorized links; on mobile (< 768px), the dropdown converts to accordion-style; keyboard navigation follows ARIA menubar patterns (Escape to close, arrow keys within panel)

**Test Cases**:
1. **Unit**: `docs-site/src/theme/NavbarItem/__tests__/NavbarItem.test.tsx`
   - testPassthroughNonMegaMenu(): Render NavbarItem without megaMenu prop, assert original NavbarItem rendered
   - testMegaMenuOpens(): Render NavbarItem with megaMenu prop, simulate hover/click, assert panel visible
   - testMegaMenuCloses(): After open, press Escape key, assert panel hidden
   - testAriaExpanded(): When open, assert `aria-expanded="true"` on trigger element
   - **Coverage Target**: 90%

2. **E2E**: `docs-site/e2e/navigation.spec.ts`
   - testMegaMenuDesktop(): Hover nav item, assert mega-menu panel appears
   - testMegaMenuKeyboard(): Tab to nav item, press Enter, assert panel opens; press Escape, assert closes
   - testMegaMenuMobile(): At 375px, tap nav item, assert accordion panel expands
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Run swizzle: `cd repositories/anton-abyzov/specweave/docs-site && npx docusaurus swizzle @docusaurus/theme-classic NavbarItem --wrap`
2. Edit `src/theme/NavbarItem/index.tsx`: import `@theme-original/NavbarItem`, intercept items with `customProps.megaMenu === true`
3. Create `MegaMenuPanel` component: `role="menu"`, `aria-haspopup="true"`, 12-column CSS grid, categorized link sections
4. Implement focus management: `role="menubar"` on nav, focus trap within panel, Escape closes, arrow keys navigate between items
5. Mobile adaptation: at `max-width: 768px`, render accordion-style panel instead of floating panel
6. Update `docusaurus.config.ts` to add `customProps.megaMenu: true` and panel content to relevant navbar items

---

### T-029: Swizzle Footer in Eject Mode with 4-Column Layout

**User Story**: US-009
**Satisfies ACs**: AC-US9-03
**Status**: [x] completed

**Test Plan**:
- **Given** the ejected custom Footer component loaded on any page
- **When** rendered
- **Then** it displays a 4-column layout (Product, Docs, Community, Company) with styled links, social icon row (GitHub, Discord, YouTube, X/Twitter), and copyright text; the dark background is applied regardless of theme

**Test Cases**:
1. **Unit**: `docs-site/src/theme/Footer/__tests__/Footer.test.tsx`
   - testFourColumns(): Render Footer, assert 4 column headings: Product, Docs, Community, Company
   - testSocialIcons(): Assert 4 social icon links (GitHub, Discord, YouTube, Twitter)
   - testCopyright(): Assert copyright text visible with current year
   - testDarkBackground(): Assert footer wrapper has dark background class
   - **Coverage Target**: 90%

**Implementation**:
1. Run swizzle: `npx docusaurus swizzle @docusaurus/theme-classic Footer --eject`
2. Replace `src/theme/Footer/index.tsx` with custom implementation: 4-column grid (Product, Docs, Community, Company), each column with heading and link list
3. Social icons row: GitHub, Discord, YouTube, X using Icon component with brand SVGs
4. Copyright: `© {new Date().getFullYear()} SpecWeave. All rights reserved.`
5. Background: always dark (`var(--sw-surface-dark)`)
6. Create `src/theme/Footer/Footer.module.css`

---

### T-030: Add Version Header Comments to Swizzled Files

**User Story**: US-009
**Satisfies ACs**: AC-US9-02
**Status**: [x] completed

**Test Plan**:
- **Given** both swizzled component files (NavbarItem and Footer)
- **When** opened
- **Then** each has a comment header noting the Docusaurus version (3.9.2) it was swizzled from, the swizzle mode (wrap/eject), and upgrade verification instructions

**Test Cases**:
1. **Unit**: `docs-site/src/theme/__tests__/swizzleHeaders.test.ts`
   - testNavbarItemHeader(): Read NavbarItem/index.tsx, assert first comment block contains "3.9.2" and "wrap"
   - testFooterHeader(): Read Footer/index.tsx, assert first comment block contains "3.9.2" and "eject"
   - **Coverage Target**: 85%

**Implementation**:
1. Add header comment to `src/theme/NavbarItem/index.tsx`: `/* Swizzled from @docusaurus/theme-classic@3.9.2 -- WRAP mode. On upgrade: npx docusaurus swizzle --list to verify NavbarItem API stability. */`
2. Add header comment to `src/theme/Footer/index.tsx`: `/* Swizzled from @docusaurus/theme-classic@3.9.2 -- EJECT mode. On upgrade, compare themeConfig.footer schema for breaking changes and port manually. */`

---

## User Story: US-010 - Academy Enhancement

**Linked ACs**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04
**Tasks**: 2 total, 0 completed

### T-031: Enhance Academy Index with ContentCard Grid

**User Story**: US-010
**Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-04
**Status**: [x] completed

**Test Plan**:
- **Given** the enhanced academy index page rendered
- **When** inspected at both desktop and 375px mobile viewport
- **Then** courses display as a grid of ContentCards showing title, description, reading time, difficulty level, and prerequisites; on mobile, the grid collapses to a single column

**Test Cases**:
1. **Unit**: `docs-site/src/pages/__tests__/academy.test.tsx`
   - testContentCardsRendered(): Render academy index, assert ContentCard components present
   - testMetadataVisible(): Assert reading time and difficulty visible on each card
   - testPrerequisitesVisible(): Assert prerequisites field rendered when present
   - **Coverage Target**: 90%

2. **E2E**: `docs-site/e2e/academy.spec.ts`
   - testMobileSingleColumn(): At 375px, assert card grid has 1 column
   - testDesktopGrid(): At 1200px, assert card grid has 2+ columns
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Locate academy index page (likely `docs-site/docs/academy/index.mdx` or equivalent)
2. Convert to TSX or add custom component for card grid rendering
3. Add frontmatter fields to academy course files: `reading_time`, `difficulty`, `prerequisites`
4. Render ContentCard grid in academy index; pass metadata from frontmatter to cards
5. CSS: grid collapses to `grid-template-columns: 1fr` at `max-width: 640px`

---

### T-032: Style Difficulty Badges (Green/Amber/Purple)

**User Story**: US-010
**Satisfies ACs**: AC-US10-03
**Status**: [x] completed

**Test Plan**:
- **Given** the difficulty badge on an academy ContentCard
- **When** the difficulty is beginner, intermediate, or advanced
- **Then** the Badge component renders green for beginner, amber for intermediate, and purple for advanced

**Test Cases**:
1. **Unit**: `docs-site/src/components/cards/ContentCard/__tests__/ContentCard.test.tsx`
   - testBeginnerBadge(): Render ContentCard with difficulty="beginner", assert Badge with variant="success" (green)
   - testIntermediateBadge(): Render with difficulty="intermediate", assert Badge with variant="warning" (amber)
   - testAdvancedBadge(): Render with difficulty="advanced", assert Badge with variant="primary" (purple)
   - **Coverage Target**: 90%

**Implementation**:
1. Update ContentCard component to map difficulty to Badge variant: `beginner -> success`, `intermediate -> warning`, `advanced -> primary`
2. Confirm Badge CSS module has correct colors: `.success { background: var(--sw-color-success-light); color: var(--sw-color-success) }`, `.warning { background: var(--sw-color-warning-light); color: var(--sw-color-warning) }`, `.primary { background: var(--sw-color-primary-100); color: var(--sw-color-primary-700) }`

---

## User Story: US-011 - Remotion Video Overhaul

**Linked ACs**: AC-US11-01, AC-US11-02, AC-US11-03, AC-US11-04, AC-US11-05
**Tasks**: 2 total, 2 completed

### T-033: Update Remotion Theme to 1920x1080 with Aligned Colors

**User Story**: US-011
**Satisfies ACs**: AC-US11-01, AC-US11-02, AC-US11-03
**Status**: [x] completed

**Test Plan**:
- **Given** the updated `remotion/lib/theme.ts`
- **When** inspected
- **Then** CONFIG.width is 1920, CONFIG.height is 1080, all color values match the `--sw-*` token hex equivalents documented in comments, font sizes are scaled ~1.5x from previous values, and Lucide React icons replace inline SVG elements in at least 2 scenes

**Test Cases**:
1. **Unit**: `docs-site/remotion/__tests__/theme.test.ts`
   - testResolution(): Import theme CONFIG, assert width === 1920 and height === 1080
   - testColorValues(): Assert COLORS.surfaceDark === '#0b0816', COLORS.primary500 === '#6b58b8'
   - testColorComments(): Read theme.ts file content, assert each color has a comment referencing --sw-* token name
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/docs-site/remotion/lib/theme.ts` (or equivalent path)
2. Update CONFIG: `width: 1920, height: 1080`
3. Update COLORS to match plan.md values with inline comments: `surfaceDark: '#0b0816', // --sw-surface-dark` etc.
4. Scale all font sizes in scene components by ~1.5x (find and update each scene file)
5. Replace inline SVG elements with Lucide React imports in at least 2 scenes
6. Update gradient backgrounds in scene files to use richer multi-stop gradients matching new token palette

---

### T-034: Render Video at 1920x1080 (MP4 + WebM)

**User Story**: US-011
**Satisfies ACs**: AC-US11-04, AC-US11-05
**Status**: [x] completed

**Test Plan**:
- **Given** the updated render script executed via `npm run remotion:render`
- **When** it completes
- **Then** both `static/video/hero.mp4` (H.264) and `static/video/hero.webm` (VP9) exist in the output directory at 1920x1080 resolution

**Test Cases**:
1. **Unit**: `docs-site/remotion/__tests__/renderConfig.test.ts`
   - testRenderScriptMP4(): Check package.json remotion:render script includes mp4 output flag
   - testRenderScriptWebM(): Check package.json remotion:render script includes webm output flag
   - testOutputDirectory(): Assert render script targets `static/video/` directory
   - **Coverage Target**: 85%

2. **Manual Verification**: Run `npm run remotion:render` and verify output files at correct resolution

**Implementation**:
1. Verify `package.json` remotion:render script renders both MP4 (H.264) and WebM (VP9) at 1920x1080
2. If script only renders one format, update to render both formats with appropriate codec flags
3. Run the render script (manual step, takes several minutes)
4. Commit the output video files to `static/video/`

---

## User Story: US-012 - Cross-Browser Polish and Accessibility

**Linked ACs**: AC-US12-01, AC-US12-02, AC-US12-03, AC-US12-04, AC-US12-05
**Tasks**: 2 total, 0 completed

### T-035: Lighthouse Audit and Cross-Browser Performance Verification

**User Story**: US-012
**Satisfies ACs**: AC-US12-01, AC-US12-02, AC-US12-05
**Status**: [ ] pending

**Test Plan**:
- **Given** the redesigned landing page in a production build
- **When** a Lighthouse audit is run and the page is tested in Chrome, Firefox, Safari, and Edge (latest 2 versions)
- **Then** all four Lighthouse metrics (Performance, Accessibility, Best Practices, SEO) score 90+; no layout breaks appear across browsers; no horizontal scrollbar at any viewport from 320px to 2560px; touch targets meet 44x44px minimum

**Test Cases**:
1. **E2E**: `docs-site/e2e/lighthouse.spec.ts`
   - testLighthousePerformance(): Run Lighthouse CI against production build, assert score >= 90
   - testLighthouseAccessibility(): Assert accessibility score >= 90
   - testLighthouseBestPractices(): Assert best practices score >= 90
   - testLighthouseSEO(): Assert SEO score >= 90
   - **Coverage Target**: 100% of AC scenarios

2. **E2E**: `docs-site/e2e/viewport.spec.ts`
   - testNoHorizontalScroll320(): At 320px, assert `document.body.scrollWidth <= window.innerWidth`
   - testNoHorizontalScroll2560(): At 2560px, assert no overflow
   - testTouchTargetSize(): Assert all interactive elements have min bounding box of 44x44px
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Run `npm run build` and serve locally with `npm run serve`
2. Run Lighthouse CI and check scores; fix any Performance issues (lazy video, tree-shaken icons, no render-blocking resources)
3. Fix any Accessibility issues found (missing alt text, landmark roles, color contrast)
4. Test cross-browser: open landing page in Chrome, Firefox, Safari, Edge; verify no layout breaks
5. Test viewports 320px-2560px: assert no horizontal overflow
6. Verify buttons and links have min 44x44px clickable area

---

### T-036: Reduced Motion and Screen Reader Accessibility

**User Story**: US-012
**Satisfies ACs**: AC-US12-03, AC-US12-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the landing page with `prefers-reduced-motion: reduce` active
- **When** the page is loaded and a screen reader (VoiceOver/NVDA) navigates it
- **Then** all CSS @keyframes and JS-driven scroll animations are disabled showing content in final state; all sections have appropriate landmark roles; images have alt text; interactive elements have accessible names; the mega-menu follows ARIA menubar patterns

**Test Cases**:
1. **E2E**: `docs-site/e2e/accessibility.spec.ts`
   - testReducedMotionDisablesAnimations(): Set prefers-reduced-motion media query, assert no opacity: 0 elements on landing page after load
   - testLandmarkRoles(): Assert `<main>`, `<nav>`, `<footer>` landmark elements present
   - testImagesHaveAlt(): Assert all `<img>` elements have non-empty alt attributes
   - testInteractiveElementsAccessible(): Assert all buttons have accessible name (aria-label or text content)
   - testMegaMenuARIA(): Assert mega-menu trigger has `aria-haspopup`, panel has `role="menu"`, items have `role="menuitem"`
   - testAxeNoViolations(): Run axe-core against landing page, assert 0 violations
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Verify animations.css `@media (prefers-reduced-motion: reduce)` guard covers all animation utility classes
2. Verify all AnimateOnScroll, WordAnimation, CountUp components check `useReducedMotion` hook and skip animations
3. Audit HTML: add `<main>` wrapper around landing page content, verify `<nav>` and `<footer>` present
4. Add alt text to any images/SVGs used as images (use `aria-hidden="true"` for decorative SVGs)
5. Ensure all Button components have text content or aria-label
6. Install and configure axe-core Playwright integration: `npm install --save-dev @axe-core/playwright`
7. Add axe scan to accessibility E2E test; fix any violations found
