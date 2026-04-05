---
increment: 0658-fix-submission-pipeline-reliability
title: Fix Submission Pipeline Reliability
type: bug
priority: P1
status: completed
created: 2026-04-05T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix Submission Pipeline Reliability

## Overview

Three compounding bugs create a permanent submission deadlock where skills stuck in RECEIVED state can never be resubmitted. All 111,344 published skills are affected — any requiring resubmission could hit this deadlock.

Concrete case: submission `sub_311375ff` for skill "anymodel" has been stuck in RECEIVED since 2026-04-05T00:36:20.898Z with no recovery path.

**Root cause chain**: Queue send fails silently (Bug B) -> submission stuck in RECEIVED -> recovery ignores RECEIVED for 2 hours (Bug C) -> even after recovery, dedup blocks resubmission forever because pending states have no staleness (Bug A).

## User Stories

### US-001: Dedup Staleness for Pending States (P1)
**Project**: vskill-platform

**As a** skill publisher
**I want** stuck pending submissions to become stale after a configurable timeout
**So that** I can resubmit my skill when a prior submission is permanently stuck in a pending state

**Context**: `checkSubmissionDedup()` in `src/lib/submission-dedup.ts:82-85` returns `kind:"pending"` immediately for all PENDING_STATES (RECEIVED, TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED, VENDOR_APPROVED) with zero staleness check. Published has 24h, Rejected has 48h, Blocked has 0h (permanent) — but PENDING has no staleness at all. Once stuck, resubmission is blocked forever.

**Acceptance Criteria**:
- [x] **AC-US1-01**: Pending submissions older than the configurable staleness threshold (default 4 hours) are treated as stale, allowing resubmission
  - Given a submission in RECEIVED state with `updatedAt` 5 hours ago
  - When `checkSubmissionDedup()` is called for the same repoUrl + skillName
  - Then it returns `{ kind: "new" }` instead of `{ kind: "pending" }`
- [x] **AC-US1-02**: Pending submissions within the staleness window still block resubmission
  - Given a submission in TIER1_SCANNING state with `updatedAt` 30 minutes ago
  - When `checkSubmissionDedup()` is called for the same repoUrl + skillName
  - Then it returns `{ kind: "pending" }` as before
- [x] **AC-US1-03**: The staleness threshold for pending states is configurable via `DedupConfig.stalePendingHours`
  - Given a `DedupConfig` with `stalePendingHours: 2`
  - When a submission has been in RECEIVED state for 3 hours
  - Then `checkSubmissionDedup()` returns `{ kind: "new" }`
- [x] **AC-US1-04**: Batch dedup (`checkSubmissionDedupBatch()`) applies the same pending staleness logic
  - Given 3 submissions: one pending 5h (stale), one pending 1h (fresh), one new
  - When `checkSubmissionDedupBatch()` is called
  - Then the stale pending returns `{ kind: "new" }`, fresh pending returns `{ kind: "pending" }`, new returns `{ kind: "new" }`
- [x] **AC-US1-05**: The `DEFAULT_STALE_PENDING_HOURS` constant is set to 4 hours
  - Given no explicit `stalePendingHours` in config
  - When staleness is checked for a pending submission
  - Then the 4-hour default is used

---

### US-002: Queue Send Failure Fallback (P1)
**Project**: vskill-platform

**As a** skill publisher
**I want** my submission to be processed even when the Cloudflare queue is unavailable
**So that** submissions are never silently dropped when the queue fails

**Context**: `src/app/api/v1/submissions/route.ts:811-826` catches `SUBMISSION_QUEUE.send()` errors but only logs them. The submission is already created in DB as RECEIVED and returned to the caller as "created", but it's never enqueued — it becomes a ghost submission with no processing path.

**Acceptance Criteria**:
- [x] **AC-US2-01**: When queue send fails, the submission falls back to inline processing via `waitUntil()`
  - Given the queue send throws an error
  - When the POST /submissions handler catches the error
  - Then the submission is added to `pendingProcessing` for inline `waitUntil()` processing
- [x] **AC-US2-02**: The fallback is logged as a warning so operators can detect queue degradation
  - Given the queue send fails and fallback is triggered
  - When the error is handled
  - Then a warning is logged indicating queue failure and inline fallback activation, including the submission ID
- [x] **AC-US2-03**: The API response is unchanged — the caller still receives the submission as created
  - Given the queue send fails
  - When the fallback processes inline
  - Then the API response still includes the submission with state RECEIVED and correct metadata
- [x] **AC-US2-04**: If both queue send AND inline processing fail, the submission remains in RECEIVED for recovery cron pickup
  - Given queue send fails AND inline `processSubmission()` also throws
  - When both paths fail
  - Then the error is logged with both failure reasons and the submission stays in RECEIVED state (recovery cron will pick it up)

---

### US-003: Reduce RECEIVED Recovery Threshold (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** submissions stuck in RECEIVED state to be detected within 15 minutes
**So that** the recovery window matches other states and submissions don't wait 2 hours for rescue

**Context**: `getStaleReceivedSubmissions()` in `src/lib/submission-store.ts:1618` uses `STALE_RECEIVED_THRESHOLD_MS = 2 * 60 * 60 * 1000` (2 hours). Meanwhile `getStuckSubmissions()` uses a 15-minute threshold but explicitly excludes RECEIVED from `STUCK_STATES` (line 1515 comment: "RECEIVED removed"). This creates a 2-hour blind spot where RECEIVED items are invisible to all recovery.

**Acceptance Criteria**:
- [x] **AC-US3-01**: RECEIVED submissions are detected as stale after 15 minutes instead of 2 hours
  - Given a submission in RECEIVED state with `updatedAt` 20 minutes ago
  - When `getStaleReceivedSubmissions()` runs
  - Then the submission is included in the results
- [x] **AC-US3-02**: The `STALE_RECEIVED_THRESHOLD_MS` constant is reduced from 2 hours to 15 minutes
  - Given the recovery cron runs
  - When it calls `getStaleReceivedSubmissions()`
  - Then the cutoff is `now - 15 minutes`, not `now - 2 hours`
- [x] **AC-US3-03**: The 24-hour "very old" threshold for auto-rejection remains unchanged
  - Given a RECEIVED submission older than 24 hours
  - When `recoverStaleReceived()` processes it
  - Then it is auto-rejected (not re-enqueued), same as before
- [x] **AC-US3-04**: The retry budget (max 3 attempts) and KV counter logic remain unchanged
  - Given a RECEIVED submission that has been re-enqueued 3 times already
  - When `recoverStaleReceived()` processes it again
  - Then it is auto-rejected due to exhausted retries, same as before
- [x] **AC-US3-05**: The `updatedAt` touch after re-enqueue still prevents re-enqueue loops
  - Given a RECEIVED submission is re-enqueued by recovery
  - When recovery touches `updatedAt` to now
  - Then the next cron run (within 15 min) does not re-enqueue it again

## Functional Requirements

### FR-001: Staleness Check for All Dedup States
The `getStalenessHours()` function must return a configurable staleness window for pending states (default 4h). Both `checkSubmissionDedup()` and `checkSubmissionDedupBatch()` must call `isStale()` for pending state submissions before returning `kind:"pending"`.

### FR-002: Queue Send Resilience
The POST /submissions handler must catch queue send failures and fall back to inline processing via `waitUntil()`, using the same `pendingProcessing` path already used when `useQueue` is false.

### FR-003: Aligned Recovery Thresholds
The RECEIVED state recovery threshold must be reduced to 15 minutes to align with the threshold used for TIER1_SCANNING/TIER2_SCANNING/AUTO_APPROVED states in `recoverStuckSubmissions()`.

## Success Criteria

- Zero permanently-stuck RECEIVED submissions (verified by querying DB for RECEIVED state > 4 hours old)
- Queue send failures produce fallback processing within the same request lifecycle
- Recovery cron detects RECEIVED-stuck items within 15 minutes instead of 2 hours
- Existing dedup behavior for PUBLISHED, REJECTED, and BLOCKED states unchanged
- All existing tests continue to pass

## Out of Scope

- Refactoring the queue/KV dual-write architecture
- Adding new submission states or state machine changes
- UI changes to surface stuck submission status to end users
- Alerting/monitoring infrastructure (operator-facing dashboards)
- Changing the retry budget or auto-rejection logic beyond threshold alignment

## Dependencies

- Cloudflare Workers runtime (queue send, KV operations)
- Prisma DB (submission state queries)
- Existing `processSubmission()` function for inline fallback
- Recovery cron schedule (no changes needed — just threshold values)
