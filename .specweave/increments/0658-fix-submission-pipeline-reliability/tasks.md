---
increment: 0658-fix-submission-pipeline-reliability
title: "Fix Submission Pipeline Reliability"
type: bug
priority: P1
status: planned
test_mode: TDD
---

# Tasks: Fix Submission Pipeline Reliability

## US-001: Dedup Staleness for Pending States

### T-001: Write failing tests for pending staleness in submission-dedup
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed
**Test**: Given `src/lib/__tests__/submission-dedup.test.ts` with mocked DB — When tests are run before implementation — Then all pending-staleness assertions fail (RED), confirming the bug exists

Scenarios to write (all must fail before T-002/T-003/T-004):
- RECEIVED submission with `updatedAt` 5h ago → expects `kind:"new"`
- TIER1_SCANNING submission with `updatedAt` 30min ago → expects `kind:"pending"`
- Custom `stalePendingHours: 2` config + 3h-old RECEIVED → expects `kind:"new"`
- `DEFAULT_STALE_PENDING_HOURS` constant exported and equals 4
- Batch: 3 submissions (stale pending 5h, fresh pending 1h, new) → correct kinds per item

---

### T-002: Add DEFAULT_STALE_PENDING_HOURS constant and DedupConfig.stalePendingHours
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05
**Status**: [x] completed
**Test**: Given `src/lib/submission-dedup.ts` after this change — When `buildDedupConfig()` is called without env var — Then `stalePendingHours` defaults to 4; when `DEDUP_STALE_PENDING_HOURS=2` is set — Then it uses 2

- Add `export const DEFAULT_STALE_PENDING_HOURS = 4` (~line 29)
- Add `stalePendingHours?: number` to `DedupConfig` interface (~line 15)
- Add `stalePendingHours: parseEnvNumber(e.DEDUP_STALE_PENDING_HOURS as string)` in `buildDedupConfig()` (~line 45)

---

### T-003: Implement PENDING staleness gate in checkSubmissionDedup() and getStalenessHours()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05
**Status**: [x] completed
**Test**: Given a RECEIVED submission with `updatedAt` 5h ago — When `checkSubmissionDedup()` is called — Then it returns `{ kind: "new" }`; given same 30min ago → returns `{ kind: "pending" }`

- In `getStalenessHours()` (~line 51-58): add PENDING_STATES check returning `config?.stalePendingHours ?? DEFAULT_STALE_PENDING_HOURS` before the fallback return
- In `checkSubmissionDedup()` (~line 82-85): before returning `{ kind: "pending" }`, call `isStale(existing.updatedAt, existing.state, config)`; if stale, return `{ kind: "new" }`

---

### T-004: Implement PENDING staleness gate in checkSubmissionDedupBatch()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] completed
**Test**: Given 3 submissions — stale pending (5h), fresh pending (1h), new — When `checkSubmissionDedupBatch()` is called — Then stale pending → `{ kind: "new" }`, fresh pending → `{ kind: "pending" }`, new → `{ kind: "new" }`

- In `checkSubmissionDedupBatch()` (~line 182-184): before `results.set(name, { kind: "pending" })`, call `isStale()` on the existing record
- If stale, fall through to `needsSkillCheck` path instead of setting "pending"

---

## US-002: Queue Send Failure Fallback

### T-005: Write failing tests for queue send fallback in submissions route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed
**Test**: Given route tests with `SUBMISSION_QUEUE.send` mocked to throw — When tests run before implementation — Then assertions for inline fallback, warning log, unchanged API response, and double-failure RECEIVED state all fail (RED)

Scenarios to write:
- Queue send throws → `pendingProcessing` contains the submission item
- Queue send throws → `console.warn` called with submission ID and fallback message
- Queue send throws → API response still returns RECEIVED submission with correct metadata
- Queue send throws AND `processSubmission()` throws → both errors logged, submission stays RECEIVED

---

### T-006: Lift pendingProcessing scope and implement single queue send fallback
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given `SUBMISSION_QUEUE.send()` throws — When POST /submissions handler runs — Then submission is pushed to `pendingProcessing`, a `console.warn` is emitted with the submission ID, and the API response is unchanged (RECEIVED state, correct metadata)

- Lift `pendingProcessing` declaration to outer scope before `if (isBatch)` branch (~line 666)
- In single send catch (~line 821-826): replace `console.error` with `console.warn`, push `{ submissionId, skillName, skillPath }` to `pendingProcessing`
- Guard `waitUntil()` block (~line 844-876) with `if (pendingProcessing.length > 0)` so it handles both normal and fallback items

---

### T-007: Implement batch send fallback and double-failure error handling
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04
**Status**: [x] completed
**Test**: Given `SUBMISSION_QUEUE.sendBatch()` throws for a chunk — When handler catches error — Then all chunk items are pushed to `pendingProcessing`; given inline `processSubmission()` also throws → both errors logged, submission stays RECEIVED for recovery pickup

- In batch send catch (~line 743-748): iterate failed `chunk`, push each `{ submissionId, skillName, skillPath }` to `pendingProcessing`; log `console.warn` with chunk size and IDs
- In inner `processSubmission()` catch within `waitUntil()`: log both queue and inline error reasons without changing DB state

---

## US-003: Reduce RECEIVED Recovery Threshold

### T-008: Write failing tests for RECEIVED staleness threshold reduction
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Test**: Given `src/lib/__tests__/submission-store.test.ts` with time-mocked DB — When tests run before constant change — Then 20-min-old RECEIVED submission is NOT yet detected (test asserts it IS), confirming RED state

Scenarios to write:
- RECEIVED at 20min → detected by `getStaleReceivedSubmissions()` (currently FALSE, expects TRUE)
- RECEIVED at 10min → NOT detected (expects FALSE — should pass after fix too)
- 24h+ RECEIVED → auto-rejected (unchanged behavior, expect same result)
- 3 prior re-enqueue attempts → auto-rejected by retry budget (unchanged)
- After re-enqueue `updatedAt` touch → next cron run at <15min does NOT re-enqueue again

---

### T-009: Reduce STALE_RECEIVED_THRESHOLD_MS from 2 hours to 15 minutes
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Test**: Given a RECEIVED submission with `updatedAt` 20 minutes ago — When `getStaleReceivedSubmissions()` runs with the updated constant — Then the submission is included in results (15-min threshold crossed, bug fixed)

- In `src/lib/submission-store.ts` (~line 1618): change `2 * 60 * 60 * 1000` to `15 * 60 * 1000`
- Update inline comment to: `// 15 minutes — aligned with STUCK_THRESHOLD_MS for consistent recovery`
- No other changes: `VERY_OLD_RECEIVED_MS`, `MAX_STALE_RETRIES`, and `recoverStaleReceived()` logic remain identical
