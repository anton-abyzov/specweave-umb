# 0377: Cache Trending Skills in KV Stats Blob

## Problem

The homepage `TrendingSkillsSection` component calls `getTrendingSkills(8)` on every request, which hits the Prisma DB directly (`db.skill.findMany` with `orderBy: { trendingScore7d: "desc" }`). Meanwhile, the platform already has a robust KV caching pipeline for homepage stats (`platform:stats` blob in `SUBMISSIONS_KV`), refreshed every 5 minutes by cron. The trending skills data should ride along in that same blob instead of being a separate live DB query.

## Goal

Eliminate the live `getTrendingSkills` DB call from the homepage request path by adding a `trendingSkills` array to the existing `PlatformStats` KV blob. The `TrendingSkillsSection` component will read trending data from `getHomeStats()` (which already uses React `cache()` and multi-tier KV resolution) instead of importing `getTrendingSkills` from `data.ts`.

---

### US-001: Cache trending skills in KV stats blob
**Project**: vskill-platform

**As a** site visitor
**I want** the trending skills section to load from the KV cache
**So that** homepage renders are faster and don't require a live DB query for trending data

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `PlatformStats` interface includes a `trendingSkills` array field with the same shape as `SkillData` (at minimum: name, displayName, author, repoUrl, category, certTier, trendingScore7d, trendingScore30d, trustTier, trustScore)
- [ ] **AC-US1-02**: `computePlatformStats()` (both full and minimal paths) fetches top 8 trending skills by `trendingScore7d DESC` (non-deprecated) and includes them in the returned `PlatformStats` object
- [ ] **AC-US1-03**: `EMPTY_STATS` constant in `stats-refresh.ts` includes `trendingSkills: []` as fallback
- [ ] **AC-US1-04**: `TrendingSkillsSection` component reads trending data from `getHomeStats()` return value instead of calling `getTrendingSkills()` directly
- [ ] **AC-US1-05**: The `getTrendingSkills` import is removed from `TrendingSkills.tsx` (no direct DB call on homepage render)
- [ ] **AC-US1-06**: `getPlatformStats` backfill logic handles missing `trendingSkills` field for cached data written before this change (defaults to `[]`)
- [ ] **AC-US1-07**: Existing tests for `getTrendingSkills` in `data.ts` remain passing (function not removed, just no longer called from homepage)
- [ ] **AC-US1-08**: New/updated tests verify that `computePlatformStats` includes `trendingSkills` in its output
- [ ] **AC-US1-09**: `TrendingSkillsSection` gracefully handles empty `trendingSkills` array (renders nothing, same as current behavior)

## Technical Notes

- The `PlatformStats` interface lives in `src/lib/stats-compute.ts`
- The KV blob is written by `refreshPlatformStats()` in `src/lib/cron/stats-refresh.ts`
- The existing `safeStringify` handles BigInt serialization
- The trending skills query is simple (single `findMany` with `orderBy` + `take` + `where`) -- add it to the `Promise.allSettled` array in `computeFullStats`
- Keep `getTrendingSkills` in `data.ts` as a public API (it may be used by other routes/API endpoints) -- just remove its usage from the homepage component
- The `SkillData` type from `types.ts` is the full shape; the trending entries in the KV blob should use the same type for simplicity (avoids a separate slim type and mapping logic)

## Out of Scope

- Changing the cron refresh frequency (5 min is sufficient)
- Adding trending skills to the `/api/v1/stats` REST endpoint
- Modifying trending score calculation logic
