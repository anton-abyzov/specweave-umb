---
increment: 0392-npm-weekly-downloads
title: "npm Weekly Download Stats Integration"
type: feature
status: planned
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004, T-005]
  US-003: [T-006, T-007]
  US-004: [T-008, T-009, T-010, T-011]
---

# Tasks: npm Weekly Download Stats Integration

## User Story: US-001 - Weekly Downloads Database Field

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

### T-001: Add npmDownloadsWeekly to Prisma schema and run migration

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the existing Prisma schema with `Skill` and `MetricsSnapshot` models
- **When** `npmDownloadsWeekly Int @default(0)` is added to both models and migration runs
- **Then** the migration applies without data loss and existing rows get default value 0

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma`
2. Add `npmDownloadsWeekly Int @default(0)` to `Skill` model (after `npmPackageVerified`)
3. Add `npmDownloadsWeekly Int @default(0)` to `MetricsSnapshot` model (after `npmDownloads`)
4. Run `npx prisma migrate dev --name add-npm-downloads-weekly`
5. Run `npx prisma generate`
6. Verify migration SQL uses `ALTER TABLE ... ADD COLUMN ... DEFAULT 0`

**Dependencies**: None

---

### T-002: Add npmDownloadsWeekly to SkillData type and data layer mapping

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `SkillData` interface in `src/lib/types.ts`
- **When** `npmDownloadsWeekly: number` is added
- **Then** TypeScript compilation passes and the data layer maps the field

**Test Cases**:
1. **Unit**: `src/lib/__tests__/data-db-first.test.ts`
   - testSkillDataIncludesWeeklyDownloads(): Verify mapped skill object has `npmDownloadsWeekly`
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `src/lib/types.ts`: add `npmDownloadsWeekly: number` to `SkillData` (after `npmDownloads`)
2. Edit `src/lib/data.ts`: add `npmDownloadsWeekly: s.npmDownloadsWeekly ?? 0` in skill mapping
3. Verify TypeScript compiles cleanly

**Dependencies**: T-001

---

## User Story: US-002 - Weekly Downloads Enrichment

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Tasks**: 3 total, 0 completed

### T-003: Add period parameter to fetchNpmDownloadsBulk

**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [x] completed

**Test Plan**:
- **Given** `fetchNpmDownloadsBulk` currently hardcodes `last-month` in the URL
- **When** a `period` parameter is added defaulting to `"last-month"`
- **Then** calling with `"last-week"` fetches from `https://api.npmjs.org/downloads/point/last-week/...`

**Test Cases**:
1. **Unit**: `src/lib/__tests__/popularity-fetcher.test.ts`
   - testBulkFetchDefaultsToLastMonth(): Verify existing behavior unchanged when period omitted
   - testBulkFetchLastWeek(): Verify URL uses `last-week` when period is `"last-week"`
   - testBulkFetchCacheKeyIncludesPeriod(): Verify cache keys are period-scoped (no cross-contamination)
   - **Coverage Target**: 95%

**Implementation**:
1. Edit `src/lib/popularity-fetcher.ts`
2. Add `period` parameter to `fetchNpmDownloadsBulk`: `period: "last-month" | "last-week" = "last-month"`
3. Replace hardcoded `last-month` in URL with `${period}`
4. Scope cache keys by period: `npm:${period}:${name}` (prevents monthly cache serving weekly requests)
5. Update `fetchNpmDownloads` single-package function similarly (used by `enrichSkillWithMetrics`)

**Dependencies**: None

---

### T-004: Add weekly bulk fetch to enrichment batch

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Status**: [x] completed

**Test Plan**:
- **Given** the enrichment cron calls `fetchNpmDownloadsBulk` once for monthly
- **When** a second sequential call with `"last-week"` is added
- **Then** weekly downloads are written to `npmDownloadsWeekly` in the DB transaction

**Test Cases**:
1. **Unit**: `src/lib/cron/__tests__/enrichment.test.ts`
   - testEnrichmentFetchesWeeklyDownloads(): Two calls to fetchNpmDownloadsBulk (last-month, last-week)
   - testWeeklyWrittenToSkill(): `npmDownloadsWeekly` included in skill update
   - testWeeklyIncludedInSnapshot(): MetricsSnapshot row includes `npmDownloadsWeekly`
   - testWeeklyNullPreservesExisting(): When weekly fetch returns null, existing value preserved
   - testMonthlyFieldUnchanged(): `npmDownloads` still written from monthly map, not weekly
   - testTrendingFormulaNotModified(): `buildTrendingScoreUpdateSql` output unchanged
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `src/lib/cron/enrichment.ts`
2. Add `npmDownloadsWeekly` to the `select` in `db.skill.findMany`
3. After existing monthly bulk fetch, add sequential weekly bulk fetch:
   ```typescript
   const npmWeeklyMap = npmPackageNames.length > 0
     ? await fetchNpmDownloadsBulk(npmPackageNames, "last-week")
     : new Map<string, number | null>();
   ```
4. In per-skill loop, extract weekly value: `const bulkNpmWeekly = skill.npmPackage ? npmWeeklyMap.get(skill.npmPackage) ?? null : null`
5. In npm verification branches, write `npmDownloadsWeekly` when weekly value available (null-preserves pattern)
6. In `currentMetrics` object, add `npmDownloadsWeekly` for snapshot
7. In MetricsSnapshot create, include `npmDownloadsWeekly`

**Dependencies**: T-001, T-003

---

### T-005: Regression test - trending formula unchanged

**User Story**: US-002
**Satisfies ACs**: AC-US2-06
**Status**: [x] completed

**Test Plan**:
- **Given** the `buildTrendingScoreUpdateSql` function
- **When** the SQL is generated after our changes
- **Then** it references only `npmDownloads` (monthly), never `npmDownloadsWeekly`

**Test Cases**:
1. **Unit**: `src/lib/cron/__tests__/trending-score.test.ts` (existing file, add test)
   - testTrendingFormulaNoWeeklyReference(): Assert SQL string does not contain `npmDownloadsWeekly`
   - **Coverage Target**: 90%

**Implementation**:
1. Add regression test to existing trending-score test file
2. Call `buildTrendingScoreUpdateSql()` and assert output SQL does not include `npmDownloadsWeekly`

**Dependencies**: T-004

---

## User Story: US-003 - Weekly Downloads in Skill Detail Page

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 0 completed

### T-006: Update data layer to include npmDownloadsWeekly in skill queries

**User Story**: US-003
**Satisfies ACs**: AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `getSkillByName` in `data.ts` selects skill fields for the detail page
- **When** `npmDownloadsWeekly` is added to the select
- **Then** the returned `SkillData` object includes the weekly value

**Test Cases**:
1. **Unit**: `src/lib/__tests__/data-db-first.test.ts`
   - testGetSkillByNameIncludesWeekly(): Verify `npmDownloadsWeekly` present in returned data
   - **Coverage Target**: 90%

**Implementation**:
1. Verify `data.ts` Prisma select for skill detail includes `npmDownloadsWeekly` (may already be included if using `findFirst` without explicit select)
2. Ensure the skill-to-SkillData mapping includes `npmDownloadsWeekly` (done in T-002)

**Dependencies**: T-002

---

### T-007: Add Weekly StatCard and relabel Monthly on skill detail page

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** the skill detail page shows a "NPM" StatCard for monthly downloads
- **When** `npmDownloadsWeekly > 0`
- **Then** a "Weekly" StatCard appears and the existing card is relabeled to "Monthly"

**Implementation**:
1. Edit `src/app/skills/[name]/page.tsx`
2. Change existing StatCard label from `"NPM"` to `"Monthly"` (line ~281)
3. Add new conditional StatCard after monthly:
   ```tsx
   {skill.npmDownloadsWeekly > 0 && <StatCard value={formatNumber(skill.npmDownloadsWeekly)} label="Weekly" />}
   ```
4. Both use `formatNumber` (already does, just verify)

**Dependencies**: T-006

---

## User Story: US-004 - Weekly Downloads in Edge Search Ranking

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
**Tasks**: 4 total, 0 completed

### T-008: Add npmDownloadsWeekly to SearchIndexEntry and bump INDEX_VERSION

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** `SearchIndexEntry` has no `npmDownloadsWeekly` field and `INDEX_VERSION` is 3
- **When** the field is added and version bumped to 4
- **Then** TypeScript compiles and the version change triggers full rebuild on deploy

**Test Cases**:
1. **Unit**: `src/lib/__tests__/search-index.test.ts`
   - testIndexVersionIs4(): Assert `INDEX_VERSION === 4`
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `src/lib/search-index.ts`
2. Add `npmDownloadsWeekly: number` to `SearchIndexEntry` interface
3. Change `INDEX_VERSION` from 3 to 4

**Dependencies**: T-002

---

### T-009: Update buildSearchIndex and updateSearchShard with 3-field sort

**User Story**: US-004
**Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** shards are sorted by `trustScore DESC, githubStars DESC`
- **When** `npmDownloadsWeekly` is added as third tiebreaker
- **Then** skills with equal trust and stars sort by weekly downloads descending

**Test Cases**:
1. **Unit**: `src/lib/__tests__/search-index.test.ts`
   - testBuildSearchIndexThreeFieldSort(): Build index, verify shard entries sorted by trust, stars, weekly
   - testUpdateSearchShardThreeFieldSort(): Upsert entry, verify shard re-sorted with 3 fields
   - testTiebreakerWeeklyDownloads(): Two skills with same trust/stars, higher weekly ranks first
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `src/lib/search-index.ts`
2. In `buildSearchIndex`: add `npmDownloadsWeekly: true` to Prisma select
3. In entry construction: add `npmDownloadsWeekly: skill.npmDownloadsWeekly ?? 0`
4. Update all sort comparators (4 locations: name shards, author shards in build; name shard, author shard in upsert):
   ```typescript
   (a, b) => b.trustScore - a.trustScore || b.githubStars - a.githubStars || b.npmDownloadsWeekly - a.npmDownloadsWeekly
   ```

**Dependencies**: T-008

---

### T-010: Update edge search sort and SearchResult type in search.ts

**User Story**: US-004
**Satisfies ACs**: AC-US4-06, AC-US4-07
**Status**: [x] completed

**Test Plan**:
- **Given** `searchSkillsEdge` sorts by `trustScore DESC, githubStars DESC`
- **When** `npmDownloadsWeekly` is added as third tiebreaker
- **Then** edge search results reflect 3-field sort and include the field

**Test Cases**:
1. **Unit**: `src/lib/search.test.ts`
   - testEdgeSearchThreeFieldSort(): Mock KV shard, verify result order uses weekly tiebreaker
   - testSearchResultIncludesWeekly(): Verify `npmDownloadsWeekly` in mapped SearchResult
   - testPostgresOrderByIncludesWeekly(): Verify ORDER BY in Postgres fallback includes `npmDownloadsWeekly`
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `src/lib/search.ts`
2. Add `npmDownloadsWeekly?: number` to `SearchResult` interface
3. In `searchSkillsEdge`, update sort comparator:
   ```typescript
   filtered.sort((a, b) => b.trustScore - a.trustScore || b.githubStars - a.githubStars || (b.npmDownloadsWeekly ?? 0) - (a.npmDownloadsWeekly ?? 0));
   ```
4. In result mapping, add `npmDownloadsWeekly: entry.npmDownloadsWeekly ?? 0`
5. In `searchSkills` (Postgres fallback), update both ORDER BY clauses to add `"npmDownloadsWeekly" DESC`
6. Add `npmDownloadsWeekly` to Postgres SELECT and result mapping

**Dependencies**: T-009

---

### T-011: Update SearchShardQueueMessage and publish path

**User Story**: US-004
**Satisfies ACs**: AC-US4-02 (queue path)
**Status**: [x] completed

**Test Plan**:
- **Given** `SearchShardQueueMessage.entry` lacks `npmDownloadsWeekly`
- **When** the field is added and the publish path includes it
- **Then** newly published skills create shard entries with `npmDownloadsWeekly: 0`

**Test Cases**:
1. **Unit**: `src/lib/__tests__/submission-store.test.ts`
   - testRebuildSearchShardIncludesWeekly(): Verify queue message entry has `npmDownloadsWeekly`
   - **Coverage Target**: 85%

**Implementation**:
1. Edit `src/lib/queue/types.ts`: add `npmDownloadsWeekly?: number` to `SearchShardQueueMessage.entry`
2. Edit `src/lib/submission-store.ts`: add `npmDownloadsWeekly: 0` to the queue message entry object (~line 1170)

**Dependencies**: T-008

---

## Summary

| Phase | Tasks | ACs Covered |
|-------|-------|-------------|
| US-001: Schema + Types | T-001, T-002 | AC-US1-01 through AC-US1-04 |
| US-002: Enrichment | T-003, T-004, T-005 | AC-US2-01 through AC-US2-06 |
| US-003: UI Display | T-006, T-007 | AC-US3-01 through AC-US3-04 |
| US-004: Search Ranking | T-008, T-009, T-010, T-011 | AC-US4-01 through AC-US4-07 |

**Total**: 11 tasks, 21 acceptance criteria covered, 0 gaps
