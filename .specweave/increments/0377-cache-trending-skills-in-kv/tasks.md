# 0377: Tasks

### T-001: Add trendingSkills field to PlatformStats interface
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test**: Given the PlatformStats interface in stats-compute.ts -> When I inspect the type -> Then it includes a `trendingSkills` array field typed as an array of skill-shaped objects (name, displayName, author, repoUrl, category, certTier, trendingScore7d, trendingScore30d, trustTier, trustScore at minimum)

**Files**: `src/lib/stats-compute.ts`

---

### T-002: Add trending skills query to computeFullStats
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test**: Given computeFullStats runs -> When it executes the Promise.allSettled batch -> Then it includes a query for top 8 non-deprecated skills ordered by trendingScore7d DESC, and the returned PlatformStats includes the mapped results in `trendingSkills`

**Files**: `src/lib/stats-compute.ts`

---

### T-003: Add trending skills fallback to computeMinimalStats
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test**: Given computeMinimalStats runs as fallback -> When the trending query succeeds -> Then trendingSkills contains the results; When the trending query fails -> Then trendingSkills defaults to `[]`

**Files**: `src/lib/stats-compute.ts`

---

### T-004: Update EMPTY_STATS and backfill in stats-refresh.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-06 | **Status**: [ ] pending
**Test**: Given a cached KV blob without trendingSkills field -> When getPlatformStats parses it -> Then stats.trendingSkills is backfilled to `[]`. Given no cached stats -> When EMPTY_STATS is used -> Then it includes `trendingSkills: []`

**Files**: `src/lib/cron/stats-refresh.ts`

---

### T-005: Update TrendingSkillsSection to read from getHomeStats
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05, AC-US1-09 | **Status**: [ ] pending
**Test**: Given the TrendingSkillsSection component renders -> When it fetches data -> Then it calls getHomeStats() and reads trendingSkills from the result; it does NOT import or call getTrendingSkills from data.ts. Given empty trendingSkills -> When component renders -> Then it returns null (same as current empty behavior)

**Files**: `src/app/components/home/TrendingSkills.tsx`

---

### T-006: Update/add tests for stats-compute trending skills
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [ ] pending
**Test**: Given the stats-refresh test suite -> When computePlatformStats is called -> Then the result includes a `trendingSkills` array. Given the DB returns trending skills -> Then the array contains mapped skill entries

**Files**: `src/lib/cron/__tests__/stats-refresh.test.ts`

---

### T-007: Verify existing getTrendingSkills tests still pass
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [ ] pending
**Test**: Given the existing test suites for getTrendingSkills in data.test.ts, data-db-first.test.ts, data-prisma.test.ts -> When tests run -> Then all pass without modification (function still exists and is exported from data.ts)

**Files**: `src/lib/__tests__/data.test.ts`, `src/lib/__tests__/data-db-first.test.ts`, `src/lib/__tests__/data-prisma.test.ts`

---

### T-008: Build and deploy verification
**User Story**: US-001 | **Satisfies ACs**: all | **Status**: [ ] pending
**Test**: Given all changes are committed -> When `npm run build` runs -> Then it completes without errors. When deployed -> Then the homepage loads trending skills from KV cache with no DB query in the request path.
