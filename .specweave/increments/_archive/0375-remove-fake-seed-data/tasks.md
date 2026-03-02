# Tasks: 0375-remove-fake-seed-data

## Phase 1: Prisma Schema + Migration

### T-001: Add repo404Count field to Skill model
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given Prisma schema -> When `repo404Count Int @default(0)` added to Skill model -> Then migration generates successfully and field defaults to 0

### T-002: Generate and apply Prisma migration
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given updated schema -> When `npx prisma migrate dev` runs -> Then migration SQL creates `repo404Count` column with default 0

## Phase 2: File Rename + Data Removal

### T-003: Create agent-data.ts with agents array only
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given seed-data.ts exists -> When agent-data.ts is created -> Then it exports only `agents: AgentData[]` (44 entries) and re-exports `AgentData` type, no `skills` or `SeedSkillData`

### T-004: Delete seed-data.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given agent-data.ts exists with correct content -> When seed-data.ts is deleted -> Then no file named seed-data.ts exists in src/lib/

### T-005: Update import in data.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given data.ts imports from `./seed-data` -> When updated to `./agent-data` -> Then TypeScript compiles and `getAgents()` returns 44 agents

### T-006: Update import in prisma/seed.ts
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-02 | **Status**: [x] completed
**Test**: Given seed.ts imports from `../src/lib/seed-data` -> When updated to `../src/lib/agent-data` -> Then TypeScript compiles and only `agents` is imported

### T-007: Update comment in agent-branding.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test**: Given agent-branding.ts references "seed-data" in comment -> When updated -> Then comment says "agent-data"

## Phase 3: Seed Script Update

### T-008: Remove skill upsert loop from seed.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test**: Given seed.ts has skill upsert loop -> When loop removed -> Then `npx prisma db seed` runs without inserting any skills

### T-009: Remove SKILL_NAME_RENAMES map from seed.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given seed.ts has SKILL_NAME_RENAMES -> When removed -> Then no rename migration runs during seed

### T-010: Remove skills import and SeedSkillData references from seed.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given seed.ts imports `skills` -> When import removed -> Then seed.ts only imports `agents` from agent-data

### T-011: Verify admin and blocklist seeding still works
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given updated seed.ts -> When `npx prisma db seed` runs with ADMIN_EMAIL+ADMIN_PASSWORD -> Then admin is created and blocklist entries are seeded

## Phase 4: Enrichment 404 Hardening

### T-012: Write failing test for 404 counter increment (TDD RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given a skill with repo404Count=0 -> When enrichment gets GitHub 404 -> Then repo404Count is incremented to 1

### T-013: Write failing test for 404 threshold deprecation (TDD RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test**: Given a skill with repo404Count=2 -> When enrichment gets GitHub 404 -> Then repo404Count=3 and isDeprecated=true

### T-014: Write failing test for 404 counter reset on success (TDD RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given a skill with repo404Count=2 -> When enrichment gets GitHub 200 -> Then repo404Count is reset to 0

### T-015: Implement 404 counter logic in enrichment.ts (TDD GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given failing tests T-012/T-013/T-014 -> When 404 counter logic added to enrichment.ts -> Then all three tests pass

### T-016: Update existing enrichment 404 test (TDD REFACTOR)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Test**: Given "does NOT auto-deprecate on single 404" test -> When updated to verify counter increment instead -> Then test reflects new counter-based behavior

## Phase 5: DB Cleanup Script

### T-017: Create cleanup-seed-skills.ts script
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given production DB with seed skills -> When script runs without --execute -> Then it prints count of records to delete without actually deleting

### T-018: Add pipeline-entry skip logic to cleanup script
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test**: Given a seed skill name that also has a Submission record -> When cleanup runs -> Then that skill is skipped (not deleted)

## Phase 6: Test Updates

### T-019: Delete seed-data-accuracy.test.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test**: Given seed-data-accuracy.test.ts exists -> When deleted -> Then test suite runs without it

### T-020: Update data.test.ts mock path
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed
**Test**: Given data.test.ts mocks `../seed-data` -> When updated to `../agent-data` -> Then test passes with same assertions

### T-021: Remove or update TC-021 in popularity-fetcher.test.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test**: Given TC-021 imports seed-data for npmPackage check -> When removed -> Then popularity-fetcher tests pass

### T-022: Verify data-enrichment.test.ts still passes
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Test**: Given data-enrichment.test.ts has no direct seed-data dependency -> When test suite runs -> Then all data-enrichment tests pass

### T-023: Run full test suite and verify all pass
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [x] completed
**Test**: Given all changes applied -> When `npm test` runs -> Then exit code 0 with >80% coverage
