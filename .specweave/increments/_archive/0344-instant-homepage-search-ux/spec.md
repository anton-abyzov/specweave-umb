# FS-344: Instant Homepage + Search UX

## Problem
The home page is an async Server Component that blocks on two data fetches (`getPlatformStats` + `getTrendingSkills`) before rendering anything. On Neon cold starts or KV misses, this causes multi-second page loads. The search input is buried below the fold in the Category Navigator section.

## Solution
Split the page into a synchronous static shell with Suspense-streamed dynamic sections, add a prominent hero search input, and add compound database indexes for optimal query performance.

## User Stories

### US-001: Instant Page Shell via Suspense Streaming
**As a** visitor, **I want** the homepage to render instantly with skeleton placeholders, **so that** I see content immediately and data fills in progressively.

**Acceptance Criteria:**
- [x] AC-US1-01: Static shell (hero text, security callout, CTAs, verification info, agent badges) renders with zero data dependencies
- [x] AC-US1-02: Hero stats, market dashboard, trending skills, and category nav each stream independently via `<Suspense>`
- [x] AC-US1-03: Each dynamic section shows animated skeleton fallback while loading
- [x] AC-US1-04: `getPlatformStats` is deduplicated across Suspense boundaries via `React.cache()`
- [x] AC-US1-05: ISR revalidation reduced from 300s to 60s
- [x] AC-US1-06: Build-time fallback still works (try/catch per component)

### US-002: Hero Search Input
**As a** visitor, **I want** a search input visible in the hero section next to "Browse Skills", **so that** I can immediately start searching without scrolling.

**Acceptance Criteria:**
- [x] AC-US2-01: Search input appears in hero CTA row, next to "Browse Skills" button
- [x] AC-US2-02: Typing opens SearchPalette with the typed text pre-filled
- [x] AC-US2-03: Input clears itself after dispatching to SearchPalette
- [x] AC-US2-04: Cmd+K shortcut badge shown in the input
- [x] AC-US2-05: SearchPalette `openSearch` handler reads `detail.query` and pre-fills
- [x] AC-US2-06: Does NOT auto-focus on page load (mobile-friendly)

### US-003: Database Compound Indexes
**As a** platform operator, **I want** compound indexes for common query patterns, **so that** trending and browse queries use optimal index scans.

**Acceptance Criteria:**
- [x] AC-US3-01: Compound index `(isDeprecated, trendingScore7d DESC)` for `getTrendingSkills`
- [x] AC-US3-02: Compound index `(category, trendingScore7d DESC)` for category+trending browse
- [x] AC-US3-03: Compound index `(category, githubStars DESC)` for category+stars browse
- [x] AC-US3-04: Prisma schema updated with `@@index` declarations
- [x] AC-US3-05: Migration created and applied

## Non-Functional Requirements
- NFR-01: Homepage static shell must render in < 100ms (no data fetch blocking)
- NFR-02: `npm run build` passes with no errors
- NFR-03: Existing tests continue to pass
