# 0379 — Tasks

## Phase 1: Schema & Core Types

### T-001: Add BLOCKED to Prisma enum and generate migration
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given schema.prisma → When BLOCKED added to SubmissionState enum → Then `db:generate` succeeds and migration SQL contains `ALTER TYPE "SubmissionState" ADD VALUE 'BLOCKED'`

Files: `prisma/schema.prisma`, `prisma/migrations/20260307100000_add_blocked_state/migration.sql`

### T-002: Add BLOCKED to TypeScript type union
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given types.ts → When BLOCKED added → Then TypeScript compilation succeeds

Files: `src/lib/types.ts`

### T-003: Update submission-categories with BLOCKED
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given submission-categories.ts → When getStateCategory("BLOCKED") called → Then returns "blocked". When expandStateCategory("blocked") called → Then returns ["BLOCKED"]

Files: `src/lib/submission-categories.ts`

### T-004: Add block/unblock events to state machine
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US3-01 | **Status**: [x] completed
**Test**: Given state machine → When transition("RECEIVED", "block") → Then returns { newState: "BLOCKED", valid: true }. When transition("BLOCKED", "unblock") → Then returns { newState: "RECEIVED", valid: true }. When transition("PUBLISHED", "block") → Then returns { valid: false }

Files: `src/lib/pipeline/submission-machine.ts`

## Phase 2: API Simplifications

### T-005: Simplify blocked filter in submissions API
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given GET /api/v1/submissions?state=blocked → When blocked is a real category → Then query uses WHERE state='BLOCKED' instead of BlocklistEntry JOIN

Files: `src/app/api/v1/submissions/route.ts`

### T-006: Move blocked count to Phase 1 in stats cron
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given stats cron refresh → When BLOCKED is a real state → Then blocked count uses simple `count({ state: BLOCKED })` in Phase 1 parallel queries. Stats API is KV-read-only.

Files: `src/lib/cron/queue-stats-refresh.ts`, `src/app/api/v1/submissions/stats/route.ts`

### T-007: Add BLOCKED to admin submissions VALID_STATES and reenqueue
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given admin submissions route → When filtering by state=BLOCKED → Then returns only BLOCKED submissions. Given reenqueue route → When bulk-requeue state=BLOCKED → Then BLOCKED submissions transition to RECEIVED.

Files: `src/app/api/v1/admin/submissions/route.ts`, `src/app/api/v1/admin/reenqueue/route.ts`

## Phase 3: Pipeline Integration

### T-008: Add early blocklist check in process-submission
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test**: Given a submission with a blocked skillName → When process-submission runs → Then submission transitions to BLOCKED before scanning starts

Files: `src/lib/queue/process-submission.ts`

### T-009: Transition to BLOCKED on auto-blocklist creation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given tier1 scan with critical findings → When auto-blocklist entry is created → Then current submission state becomes BLOCKED (not just TIER1_FAILED)

Files: `src/lib/queue/process-submission.ts`

## Phase 4: Admin Routes

### T-010: Bulk-transition active submissions on admin block
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test**: Given 5 RECEIVED submissions with skillName "malware-tool" → When admin blocks "malware-tool" → Then all 5 transition to BLOCKED and SSE events fire

Files: `src/app/api/v1/admin/skills/[name]/block/route.ts`

### T-011: Bulk-transition BLOCKED submissions on admin unblock
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given 3 BLOCKED submissions with skillName "safe-tool" → When admin unblocks → Then all 3 transition to RECEIVED

Files: `src/app/api/v1/admin/blocklist/[id]/unblock/route.ts`

## Phase 5: UI

### T-012: Add BLOCKED and ON_HOLD badges to all UI state configs
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given a submission with state=BLOCKED → When rendered in SubmissionTable or admin pages → Then shows "Blocked" badge with dark red styling

Files: `src/app/queue/SubmissionTable.tsx`, `src/app/admin/submissions/page.tsx`, `src/app/admin/submissions/[id]/page.tsx`

## Phase 6: Backfill

### T-013: Backfill existing blocked submissions
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-02, AC-US2-01 | **Status**: [x] completed
**Test**: Given existing submissions matching active blocklist entries in non-terminal states → When backfill runs → Then they transition to BLOCKED state

Files: `prisma/migrations/20260307100001_backfill_blocked_state/migration.sql`
