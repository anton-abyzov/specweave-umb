---
increment: 0424-homepage-redesign
title: "Redesign vskill Platform Homepage"
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-005, T-006]
  US-004: [T-004]
  US-005: [T-007, T-008]
tasks_total: 8
tasks_completed: 0
---

# Tasks: Redesign vskill Platform Homepage

## User Story: US-001 - Metric Card Alignment and Navigation

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Tasks**: 2 total, 0 completed

---

### T-001: Enhance MetricCard with description, linkLabel, and href props
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-06, AC-US1-07
**Status**: [ ] pending

**Test Plan**:
- **Given** a MetricCard rendered with `href`, `description`, and `linkLabel` props
- **When** the component mounts
- **Then** the card wraps its content in a `<Link>` pointing to the href, displays the description text below the metric value, and shows the linkLabel as a footer element

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/MetricCard.test.tsx`
   - `testRendersDescriptionText()`: Render with `description="Total GitHub stars"`; assert text is present in the DOM (AC-US1-06)
   - `testRendersLinkLabel()`: Render with `linkLabel="Browse skills >>"`; assert text is present in the DOM (AC-US1-07)
   - `testWrapsInLinkWhenHrefProvided()`: Render with `href="/skills"`; assert a `<a>` element wraps the card content with correct href (AC-US1-01)
   - `testNoLinkWhenHrefOmitted()`: Render without `href`; assert no `<a>` wrapper exists (backward compatibility)
   - `testCardHasFullHeight()`: Render the card; assert outer container has `height: 100%` style for equal-height alignment (AC-US1-01)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/components/MetricCard.tsx`
2. Add optional props to the interface: `description?: string`, `linkLabel?: string`, `href?: string`
3. Set `height: "100%"` on the outer container style
4. Add a `<p>` element after the metric value displaying `description` when provided
5. Add a footer `<span>` displaying `linkLabel` when provided
6. When `href` is provided, import `Link` from `next/link` and wrap the card content in `<Link href={href}>`
7. Ensure all new props are optional so existing call sites remain unchanged

---

### T-002: Wire MetricCard navigation targets in MarketDashboard
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Status**: [ ] pending

**Test Plan**:
- **Given** the MarketDashboard component rendering 4 MetricCards
- **When** the dashboard mounts with platform stats
- **Then** each card receives the correct `href`, `description`, and `linkLabel` props

**Test Cases**:
1. **Unit**: `src/app/components/home/__tests__/MarketDashboard.test.tsx`
   - `testStarsCardLinksToSkillsSortStars()`: Assert Stars MetricCard has `href="/skills?sort=stars"` (AC-US1-02)
   - `testSubmissionsCardLinksToQueue()`: Assert Submissions MetricCard has `href="/queue"` (AC-US1-03)
   - `testBlockedCardLinksToTrustBlocked()`: Assert Blocked MetricCard has `href="/trust?tab=blocked"` (AC-US1-04)
   - `testAvgScoreCardLinksToAudits()`: Assert Avg Score MetricCard has `href="/audits"` (AC-US1-05)
   - `testAllCardsHaveDescriptions()`: Assert all 4 cards have non-empty `description` props (AC-US1-06)
   - `testAllCardsHaveLinkLabels()`: Assert all 4 cards have non-empty `linkLabel` props (AC-US1-07)
   - `testCardGridUsesEqualHeightLayout()`: Assert the card container has `align-items: stretch` or equivalent (AC-US1-01)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/components/home/MarketDashboard.tsx`
2. Update GitHub Stars `<MetricCard>` with `href="/skills?sort=stars"`, `description="Total GitHub stars across all published skills"`, `linkLabel="Browse skills >>"`
3. Update Submissions `<MetricCard>` with `href="/queue"`, `description="Total skill submissions received"`, `linkLabel="View queue >>"`
4. Update Blocked `<MetricCard>` with `href="/trust?tab=blocked"`, `description="Skills blocked by trust checks"`, `linkLabel="View blocked >>"`
5. Update Avg Score `<MetricCard>` with `href="/audits"`, `description="Average audit score across all scanned skills"`, `linkLabel="View audits >>"`
6. Ensure the card grid container uses `display: flex` or CSS grid with equal-height alignment

---

## User Story: US-002 - Pipeline Flow Visualization

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 1 total, 0 completed

---

### T-003: Create PipelineFlow component
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the PipelineFlow component rendered with platform stats
- **When** the component mounts
- **Then** it displays 4 connected steps (Authors, Submitted, Scanned, Published) each with a metric and link to the corresponding page

**Test Cases**:
1. **Unit**: `src/app/components/home/__tests__/PipelineFlow.test.tsx`
   - `testRendersFourSteps()`: Assert 4 step elements are present with labels "Authors", "Submitted", "Scanned", "Published" (AC-US2-01)
   - `testEachStepShowsMetric()`: Assert each step displays the correct number from stats (AC-US2-02)
   - `testAuthorsLinksToAuthorsPage()`: Assert Authors step has `href="/authors"` (AC-US2-03)
   - `testSubmittedLinksToQueue()`: Assert Submitted step has `href="/queue"` (AC-US2-03)
   - `testScannedLinksToAudits()`: Assert Scanned step has `href="/audits"` (AC-US2-03)
   - `testPublishedLinksToSkills()`: Assert Published step has `href="/skills"` (AC-US2-03)
   - `testRendersConnectorsBetweenSteps()`: Assert 3 connector elements exist between the 4 steps (AC-US2-01)
   - `testHasResponsivePipelineClass()`: Assert the container has the `pipeline-flow` CSS class for responsive layout (AC-US2-04)
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/components/home/PipelineFlow.tsx` as a server component (no `"use client"`)
2. Import `Link` from `next/link` and accept `PlatformStats` as a prop
3. Define 4 steps as an array: `[{ label: "Authors", metric: stats.uniqueAuthors, href: "/authors" }, ...]`
4. Render a flex container with class `pipeline-flow`
5. For each step, render a `<Link>` containing the step label and formatted metric number
6. Between each step, render a connector element (arrow character or CSS pseudo-element)
7. Add responsive CSS in globals.css: `flex-direction: row` desktop, `flex-direction: column` at `max-width: 768px`

---

## User Story: US-004 - Interactive Category Chart

**Linked ACs**: AC-US4-01, AC-US4-02
**Tasks**: 1 total, 0 completed

---

### T-004: Convert CategoryDistribution from SVG to clickable HTML bars
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [ ] pending

**Test Plan**:
- **Given** the CategoryDistribution component rendered with category data
- **When** the component mounts
- **Then** each category renders as an HTML bar wrapped in a link to `/skills?category=X` with hover highlight support

**Test Cases**:
1. **Unit**: `src/app/components/charts/__tests__/CategoryDistribution.test.tsx`
   - `testRendersHTMLBarsNotSVG()`: Assert no `<svg>` elements in output; assert `<div>` bar elements present (AC-US4-01)
   - `testEachBarLinksToCorrectCategory()`: For category "security", assert link has `href="/skills?category=security"` (AC-US4-01)
   - `testBarWidthProportionalToCount()`: For max-count category, assert bar width is 100%; for half-count category, assert width is 50% (AC-US4-01)
   - `testBarsHaveHoverClass()`: Assert each bar element has the `category-bar` CSS class for hover styling (AC-US4-02)
   - `testRendersAllCategories()`: Given 5 categories, assert 5 bar elements rendered (AC-US4-01)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/components/charts/CategoryDistribution.tsx`
2. Remove all SVG rendering logic (`<svg>`, `<rect>`, `<text>` elements)
3. Import `Link` from `next/link`
4. Calculate `maxCount` from the categories array
5. For each category, render a `<Link href={`/skills?category=${category.name}`}>` wrapping a container with:
   - Category name label
   - Count label
   - A bar `<div>` with `width: ${(category.count / maxCount) * 100}%` and class `category-bar`
6. Add `.category-bar:hover` style in `globals.css` with background highlight (e.g., `background-color: rgba(var(--accent-rgb), 0.1)`)

---

## User Story: US-003 - Hero Section Cleanup

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 0 completed

---

### T-005: Restructure hero section in page.tsx
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the homepage rendered
- **When** the hero section mounts
- **Then** it contains 4 distinct rows (heading, subtitle+security, search, CTAs+stats) with the security callout as compact inline text and a visible "Submit a Skill" secondary CTA

**Test Cases**:
1. **Unit**: `src/app/__tests__/page.test.tsx`
   - `testHeroHasFourRows()`: Assert 4 distinct row containers within the hero section (AC-US3-01)
   - `testSecurityCalloutIsInline()`: Assert security text is a `<span>` element (not a block-level element or full-width div) (AC-US3-03)
   - `testSubmitSkillCTAIsVisible()`: Assert a link/button with text "Submit a Skill" is present in the hero (AC-US3-04)
   - `testHeadingIsFirstRow()`: Assert the `<h1>` heading is in the first row of the hero (AC-US3-01)
   - `testSearchBarInThirdRow()`: Assert the search input is in the third row (AC-US3-01)
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/app/page.tsx`
2. Locate the hero section markup
3. Restructure into 4 explicit row containers:
   - Row 1: `<h1>` heading only
   - Row 2: Subtitle `<p>` with security callout as an inline `<span>` (not a separate block)
   - Row 3: `<HeroSearchInput>` component
   - Row 4: Primary CTA ("Browse Skills") + Secondary CTA ("Submit a Skill") + quick stats
4. Remove or collapse any full-width security block into the inline span
5. Ensure "Submit a Skill" links to the appropriate page (e.g., `/submit` or GitHub)

---

### T-006: Remove size constraints from HeroSearchInput
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [ ] pending

**Test Plan**:
- **Given** the HeroSearchInput component rendered
- **When** it is placed in a full-width container
- **Then** the search input expands to fill the container width with no maxWidth or fixed-width constraints

**Test Cases**:
1. **Unit**: `src/app/components/home/__tests__/HeroSearchInput.test.tsx`
   - `testSearchInputHasFullWidth()`: Assert the input or its container has `width: 100%` style (AC-US3-02)
   - `testNoMaxWidthConstraint()`: Assert the input container does NOT have a `maxWidth` style property (AC-US3-02)
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/app/components/home/HeroSearchInput.tsx`
2. Remove any `maxWidth` or fixed `width` (e.g., `width: "500px"`) from the input or its container styles
3. Set `width: "100%"` on the outermost container of the search input
4. Verify the search input stretches to fill its parent

---

## User Story: US-005 - Section Reordering and Visual Connection

**Linked ACs**: AC-US5-01, AC-US5-02
**Tasks**: 2 total, 0 completed

---

### T-007: Reorder page sections and integrate PipelineFlow
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [ ] pending

**Test Plan**:
- **Given** the homepage rendered with all sections
- **When** the page mounts
- **Then** sections appear in order: Hero, Pipeline, Dashboard, Categories, Trending, Trust

**Test Cases**:
1. **Unit**: `src/app/__tests__/page.test.tsx`
   - `testSectionOrder()`: Query all major section containers; assert order is Hero, Pipeline, Dashboard, Categories, Trending, Trust (AC-US5-01)
   - `testPipelineFlowRendered()`: Assert a PipelineFlow component is present on the page (AC-US5-01)
   - `testCategoriesBeforeTrending()`: Assert CategoryDistribution DOM node appears before TrendingSkills DOM node (AC-US5-02)
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/app/page.tsx`
2. Import `PipelineFlow` from `./components/home/PipelineFlow`
3. Reorder the JSX section rendering to match: Hero -> PipelineFlow -> MarketDashboard -> CategoryDistribution -> TrendingSkills -> Trust
4. Pass `stats` (from `getHomeStats()`) to the `<PipelineFlow>` component
5. Verify CategoryNav/CategoryDistribution appears before TrendingSkills in the JSX order

---

### T-008: Add PipelineSkeleton and responsive CSS
**User Story**: US-005 | **Satisfies ACs**: AC-US2-04, AC-US5-01
**Status**: [ ] pending

**Test Plan**:
- **Given** the homepage loading state and the pipeline section on various viewports
- **When** the skeleton renders and the pipeline displays on mobile
- **Then** a PipelineSkeleton placeholder is visible during loading and the pipeline switches to vertical layout on mobile

**Test Cases**:
1. **Unit**: `src/app/components/home/__tests__/HomeSkeleton.test.tsx`
   - `testPipelineSkeletonRendered()`: Assert a skeleton placeholder element for the pipeline is present in HomeSkeleton output (AC-US5-01)
   - `testPipelineSkeletonMatchesPosition()`: Assert the pipeline skeleton appears after the hero skeleton and before the dashboard skeleton (AC-US5-01)
2. **CSS**: Manual verification
   - `testPipelineHorizontalOnDesktop()`: At 1024px width, pipeline steps are in a horizontal row (AC-US2-04)
   - `testPipelineVerticalOnMobile()`: At 375px width, pipeline steps stack vertically (AC-US2-04)
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/app/components/home/HomeSkeleton.tsx`
2. Add a `PipelineSkeleton` section matching the pipeline layout: 4 placeholder boxes with connector placeholders between them
3. Position the PipelineSkeleton after the hero skeleton and before the dashboard skeleton
4. Open `src/app/globals.css`
5. Add `.pipeline-flow` styles: `display: flex; flex-direction: row; align-items: center; gap: 16px; justify-content: center`
6. Add `.pipeline-step` styles: `padding: 16px; border-radius: 8px; text-align: center; text-decoration: none`
7. Add `.pipeline-connector` styles for arrow elements
8. Add `@media (max-width: 768px)` block: `.pipeline-flow { flex-direction: column; }` with connector rotation
9. Add `.category-bar:hover` background highlight style
10. Run `npx vitest run` to confirm all tests pass
