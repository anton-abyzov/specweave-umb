---
increment: 0367-stuck-submission-detection
title: "Stuck Submission Detection"
type: feature
priority: P1
status: planned
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Stuck Submission Detection

## Overview

Submissions can get stuck in non-terminal states (RECEIVED, TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED) due to timeouts, transient errors, or worker crashes. The current system runs hourly with a single retry before giving up. This increment upgrades detection to run every 5 minutes, adds a 3-retry budget with exponential backoff, tracks inflight processing stage in KV, classifies timeout/error causes, shows early staleness warnings to users, and pre-aggregates timeout metrics for admin observability.

## User Stories

### US-001: Faster Stuck Detection via 5-Minute Cron (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the cron to run every 5 minutes instead of hourly
**So that** stuck submissions are detected and recovered within minutes rather than waiting up to an hour

**Acceptance Criteria**:
- [x] **AC-US1-01**: wrangler.jsonc cron schedule changed from `0 * * * *` to `*/5 * * * *`
- [x] **AC-US1-02**: All existing cron tasks (npm discovery, recovery, enrichment, stats refresh) continue to run within the 5-minute schedule without exceeding Worker CPU limits
- [x] **AC-US1-03**: Recovery runs every cron tick (no gating or feature flag needed)

---

### US-002: Expanded Retry Budget with Exponential Backoff (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** stuck submissions retried up to 3 times with increasing backoff windows
**So that** transient failures have multiple chances to resolve before permanent rejection

**Acceptance Criteria**:
- [x] **AC-US2-01**: Retry count stored in existing KV key `recovery:retried:{submissionId}` as integer string ("1", "2", "3")
- [x] **AC-US2-04**: After 3 retries exhausted, submission marked REJECTED with descriptive message
- [x] **AC-US2-05**: KV key has 24-hour TTL for automatic cleanup

---

### US-003: Inflight Processing Stage Tracking (P1)
**Project**: vskill-platform

**As a** platform component
**I want** the current processing stage and timestamp tracked in KV during submission processing
**So that** the system knows exactly where a submission is stuck and can report it to users

**Acceptance Criteria**:
- [x] **AC-US3-01**: Consumer writes `inflight:{submissionId}` KV with `{ startedAt, attempt }` before processing
- [x] **AC-US3-02**: Inflight KV key deleted on success or failure (cleanup in both paths)
- [x] **AC-US3-04**: Inflight KV key has TTL of 5 minutes to auto-expire orphaned records

---

### US-004: User-Facing Staleness Warning (P1)
**Project**: vskill-platform

**As a** skill submitter watching my submission
**I want** to see a staleness warning if my submission appears stuck
**So that** I know the platform is aware and working on recovery

**Acceptance Criteria**:
- [x] **AC-US4-01**: Client-side staleness threshold of 3 minutes based on `updatedAt` field
- [x] **AC-US4-03**: Recovery system trigger threshold remains 5 minutes (separate from UX threshold)
- [x] **AC-US4-04**: Staleness warning disappears once the submission progresses or is recovered

---

### US-005: Timeout/Error Classification (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** processing failures classified by root cause
**So that** I can identify systemic issues (e.g., GitHub API outage vs AI model failures)

**Acceptance Criteria**:
- [x] **AC-US5-01**: Timeout errors distinguished from other failures via error message pattern matching
- [x] **AC-US5-04**: Consumer catch block classifies timeout vs other before calling `recordTimeout()` or `recordFailed()`

---

### US-006: Admin Timeout Metrics (P2)
**Project**: vskill-platform

**As an** admin reviewing queue health
**I want** pre-aggregated timeout metrics broken down by classification
**So that** I can spot trends without expensive on-the-fly queries

**Acceptance Criteria**:
- [x] **AC-US6-01**: Timeout metrics stored in existing `QUEUE_METRICS_KV` hourly buckets via `timedOut` field (backward-compatible)
- [x] **AC-US6-02**: `recordTimeout(kv, durationMs)` function increments both `failed` and `timedOut` on bucket and totals
- [x] **AC-US6-03**: Admin queue status API extended with `totalTimedOut` in throughput and `timedOut` in recentHours
- [ ] **AC-US6-04**: Hourly bucket KV keys have 48-hour TTL for automatic cleanup

## Functional Requirements

### FR-001: Cron Schedule Change
Change wrangler.jsonc `crons` from `["0 * * * *"]` to `["*/5 * * * *"]`. All cron body tasks (stats refresh, DB prewarm, npm discovery, recovery, enrichment) remain sequential within `ctx.waitUntil`. The npm/enrichment workloads are lightweight enough to run every 5 minutes.

### FR-002: Retry Budget KV Schema
```
Key:   recovery:budget:{submissionId}
Value: {"count": 2, "lastRetryAt": "2026-02-24T12:00:00Z", "nextRetryAfter": "2026-02-24T12:15:00Z"}
TTL:   86400 (24 hours)
```
Backoff schedule: `[180, 600, 1800]` seconds (3min, 10min, 30min). Recovery reads the budget, checks `now >= nextRetryAfter`, increments count, computes next window, and re-enqueues. When `count >= 3`, marks REJECTED with `STUCK_EXHAUSTED`.

### FR-003: Inflight KV Schema
```
Key:   inflight:{submissionId}
Value: {"stage": "TIER1_SCANNING", "startedAt": "ISO", "submissionId": "sub_xxx"}
TTL:   3600 (1 hour)
```
Written by `updateState()` or a wrapper when state transitions to a non-terminal scanning state. Deleted on terminal state. On error, augmented with `{"error": {"classification": "SCAN_TIMEOUT", "message": "Timeout after 55000ms"}}`.

### FR-004: Error Classification Utility
```typescript
type TimeoutClassification = "SCAN_TIMEOUT" | "NETWORK_ERROR" | "DB_ERROR" | "LLM_ERROR" | "UNKNOWN";

function classifyError(error: unknown): TimeoutClassification;
```
Pattern matching: `withTimeout` rejection message -> `SCAN_TIMEOUT`; fetch/TypeError/AbortError -> `NETWORK_ERROR`; Prisma errors -> `DB_ERROR`; Workers AI / `@cloudflare/ai` errors -> `LLM_ERROR`; default -> `UNKNOWN`.

### FR-005: Dual Threshold Design
- **UX threshold (3 min)**: Used by submission status endpoint to add `staleness` field to response. Read from inflight KV. Informational only.
- **Recovery threshold (5 min)**: Used by `getStuckSubmissions()` DB query. Triggers actual re-enqueue. Already exists (STUCK_THRESHOLD_MS = 5 * 60 * 1000).

## Success Criteria

- Stuck submissions detected within 5 minutes (down from up to 60 minutes)
- Users see staleness warning within 3 minutes of a stuck submission
- 3x retry budget gives transient failures 43 minutes of recovery window
- Admin dashboard shows timeout breakdown by classification per hour
- No increase in Worker CPU time beyond Cloudflare free tier limits

## Out of Scope

- User-facing notifications (email/push) for stuck submissions
- Automatic scaling of retry budget based on error classification
- Admin UI for timeout metrics (API only in this increment)
- Changes to the DLQ (dead letter queue) consumer
- Submission detail page staleness indicator (future increment)

## Dependencies

- Increment 0365 (Queue Position UX) -- completed, provides the positions endpoint and queue page infrastructure
- Existing `QUEUE_METRICS_KV` and `SUBMISSIONS_KV` bindings
- Existing `recovery.ts` module (will be extended)
- Existing `consumer.ts` and `process-submission.ts` (will be extended with classification)
