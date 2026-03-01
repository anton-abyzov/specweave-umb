---
increment: 0392-npm-weekly-downloads
title: "npm Weekly Download Stats Integration"
type: feature
priority: P1
status: in-progress
created: 2026-03-01
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: npm Weekly Download Stats Integration

## Overview

Add `npmDownloadsWeekly` as a separate field alongside the existing monthly `npmDownloads`. Weekly downloads are used for display on skill detail pages and as a third tiebreaker in edge search sorting. The existing monthly field and trending formula remain unchanged.

## Interview Decisions

- **Q1**: Add `npmDownloadsWeekly` as a separate DB column; keep `npmDownloads` for the trending formula.
- **Q2**: Trending formula unchanged — weekly field is for display and search ranking only.
- **Q3**: Edge search sort becomes: `trustScore DESC, githubStars DESC, npmDownloadsWeekly DESC`.
- **Q4**: Two bulk npm API calls per enrichment cycle — one `last-month` (existing), one `last-week` (new).
- **Q5**: Existing monthly values untouched; weekly defaults to 0 and populates on next enrichment.

## User Stories

### US-001: Weekly Downloads Database Field (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** a dedicated `npmDownloadsWeekly` integer field on the Skill model
**So that** weekly download counts are stored separately from monthly without affecting the trending formula

**Acceptance Criteria**:
- [x] **AC-US1-01**: Prisma schema has `npmDownloadsWeekly Int @default(0)` on the `Skill` model alongside existing `npmDownloads`
- [x] **AC-US1-02**: A Prisma migration adds the column with default 0 (no data loss on existing rows)
- [x] **AC-US1-03**: `MetricsSnapshot` model includes `npmDownloadsWeekly Int @default(0)` for historical tracking
- [x] **AC-US1-04**: `SkillData` type in `src/lib/types.ts` includes `npmDownloadsWeekly: number`

---

### US-002: Weekly Downloads Enrichment (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the enrichment cron to fetch weekly npm downloads alongside monthly
**So that** the `npmDownloadsWeekly` field is populated automatically each cycle

**Acceptance Criteria**:
- [x] **AC-US2-01**: `fetchNpmDownloadsBulk` accepts a `period` parameter (`"last-month"` | `"last-week"`) defaulting to `"last-month"`
- [x] **AC-US2-02**: Enrichment batch makes two bulk API calls: one to `https://api.npmjs.org/downloads/point/last-month/...` (existing) and one to `https://api.npmjs.org/downloads/point/last-week/...` (new)
- [x] **AC-US2-03**: Weekly download count is written to `npmDownloadsWeekly` in the same DB transaction as other metric updates
- [x] **AC-US2-04**: If the weekly API call fails, existing `npmDownloadsWeekly` value is preserved (null-means-preserve pattern)
- [x] **AC-US2-05**: Weekly download count is included in the `MetricsSnapshot` row created during enrichment
- [x] **AC-US2-06**: The existing `npmDownloads` (monthly) field and trending formula SQL are not modified

---

### US-003: Weekly Downloads in Skill Detail Page (P1)
**Project**: vskill-platform

**As a** developer browsing skills
**I want** to see weekly download stats on the skill detail page
**So that** I can gauge recent adoption velocity beyond the monthly aggregate

**Acceptance Criteria**:
- [x] **AC-US3-01**: Skill detail page shows a "Weekly" StatCard when `npmDownloadsWeekly > 0`
- [x] **AC-US3-02**: The existing StatCard labeled "NPM" is relabeled to "Monthly" for clarity
- [x] **AC-US3-03**: Both monthly and weekly StatCards use the same `formatNumber` helper for consistent display
- [x] **AC-US3-04**: Data layer (`src/lib/data.ts`) includes `npmDownloadsWeekly` in the Prisma select for skill detail queries

---

### US-004: Weekly Downloads in Edge Search Ranking (P2)
**Project**: vskill-platform

**As a** developer searching for skills
**I want** weekly download count used as a third tiebreaker in edge search results
**So that** actively-downloaded skills rank higher among otherwise equal results

**Acceptance Criteria**:
- [x] **AC-US4-01**: `SearchIndexEntry` interface includes `npmDownloadsWeekly: number`
- [x] **AC-US4-02**: `buildSearchIndex` selects `npmDownloadsWeekly` from Postgres and populates it into each shard entry
- [x] **AC-US4-03**: Shard sort order is `trustScore DESC, githubStars DESC, npmDownloadsWeekly DESC`
- [x] **AC-US4-04**: `updateSearchShard` upsert uses the same three-field sort order
- [x] **AC-US4-05**: `INDEX_VERSION` is bumped to 4 to trigger full index rebuild on deploy
- [x] **AC-US4-06**: Edge search results in `search.ts` sort by `trustScore DESC, githubStars DESC, npmDownloadsWeekly DESC` (KV path and Postgres fallback)
- [x] **AC-US4-07**: The `SearchResult` type in `search.ts` includes `npmDownloadsWeekly`

## Functional Requirements

### FR-001: Additive Schema Change
The `npmDownloadsWeekly` column is added with `@default(0)`. No backfill migration is needed — the field starts at 0 and is populated on the next enrichment cycle.

### FR-002: Two Bulk API Calls
The enrichment batch fetches both `last-month` and `last-week` periods from the npm registry API. Both calls use the existing `fetchNpmDownloadsBulk` function with the new `period` parameter. The two calls run sequentially (not in parallel) to respect npm API rate limits.

### FR-003: Trending Formula Unchanged
The `buildTrendingScoreUpdateSql` function in `src/lib/trending-formula.ts` continues to use `npmDownloads` (monthly). No weight adjustments are made.

### FR-004: Index Version Bump
`INDEX_VERSION` bumps from 3 to 4 in `search-index.ts`. This ensures all edge caches rebuild their shards with the new `npmDownloadsWeekly` field on next cron run.

## Success Criteria

- Weekly download data appears on skill detail pages after one enrichment cycle
- Edge search sort reflects three-field tiebreaker
- Trending formula produces identical scores before and after deploy (regression test)
- No increase in npm API error rate (two calls per batch remains within rate limits)

## Out of Scope

- Changing trending formula weights to incorporate weekly downloads
- Historical backfill of weekly download data for past enrichment snapshots
- UI chart or sparkline for weekly download trends
- Weekly downloads in the admin npm-backfill endpoint (uses monthly only)

## Dependencies

- npm registry bulk downloads API (`/downloads/point/last-week/`) — same endpoint pattern as monthly, already stable
- Prisma migration infrastructure (existing)
