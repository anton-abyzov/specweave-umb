# Tasks — 0321 Fix Skill Slugs

### T-001: Add extractRepoName helper to slug.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test**: Given repoUrl "https://github.com/owner/repo-name" → When extractRepoName called → Then returns "repo-name"

### T-002: Write slug-migration.ts core algorithm (RED tests first)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-09, AC-US1-10 | **Status**: [x] completed
**Test**: Given mock Prisma DB with skills covering all 6 scenarios → When recomputeSlugs(dryRun=true) called → Then returns correct rename/delete plans without mutations

### T-003: Implement recomputeSlugs GREEN
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-09, AC-US1-10 | **Status**: [x] completed
**Test**: All T-002 RED tests pass

### T-004: Add KV sync to recomputeSlugs
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [x] completed
**Test**: Given skill renamed from "old-slug" to "new-slug" → When executed → Then KV has skill:new-slug with data AND skill:alias:old-slug pointing to new-slug

### T-005: Create POST /api/v1/admin/recompute-slugs route
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08, AC-US1-10, AC-US1-11 | **Status**: [x] completed
**Test**: Given SUPER_ADMIN auth + dryRun=true → When POST → Then 200 with stats, no mutations; Given no auth → Then 401

### T-006: Run full test suite
**User Story**: US-001 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: All existing tests + new tests pass (34/34 new tests pass; 2 pre-existing failures in unrelated test files)
