# Tasks — 0343

### T-001: Rewrite computePlatformStats with Prisma queries
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given stats-compute.ts → When computePlatformStats called → Then no $queryRaw for deduped stars, unique repos, npm stats; all queries in single Promise.all

### T-002: Add safeTopStarRepos with DISTINCT ON fallback
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given DISTINCT ON query fails → When safeTopStarRepos called → Then falls back to findMany + JS dedup

### T-003: Add computeMinimalStats fallback
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given full stats computation throws → When computePlatformStats called → Then returns minimal stats with totalSkills > 0

### T-004: Add BigInt-safe serialization in getPlatformStats
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given stats contain BigInt values → When serialized to KV → Then no serialization error, values stored as numbers

### T-005: Update stats-compute unit tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 through AC-US2-04 | **Status**: [x] completed
**Test**: Given updated mock structure → When tests run → Then all pass with new Prisma-based query mocks

### T-006: Create E2E smoke tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 through AC-US3-05 | **Status**: [x] completed
**Test**: Given production deployment → When smoke tests run → Then homepage count > 0, stats API 200, skills visible

### T-007: Deploy and verify production
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 through AC-US1-04 | **Status**: [x] completed
**Test**: Given deployment complete → When visiting verified-skill.com → Then homepage shows real skill counts
