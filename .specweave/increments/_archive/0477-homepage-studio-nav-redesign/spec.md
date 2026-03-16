---
increment: 0477-homepage-studio-nav-redesign
title: 'Homepage Simplification, Studio Landing Page, and Navigation Restructure'
status: completed
priority: P1
type: feature
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Homepage Simplification, Studio Landing Page, and Navigation Restructure

## Problem Statement

The verified-skill.com homepage crams 7+ sections together -- video hero, role cards, search input, trending skills, Skill Studio promo, category nav, market dashboard, verification explainer, and agent badges. Users visit to find skills but must scroll past marketing material to reach them. Meanwhile, `/studio` returns 404 despite Skill Studio being a core product, and the primary navigation includes author-workflow links (Queue, Submit) that clutter discovery flows.

## Goals

- Make skill search the dominant homepage interaction by placing a hero search input as the primary element
- Give Skill Studio its own dedicated landing page at `/studio` with video demo, feature cards, and getting-started guide
- Streamline primary navigation to discovery-oriented items (Skills, Studio, Publishers, Trust, Docs)
- Extract a shared VideoPlayer component from duplicated video logic in HomepageDemoHero and SkillStudioSection
- Delete dead homepage sections and their component files after migration

## User Stories

### US-001: Shared VideoPlayer Component
**Project**: vskill-platform
**As a** developer
**I want** a shared VideoPlayer component that encapsulates video playback with lazy loading
**So that** video logic is not duplicated across HomepageDemoHero and SkillStudioSection

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the VideoPlayer component, when rendered with a `src` prop (mp4 + webm), then it displays a video element with play/pause overlay button, autoPlay, muted, loop, and playsInline attributes
- [x] **AC-US1-02**: Given the VideoPlayer component with default props, when the video enters the viewport, then it starts loading via IntersectionObserver (lazy-load by default)
- [x] **AC-US1-03**: Given the VideoPlayer component with `eager={true}`, when the page loads, then the video loads immediately without waiting for intersection
- [x] **AC-US1-04**: Given the VideoPlayer component, when rendered, then it accepts `ariaLabel`, `accentColor`, and `className` props for customization, and the play/pause button border uses the accent color

---

### US-002: Studio Landing Page
**Project**: vskill-platform
**As a** skill author
**I want** a dedicated `/studio` page explaining Skill Studio features
**So that** I can learn about BDD testing, benchmarking, and local development before installing

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a visitor navigating to `/studio`, when the page loads, then they see a hero section with "Skill Studio" heading, the tagline "Test skills with BDD assertions, run benchmarks against any LLM, and track quality over time", and a CLI command (`npx vskill studio`) with a copy-to-clipboard button
- [x] **AC-US2-02**: Given the `/studio` page, when scrolling past the hero, then a video demo section renders using the shared VideoPlayer component with `/video/skill-studio.mp4` and `/video/skill-studio.webm` sources (lazy-loaded)
- [x] **AC-US2-03**: Given the `/studio` page, when scrolling to the features section, then 4 feature cards are displayed: "BDD Tests" (green), "A/B Compare" (blue), "Any Model" (purple), "100% Local" (cyan) -- each with a title, description, and accent color
- [x] **AC-US2-04**: Given the `/studio` page, when scrolling to the getting-started section, then 3 numbered steps are shown: (1) install vskill, (2) init a test suite, (3) run studio -- each with a CLI command
- [x] **AC-US2-05**: Given the `/studio` page, when inspecting the HTML head, then it contains page-specific `<title>`, `<meta name="description">`, Open Graph (`og:title`, `og:description`, `og:url`), and Twitter Card (`twitter:title`, `twitter:description`) metadata

---

### US-003: Navigation Restructure -- Desktop
**Project**: vskill-platform
**As a** visitor
**I want** the desktop navigation to show Skills, Studio, Publishers, Trust, and Docs
**So that** I can quickly access discovery and learning pages without author-workflow clutter

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the desktop nav in `layout.tsx`, when rendered, then it contains links in this order: Skills, Studio, Publishers, Trust, Docs -- and does NOT contain Queue or Submit links
- [x] **AC-US3-02**: Given the desktop nav, when the Studio link is present, then it links to `/studio`
- [x] **AC-US3-03**: Given the footer in `layout.tsx`, when rendered, then it retains all existing links AND adds a Studio link, keeping Queue and Submit accessible from the footer

---

### US-004: Navigation Restructure -- Mobile
**Project**: vskill-platform
**As a** mobile visitor
**I want** the mobile navigation menu to match the restructured desktop nav
**So that** I have a consistent experience across devices

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the MobileNav component, when the menu is open, then it shows links in this order: Skills, Studio, Publishers, Trust, Docs, GitHub -- and does NOT contain Queue or Submit
- [x] **AC-US4-02**: Given the mobile nav, when the Studio link is tapped, then the menu closes and navigates to `/studio`

---

### US-005: Homepage Simplification
**Project**: vskill-platform
**As a** visitor
**I want** the homepage to lead with a search-first design
**So that** I can find skills immediately without scrolling past marketing sections

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the homepage, when rendered, then the top section contains a compact header with the tagline "Install AI skills you can trust" and a key stat (e.g., "90k+ verified")
- [x] **AC-US5-02**: Given the homepage on a non-touch device (`matchMedia('(hover: hover)')` matches), when the page loads, then the hero search input is auto-focused
- [x] **AC-US5-03**: Given the homepage on a touch device, when the page loads, then the hero search input is NOT auto-focused (to avoid triggering the virtual keyboard)
- [x] **AC-US5-04**: Given the hero search input, when rendered, then its placeholder text reads "Search 90,000+ verified skills..." and typing dispatches `openSearch` custom event to the existing SearchPalette
- [x] **AC-US5-05**: Given the homepage, when rendered below the search, then sections appear in this order: category pills (CategoryNav), trending skills (TrendingSkillsSection), compact agent strip ("Works with 39 agents" + 6 agent icons + "+N more")
- [x] **AC-US5-06**: Given the homepage, when rendered, then HomepageDemoHero (video hero), role cards, SkillStudioSection, MarketDashboard, verification explainer, and full agent badge grid are NOT present

---

### US-006: Homepage SEO Structured Data
**Project**: vskill-platform
**As a** search engine crawler
**I want** JSON-LD SearchAction structured data on the homepage
**So that** the site can appear with a sitelinks search box in search results

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the homepage HTML, when inspecting the head, then a `<script type="application/ld+json">` tag contains a WebSite schema with `potentialAction` of type `SearchAction` pointing to `/skills?q={search_term_string}`
- [x] **AC-US6-02**: Given the JSON-LD, when validated, then it conforms to schema.org WebSite + SearchAction specification

---

### US-007: Dead Code Cleanup
**Project**: vskill-platform
**As a** developer
**I want** removed homepage sections and their component files deleted
**So that** the codebase stays lean and there is no dead code to maintain

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given the cleanup is complete, when checking the file system, then `HomepageDemoHero.tsx` and `MarketDashboard.tsx` (and related files) are deleted
- [x] **AC-US7-02**: Given the cleanup, when checking `HomeSkeleton.tsx`, then unused skeleton components (`HeroStatsSkeleton`, `DashboardSkeleton`) are removed if no longer imported anywhere
- [x] **AC-US7-03**: Given the cleanup, when running `npx tsc --noEmit`, then there are zero type errors (no dangling imports)
- [x] **AC-US7-04**: Given the cleanup, when running the full test suite, then all tests pass with no regressions

## Out of Scope

- Redesigning the `/skills` browse page or search results page
- Changing SearchPalette.tsx internals (Cmd+K, global type-to-search behavior)
- Adding analytics tracking for the new homepage layout (future increment)
- A/B testing between old and new homepage
- Responsive breakpoint redesign beyond nav changes
- Server-side search (search remains client-side via SearchPalette)

## Technical Notes

### Dependencies
- Existing components reused as-is: `SearchPalette.tsx`, `CategoryNav.tsx`, `TrendingSkillsSection.tsx`, `HeroSearchInput.tsx`
- Video assets already in `/public/video/`: `homepage-demo.mp4`, `homepage-demo.webm`, `skill-studio.mp4`, `skill-studio.webm`
- Agent branding data: `AGENT_COLORS`, `AGENT_ICONS` from `@/lib/agent-branding`

### Constraints
- `HeroSearchInput` dispatches `openSearch` custom event -- the new hero search must use this same mechanism
- Auto-focus uses `matchMedia('(hover: hover)')` to detect non-touch devices -- no user-agent sniffing
- VideoPlayer IntersectionObserver must disconnect on unmount to prevent memory leaks
- Homepage must remain `force-dynamic` for KV-backed stats

### Architecture Decisions
- Extract `VideoPlayer` as a client component in `src/app/components/shared/VideoPlayer.tsx`
- `/studio` is a new route at `src/app/studio/page.tsx` (server component with client VideoPlayer child)
- Agent strip data uses existing hardcoded `FEATURED_AGENTS` / `MORE_AGENTS` arrays -- first 6 entries for icons, total count derived from array lengths
- Navigation changes happen in `layout.tsx` (desktop) and `MobileNav.tsx` (mobile) -- inline styles, no CSS module changes needed

### Implementation Phases
1. **Phase 1**: Create VideoPlayer + /studio page (additive, no breaking changes)
2. **Phase 2**: Restructure navigation (add Studio, move Queue/Submit to footer only)
3. **Phase 3**: Homepage simplification (rewrite page.tsx)
4. **Phase 4**: Dead code cleanup + SEO structured data

## Success Metrics

- Homepage `page.tsx` reduced from ~300 to ~100 lines
- `/studio` returns 200 with correct OG/Twitter metadata
- Zero broken links after nav restructure (Queue/Submit still accessible via footer)
- TypeScript compiles clean (`tsc --noEmit`) after dead code removal
- All existing tests pass plus new tests for VideoPlayer, /studio page, and nav changes
