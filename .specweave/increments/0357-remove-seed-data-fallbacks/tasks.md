# Tasks: 0357 Remove Seed Data Fallbacks

### T-001: Remove seed fallback from data.ts skill functions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given DB is unreachable at build time → When any skill function is called → Then it returns empty result ([], null, or 0), not seed data

- Replace 6 catch blocks (getSkills, getSkillByName, getSkillCategories, getSkillCount, getVerifiedSkillCount, getTrendingSkills) to return empty results
- Delete `applyFiltersInMemory()` function (lines 134-183)
- Remove all `await import("./seed-data")` from catch blocks
- Update file header comment
- Keep `import { agents }` (AC-US1-04)

### T-002: Remove seed count from health check
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given health endpoint is called → When response is returned → Then `seed_count` field is absent

- Remove `import { skills as seedSkills }` from route.ts
- Remove `seed_count` from response object
- Update route.test.ts to remove `seed_count` assertion

### T-003: Delete redundant seed scripts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given `scripts/` directory → When checked → Then only `prisma/seed.ts` remains for seeding

- Delete `scripts/seed-skills.ts`
- Delete `scripts/seed-skills-to-db.ts`

### T-004: Remove trending scores from seed-data.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test**: Given seed-data.ts → When inspected → Then no skill entry has `trendingScore7d` or `trendingScore30d`

- Remove `trendingScore7d` and `trendingScore30d` from all 118 skill entries
- Make fields optional in type or create seed-specific type
- Default to 0 in `prisma/seed.ts` when writing to DB

### T-005: Delete seed-data-trending.test.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test**: Given test directory → When checked → Then `seed-data-trending.test.ts` does not exist

### T-006: Rewrite data.test.ts skill tests
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test**: Given data.test.ts → When tests run → Then skill tests verify empty-state fallback behavior

- Remove seed-data mock for skills
- Rewrite skill function tests to expect empty results when DB fails
- Keep agent and submission tests unchanged

### T-007: Fix data-prisma.test.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed
**Test**: Given data-prisma.test.ts → When tests run → Then no stale merge assumptions or hardcoded 118 references

### T-008: Run tests and verify
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test**: Given all changes applied → When `npm test` runs → Then all tests pass
