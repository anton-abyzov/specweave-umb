# Tasks: Add skillPath to Skill model and View Source link

## Phase 1: Database

### T-001: Add skillPath column to Skill model
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given Prisma schema → When migration runs → Then Skill table has nullable skillPath column

### T-002: Update publishSkill() to copy skillPath
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given a Submission with skillPath → When publishSkill() runs → Then Skill.skillPath matches Submission.skillPath

## Phase 2: API

### T-003: Add skillPath to SkillData interface and mapper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given a Skill with skillPath in DB → When GET /api/v1/skills/:name → Then response includes skillPath field

## Phase 3: Frontend

### T-004: Add Source meta row to skill detail page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given skill with skillPath → When viewing /skills/:name → Then "Source" row shows clickable link to {repoUrl}/blob/HEAD/{skillPath}
**Test**: Given skill without skillPath → When viewing /skills/:name → Then "Source" row shows "Source path unknown"

## Phase 4: Backfill

### T-005: Create backfill script
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given Skills with null skillPath → When script runs with --execute → Then skillPath populated from linked Submissions

## Phase 5: Verification

### T-006: Verify build passes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test**: Given all changes → When npm run build → Then no type errors
