---
increment: 0424-homepage-redesign
title: "Redesign vskill Platform Homepage"
type: feature
priority: P1
status: planned
created: 2026-03-04
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Redesign vskill Platform Homepage

## Problem Statement

The vskill platform homepage has several UX issues: metric cards render at unequal heights and lack navigation, there is no visual explanation of the skill verification pipeline, the hero section is cluttered with an oversized security callout blocking scannability, category bars are non-interactive dead SVGs, and the section order does not guide visitors from understanding to exploration.

## Goals

- Make all metric cards equal height, navigable, and self-describing with footer links
- Add a pipeline flow visualization showing the Authors-to-Published journey
- Clean up the hero section into distinct scannable rows
- Convert category chart from SVG to clickable HTML bars
- Reorder page sections for logical narrative flow
- Maintain server-component architecture with no new API routes

## User Stories

### US-001: Metric Card Alignment and Navigation (P1)
**Project**: vskill-platform

**As a** visitor
**I want** all metric cards to be equal height and clickable
**So that** I can navigate to detailed views from any metric

**Acceptance Criteria**:
- [ ] **AC-US1-01**: All 4 metric cards render at equal height regardless of content
- [ ] **AC-US1-02**: GitHub Stars card links to /skills?sort=stars
- [ ] **AC-US1-03**: Submissions card links to /queue
- [ ] **AC-US1-04**: Blocked card links to /trust?tab=blocked
- [ ] **AC-US1-05**: Avg Score card links to /audits
- [ ] **AC-US1-06**: Each card shows a description explaining the metric
- [ ] **AC-US1-07**: Each card shows a footer link label (e.g., "View queue >>")

---

### US-002: Pipeline Flow Visualization (P1)
**Project**: vskill-platform

**As a** visitor
**I want** to see a visual pipeline showing how skills flow through the platform
**So that** I understand the verification process at a glance

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Pipeline shows 4 connected steps: Authors -> Submitted -> Scanned -> Published
- [ ] **AC-US2-02**: Each step displays a relevant metric from platform stats
- [ ] **AC-US2-03**: Each step links to its corresponding page (/authors, /queue, /audits, /skills)
- [ ] **AC-US2-04**: Pipeline renders horizontally on desktop and vertically on mobile

---

### US-003: Hero Section Cleanup (P1)
**Project**: vskill-platform

**As a** visitor
**I want** a clean, scannable hero section
**So that** I can quickly understand what vskill is and start searching

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Hero has 4 distinct rows: heading, subtitle+security, search, CTAs+stats
- [ ] **AC-US3-02**: Search bar is full-width and prominent
- [ ] **AC-US3-03**: Security callout is compact inline text (not a full-width block)
- [ ] **AC-US3-04**: "Submit a Skill" secondary CTA is visible

---

### US-004: Interactive Category Chart (P2)
**Project**: vskill-platform

**As a** visitor
**I want** to click category bars to browse skills in that category
**So that** I can discover skills by topic

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Each category bar is a clickable link to /skills?category=X
- [ ] **AC-US4-02**: Bars show hover state with background highlight

---

### US-005: Section Reordering and Visual Connection (P1)
**Project**: vskill-platform

**As a** visitor
**I want** the page sections to flow logically
**So that** I'm guided from understanding to exploration

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Section order: Hero -> Pipeline -> Dashboard -> Categories -> Trending -> Trust
- [ ] **AC-US5-02**: CategoryNav appears before TrendingSkills

## Functional Requirements

### FR-001: MetricCard Component Enhancement
MetricCard receives new optional props: `description` (string), `linkLabel` (string), `href` (string). When `href` is provided, the entire card wraps in a Next.js `<Link>`. Card height is fixed via CSS `minHeight` or flexbox equal-height container.

### FR-002: PipelineFlow Component
New server component at `src/app/components/home/PipelineFlow.tsx`. Receives `PlatformStats` and renders 4 steps connected by arrows/connectors. Each step is a `<Link>` to its target page. Uses CSS media query to switch from horizontal (desktop) to vertical (mobile) layout.

### FR-003: CategoryDistribution Conversion
Replace SVG-based category bars with HTML `<div>` elements wrapped in `<Link>` components. Each bar width is proportional to category count. Hover state via CSS `:hover` pseudo-class or inline style with `onMouseEnter`/`onMouseLeave`.

### FR-004: Hero Section Restructure
Reorganize `page.tsx` hero markup into 4 explicit rows. Search bar gets `width: 100%`. Security callout reduced to a single inline `<span>` next to the subtitle. "Submit a Skill" CTA rendered as a secondary button.

## Success Criteria

- All metric cards visually equal height at any viewport width
- Every metric card, pipeline step, and category bar navigates to the correct page
- Hero section fits in viewport on 1440px desktop without scrolling to see the search bar
- Page sections follow the specified order
- No regressions in existing functionality (server components, data loading, skeleton states)

## Out of Scope

- New API routes or backend changes
- Client-side interactivity beyond link navigation and hover states
- Animation or transition effects on pipeline steps
- Mobile-specific redesign beyond responsive pipeline layout
- Changes to individual destination pages (/queue, /skills, /audits, /trust, /authors)

## Dependencies

- Existing `getHomeStats()` server function provides all required data via `PlatformStats`
- Existing `MetricCard` component in `src/app/components/MetricCard.tsx`
- Existing `CategoryDistribution` chart in `src/app/components/charts/CategoryDistribution.tsx`
- Existing `HomeSkeleton` in `src/app/components/home/HomeSkeleton.tsx`
