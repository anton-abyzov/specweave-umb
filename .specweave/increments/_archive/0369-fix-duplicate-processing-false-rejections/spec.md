# 0369: Fix Duplicate Processing False Rejections

## Problem

Submissions are processed multiple times by the queue (retry + recovery cron). Because `updateState()` has no guards, the last write wins — causing PUBLISHED submissions to be overridden to REJECTED. Confirmed on 7+ submissions (miro-ai, x-ai-topic-selector, paperbanana, Tool-Solutions, loom, manifest-dev, TLDR) all scoring 100/100 PASS but ending as REJECTED.

Root cause: `updateState()` in submission-store.ts blindly overwrites state without checking current state. The state machine in `submission-machine.ts` defines valid transitions but is never called.

## User Stories

### US-001: State Guard (P0)
**As a** platform operator
**I want** success terminal states (PUBLISHED, VENDOR_APPROVED) to be locked against pipeline regression
**So that** duplicate processing cannot overwrite published skills with rejection

#### Acceptance Criteria
- [x] AC-US1-01: `updateState()` blocks transitions FROM PUBLISHED/VENDOR_APPROVED unless `force: true`
- [x] AC-US1-02: Blocked transitions log a warning (non-breaking, no throw)
- [x] AC-US1-03: Admin reprocess endpoints (REJECTED→RECEIVED) still work without `force`

### US-002: Pipeline Idempotency (P0)
**As a** platform operator
**I want** `processSubmission()` to skip already-published submissions
**So that** duplicate queue messages don't trigger redundant scans

#### Acceptance Criteria
- [x] AC-US2-01: `processSubmission()` checks current state at start; returns early if PUBLISHED/VENDOR_APPROVED
- [x] AC-US2-02: Early exit logs a message for observability

### US-003: Bulk Restore (P1)
**As an** admin
**I want** a bulk restore endpoint that moves falsely rejected submissions back to PUBLISHED
**So that** I can remediate the ~185 false rejections without re-scanning

#### Acceptance Criteria
- [x] AC-US3-01: `POST /api/v1/admin/submissions/restore-published` finds submissions with PUBLISHED in state history but current state REJECTED
- [x] AC-US3-02: Restores them to PUBLISHED using existing scan data (no re-scan)
- [x] AC-US3-03: Creates audit trail state events
