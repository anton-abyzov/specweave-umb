---
id: US-002
feature: FS-499
title: "Sync Retry Queue with Smart Rate Limiting (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** SpecWeave user."
project: specweave
---

# US-002: Sync Retry Queue with Smart Rate Limiting (P1)

**Feature**: [FS-499](./FEATURE.md)

**As a** SpecWeave user
**I want** failed external syncs to be persisted and retried automatically
**So that** transient failures (network errors, rate limits, provider outages) do not result in permanently lost sync state

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given an external sync fails, when the error is caught, then a retry entry is persisted to `.specweave/state/sync-retry-queue.json` with incrementId, provider, error message, attempt count, and next retry timestamp
- [x] **AC-US2-02**: Given a GitHub sync is about to execute, when `RateLimitChecker.shouldProceed()` returns `canProceed: false`, then the sync call is queued in the retry queue instead of attempted
- [x] **AC-US2-03**: Given a provider's `SyncCircuitBreaker` is in `open` state, when a sync is requested for that provider, then the sync is queued instead of attempted
- [x] **AC-US2-04**: Given the user runs `specweave sync-retry`, when there are entries in the retry queue, then each entry is retried with exponential backoff intervals (1 minute, 5 minutes, 30 minutes)
- [x] **AC-US2-05**: Given an increment transitions to `completed`, when `onIncrementDone()` executes, then the retry queue is processed for that increment before closure completes
- [x] **AC-US2-06**: Given any sync attempt occurs (success or failure), when the attempt completes, then a JSONL audit entry is appended to `.specweave/state/sync-audit.jsonl` with timestamp, incrementId, provider, outcome, and error details
- [x] **AC-US2-07**: Given a retry entry has reached 3 failed attempts, when `sync-retry` processes it, then the entry is marked `failed` and remains in the queue for manual review (not retried automatically)
- [x] **AC-US2-08**: Given the rate limiter has checked a provider's status, when a subsequent check occurs within 60 seconds, then the cached status is used instead of re-checking headers

---

## Implementation

**Increment**: [0499-external-sync-resilience](../../../../../increments/0499-external-sync-resilience/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Implement SyncRetryQueue and SyncResilienceAuditLogger
- [x] **T-004**: Implement CachedRateLimiter and CircuitBreakerRegistry
- [x] **T-005**: Implement SyncResilience facade
- [x] **T-006**: Add SSE sync-error event type and notification wiring
- [x] **T-007**: Wire retry queue drain into onIncrementDone() and implement sync-retry command
