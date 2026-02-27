# Tasks — 0344-instant-homepage-search-ux

## US-001: Instant Page Shell via Suspense Streaming

### T-001: Create skeleton components
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given homepage loads → When data is fetching → Then animated skeletons visible for stats, dashboard, trending, categories

### T-002: Extract HeroStats async component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-06 | **Status**: [x] completed
**Test**: Given HeroStats renders → When KV has stats → Then shows totalSkills heading + inline stats strip

### T-003: Extract MarketDashboard async component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04, AC-US1-06 | **Status**: [x] completed
**Test**: Given MarketDashboard renders → When KV has stats → Then shows 4 MetricCards + CategoryDistribution

### T-004: Extract TrendingSkills async component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-06 | **Status**: [x] completed
**Test**: Given TrendingSkills renders → When DB has skills → Then shows top 8 ranked skills with momentum

### T-005: Extract CategoryNav async component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04, AC-US1-06 | **Status**: [x] completed
**Test**: Given CategoryNav renders → When KV has stats → Then shows category pills with counts

### T-006: Add React.cache wrapper for getPlatformStats
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given multiple Suspense boundaries call getCachedPlatformStats → When rendering → Then only one KV read occurs

### T-007: Restructure page.tsx with Suspense boundaries
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [x] completed
**Test**: Given homepage loads → When page renders → Then static shell appears instantly, dynamic sections stream with skeletons

## US-002: Hero Search Input

### T-008: Create HeroSearchInput client component
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06 | **Status**: [x] completed
**Test**: Given hero section → When user types "react" → Then SearchPalette opens with "react" pre-filled

### T-009: Modify SearchPalette to handle pre-filled query
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given SearchPalette receives openSearch event with detail.query → When it opens → Then search input has the query text and search executes

## US-003: Database Compound Indexes

### T-010: Add compound indexes to Prisma schema + migration
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: Given schema has compound indexes → When `prisma db push` runs → Then indexes exist in database

## Verification

### T-011: Build and test verification
**Satisfies ACs**: NFR-01, NFR-02, NFR-03 | **Status**: [x] completed
**Test**: Given all changes → When `npm run build` and `npx vitest run` → Then both pass
