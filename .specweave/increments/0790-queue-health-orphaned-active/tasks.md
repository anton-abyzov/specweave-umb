---
increment: 0790-queue-health-orphaned-active
title: "Fix queue-health oldestActive reporting state-desync orphans"
---

# Tasks: 0790 — queue-health orphaned-active

### T-001: Add OLDEST_ACTIVE_FRESHNESS_MS constant
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given the file after edit, When grepped, Then `OLDEST_ACTIVE_FRESHNESS_MS = 6 * 60 * 60 * 1000` is defined as a top-level constant.

### T-002: Narrow oldestActive query with updatedAt freshness filter
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given a Prisma mock that returns null for the freshness-filtered query, When the handler runs, Then `oldestActive` is null in the response.

### T-003: Add parallel orphanedActive count + sample query
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given a Prisma mock returning `count=3` and a sample row with `updatedAt=<old>`, When the handler runs, Then `orphanedActive` is `{ count: 3, oldestId: <sample.id>, oldestUpdatedAt: <iso> }`.

### T-004: Add cache stale-shape detection
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given KV returns a cached body WITHOUT `orphanedActive`, When the handler runs, Then it recomputes (calls `db.submission.findFirst`). Given the new-shape cache, Then it returns the cached body with `cached: true`.

### T-005: Add 3 new vitest TCs in __tests__/route.test.ts
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test Plan**: New TCs cover the three behaviors above. Existing TCs continue to pass without modification (though mocks may need updates if they over-specified the existing where clause).

### T-006: Run regression — queue/health tests + typecheck
**User Story**: US-001..US-004 | **AC**: NFR | **Status**: [x] completed
**Test Plan**: `npx vitest run src/app/api/v1/queue/health/__tests__` → all green; `npx tsc --noEmit` → no new errors in `route.ts`.

### T-007: Promise.allSettled refactor + per-query warns + cache-skip on partial failure
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test Plan**: Given `mockCount` rejects but `mockFindFirst` resolves (oldestActive), When the handler runs, Then `oldestActive` is preserved, `orphanedActive` defaults to `{count:0, oldestId:null, oldestUpdatedAt:null}`, and `kvStore.has("queue-health:cache")` is false. Per-query warn assertions for each rejection path.
