---
increment: 0424-homepage-redesign
architect: sw-architect
created: 2026-03-04
---

# Architecture Plan: Redesign vskill Platform Homepage

## Overview

Frontend-only redesign of the vskill platform homepage. All components remain
Next.js server components consuming existing `getHomeStats()` data. No new API
routes, no new npm dependencies. Eight files modified or created across five
user stories.

---

## Component Map

```
page.tsx (homepage)
│
├── Hero Section (restructured in-place)
│   ├── Row 1: Heading
│   ├── Row 2: Subtitle + inline security callout
│   ├── Row 3: HeroSearchInput (full-width)
│   └── Row 4: CTAs + stats
│
├── <PipelineFlow stats={stats} />              (NEW)
│   └── 4 linked steps: Authors → Submitted → Scanned → Published
│
├── <MarketDashboard stats={stats} />           (modified)
│   └── <MetricCard href description linkLabel />  (enhanced)
│       └── Equal-height via flex container
│
├── <CategoryDistribution categories={...} />   (rewritten)
│   └── HTML divs with <Link> wrappers (was SVG)
│
├── <TrendingSkills ... />                      (moved after categories)
│
└── Trust section                               (moved last)
```

---

## Architecture Decisions

### 1. Server components throughout — no client conversion

All modified and new components remain server components. Navigation uses
Next.js `<Link>` which works in server components. Category hover states use
CSS `:hover` pseudo-classes in globals.css rather than `onMouseEnter`/
`onMouseLeave` event handlers, avoiding the need for `"use client"`.

### 2. Equal-height cards via CSS flexbox, not fixed minHeight

The metric card grid container uses `display: flex` with `align-items: stretch`
(or CSS grid with `grid-auto-rows: 1fr`). Each `MetricCard` sets `height: 100%`
on its outer element. This is more resilient than a hardcoded `minHeight` which
breaks when content varies across screen sizes.

### 3. MetricCard wraps in `<Link>` internally, not externally

The `href` prop is passed into `MetricCard` and the component conditionally
wraps its content in `<Link>`. This keeps the card's DOM structure self-contained
and avoids accessibility issues with nested interactive elements.

### 4. CategoryDistribution: HTML divs replace SVG

SVG bars cannot be wrapped in `<Link>` without hacks. Converting to HTML `<div>`
elements with percentage widths makes each bar a natural link target. The visual
result is equivalent (horizontal bars with labels and counts).

### 5. PipelineFlow: CSS flexbox with media query

Horizontal layout via `display: flex; flex-direction: row` with a
`@media (max-width: 768px)` query switching to `flex-direction: column`. Arrow
connectors between steps are CSS pseudo-elements or unicode characters that
rotate on mobile.

---

## File Targets

### 1. `src/app/components/MetricCard.tsx` (MODIFY)

Add optional props to the existing interface:
- `description?: string` — explanatory text below the metric value
- `linkLabel?: string` — footer text like "View queue >>"
- `href?: string` — navigation target

When `href` is present, wrap card content in `<Link href={href}>`. Add
`description` as a `<p>` below the value. Add `linkLabel` as a footer `<span>`.
Set `height: 100%` on the outer container. All new props are optional for
backward compatibility.

### 2. `src/app/components/home/MarketDashboard.tsx` (MODIFY)

Update all 4 `<MetricCard>` instances with:
- GitHub Stars: `href="/skills?sort=stars"`, description, linkLabel
- Submissions: `href="/queue"`, description, linkLabel
- Blocked: `href="/trust?tab=blocked"`, description, linkLabel
- Avg Score: `href="/audits"`, description, linkLabel

Ensure the card grid container uses flex/grid with equal-height alignment.

### 3. `src/app/components/charts/CategoryDistribution.tsx` (REWRITE)

Replace SVG rendering with HTML div-based bars. Each bar is a `<Link>` to
`/skills?category={categoryName}`. Bar width is calculated as a percentage of
the max category count. Add a CSS class for hover highlight.

### 4. `src/app/components/home/PipelineFlow.tsx` (NEW)

Server component receiving `PlatformStats`. Renders 4 steps:
1. Authors (stats.uniqueAuthors) -> /authors
2. Submitted (stats.totalSubmissions) -> /queue
3. Scanned (stats.scannedCount or derived) -> /audits
4. Published (stats.publishedSkills) -> /skills

Each step is a `<Link>` containing the step label and metric. Steps are
connected by arrow elements. CSS handles horizontal/vertical layout switch.

### 5. `src/app/page.tsx` (MODIFY)

Hero section restructured into 4 rows:
1. `<h1>` heading
2. Subtitle `<p>` with inline security `<span>`
3. `<HeroSearchInput>` at full width
4. CTA buttons + quick stats

Section order changed to:
Hero -> PipelineFlow -> MarketDashboard -> CategoryDistribution -> TrendingSkills -> Trust

### 6. `src/app/globals.css` (MODIFY)

Add styles for:
- `.category-bar:hover` background highlight
- `.pipeline-flow` horizontal/vertical responsive layout
- `.pipeline-step` styling
- `.pipeline-connector` arrow styling
- Media query for pipeline mobile layout

### 7. `src/app/components/home/HomeSkeleton.tsx` (MODIFY)

Add a `PipelineSkeleton` placeholder matching the pipeline flow layout position
in the page skeleton.

### 8. `src/app/components/home/HeroSearchInput.tsx` (MODIFY)

Remove any `maxWidth` or fixed-width constraints so the search input expands
to full container width.

---

## Data Flow

```
getHomeStats()
    │
    ├── PlatformStats.totalStars       → MetricCard (Stars)     → /skills?sort=stars
    ├── PlatformStats.totalSubmissions → MetricCard (Submissions)→ /queue
    ├── PlatformStats.blockedCount     → MetricCard (Blocked)    → /trust?tab=blocked
    ├── PlatformStats.averageScore     → MetricCard (Avg Score)  → /audits
    │
    ├── PlatformStats.uniqueAuthors    → PipelineFlow step 1     → /authors
    ├── PlatformStats.totalSubmissions → PipelineFlow step 2     → /queue
    ├── PlatformStats.scannedCount     → PipelineFlow step 3     → /audits
    ├── PlatformStats.publishedSkills  → PipelineFlow step 4     → /skills
    │
    └── PlatformStats.categories[]     → CategoryDistribution    → /skills?category=X
```

No new data fetching. All values already available in `PlatformStats`.

---

## Implementation Phases

### Phase 1: MetricCard Enhancement (T-001)
Add `description`, `linkLabel`, `href` props. Equal-height styling.

### Phase 2: MarketDashboard Wiring (T-002)
Wire all 4 cards with navigation targets and descriptions.

### Phase 3: PipelineFlow Component (T-003)
Create new component with 4 linked steps and responsive layout.

### Phase 4: CategoryDistribution Rewrite (T-004)
Convert SVG to HTML with clickable linked bars.

### Phase 5: Hero Section Cleanup (T-005)
Restructure hero into 4 rows, inline security callout.

### Phase 6: HeroSearchInput Width Fix (T-006)
Remove size constraints for full-width search.

### Phase 7: Section Reordering (T-007)
Reorder page sections and add PipelineFlow to the page.

### Phase 8: Skeleton and CSS (T-008)
Add PipelineSkeleton, hover styles, responsive pipeline CSS.

---

## Testing Strategy

### Unit / Integration Tests (Vitest + React Testing Library)

- **MetricCard**: renders description, linkLabel, wraps in Link when href provided, equal height class/style present
- **PipelineFlow**: renders 4 steps with correct labels, metrics, and hrefs
- **CategoryDistribution**: renders HTML bars (not SVG), each wrapped in correct Link href, hover class present
- **Hero section**: 4 rows rendered in order, search bar has full-width style, security callout is inline

### Visual / Manual Verification

- Equal card heights at 1440px, 1024px, 768px, 375px viewports
- All navigation links resolve to correct destination pages
- Pipeline horizontal on desktop, vertical on mobile
- No regressions in skeleton loading state

---

## Technical Challenges

### Challenge 1: CategoryDistribution SVG-to-HTML migration
**Problem**: Existing component uses SVG which cannot wrap elements in `<Link>`.
**Solution**: Rewrite as HTML divs with percentage-based widths. Visual parity
achieved via background colors and border-radius matching the original SVG bars.
**Risk**: Low. The chart is simple horizontal bars, not complex SVG paths.

### Challenge 2: Equal-height cards across varying content
**Problem**: Adding description text to some cards but not others could break
height alignment.
**Solution**: All 4 cards receive descriptions. Flex container with
`align-items: stretch` ensures equal height. Cards use `height: 100%`.
**Risk**: Low. Standard CSS flexbox pattern.

### Challenge 3: Pipeline responsive layout
**Problem**: Horizontal pipeline with connectors must reflow to vertical on
mobile without breaking visual connection between steps.
**Solution**: CSS flexbox direction switch at 768px breakpoint. Connectors use
CSS `::after` pseudo-elements that rotate 90 degrees on mobile.
**Risk**: Low. Tested with media query.

---

## Technology Stack

- **Language**: TypeScript (strict, ESM)
- **Framework**: Next.js 15 app router, React server components
- **Styling**: React.CSSProperties inline styles + CSS variables + globals.css
- **Navigation**: Next.js `<Link>` component
- **Testing**: Vitest + React Testing Library
- **New dependencies**: none

---

## Out of Scope

- No new API routes or server-side changes
- No client component conversions (everything stays server components)
- No animation or transition effects
- No changes to destination pages
- No new npm packages
