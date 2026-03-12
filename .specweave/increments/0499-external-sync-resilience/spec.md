---
increment: 0499-external-sync-resilience
title: "External Sync Resilience & Observability"
type: feature
priority: P1
status: planned
created: 2026-03-12
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# External Sync Resilience & Observability

## Problem Statement

External sync to GitHub/JIRA/ADO fails silently. When `syncToExternalTools()` encounters a rate limit, network error, or provider outage, the error is caught and logged to stderr but never surfaced to the user. The sync fires on every task completion regardless of whether meaningful progress occurred, generating unnecessary API calls. There is no retry mechanism, no persistent failure tracking, and no CLI tool to detect or remediate sync gaps.

## Goals

- Reduce unnecessary external sync calls by only syncing when an AC transitions to completed
- Persist failed syncs for automatic retry with exponential backoff
- Surface sync errors prominently in the dashboard with real-time updates
- Provide CLI commands for sync health monitoring and gap remediation
- Maintain backward compatibility for tasks without AC tags

## User Stories

### US-001: AC-Gated External Sync (P1)
**Project**: specweave
**As a** SpecWeave user
**I want** external sync to fire only when an acceptance criterion becomes fully satisfied
**So that** I avoid unnecessary API calls and rate limit consumption on every task completion

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a task is completed but no new ACs transitioned from unchecked to checked, when `onTaskCompleted()` runs, then `syncToExternalTools()` is NOT called
- [x] **AC-US1-02**: Given a task completion causes one or more ACs to transition from `[ ]` to `[x]`, when `onTaskCompleted()` runs, then `syncToExternalTools()` IS called with the affected user story IDs
- [x] **AC-US1-03**: Given any task is completed, when `onTaskCompleted()` runs, then living docs sync (`LivingDocsSync.syncIncrement`) still fires regardless of AC state changes
- [x] **AC-US1-04**: Given a task has no AC tags (legacy or unlinked tasks), when that task is completed, then external sync fires on every completion for backward compatibility

---

### US-002: Sync Retry Queue with Smart Rate Limiting (P1)
**Project**: specweave
**As a** SpecWeave user
**I want** failed external syncs to be persisted and retried automatically
**So that** transient failures (network errors, rate limits, provider outages) do not result in permanently lost sync state

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given an external sync fails, when the error is caught, then a retry entry is persisted to `.specweave/state/sync-retry-queue.json` with incrementId, provider, error message, attempt count, and next retry timestamp
- [ ] **AC-US2-02**: Given a GitHub sync is about to execute, when `RateLimitChecker.shouldProceed()` returns `canProceed: false`, then the sync call is queued in the retry queue instead of attempted
- [ ] **AC-US2-03**: Given a provider's `SyncCircuitBreaker` is in `open` state, when a sync is requested for that provider, then the sync is queued instead of attempted
- [ ] **AC-US2-04**: Given the user runs `specweave sync-retry`, when there are entries in the retry queue, then each entry is retried with exponential backoff intervals (1 minute, 5 minutes, 30 minutes)
- [ ] **AC-US2-05**: Given an increment transitions to `completed`, when `onIncrementDone()` executes, then the retry queue is processed for that increment before closure completes
- [ ] **AC-US2-06**: Given any sync attempt occurs (success or failure), when the attempt completes, then a JSONL audit entry is appended to `.specweave/state/sync-audit.jsonl` with timestamp, incrementId, provider, outcome, and error details
- [ ] **AC-US2-07**: Given a retry entry has reached 3 failed attempts, when `sync-retry` processes it, then the entry is marked `failed` and remains in the queue for manual review (not retried automatically)
- [ ] **AC-US2-08**: Given the rate limiter has checked a provider's status, when a subsequent check occurs within 60 seconds, then the cached status is used instead of re-checking headers

---

### US-003: Dashboard Sync Error Display (P1)
**Project**: specweave
**As a** SpecWeave user viewing the dashboard
**I want** sync errors to be prominently displayed with real-time updates
**So that** I am immediately aware of sync failures and can take corrective action

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given sync errors occurred in the last 24 hours, when the user views the OverviewPage, then a "Recent Sync Errors" panel is visible showing up to 5 recent errors with provider name, increment ID, error message, and timestamp
- [ ] **AC-US3-02**: Given an external sync fails, when the failure is recorded, then an SSE event of type `sync-error` is broadcast to all connected dashboard clients
- [ ] **AC-US3-03**: Given an external sync fails, when the failure is recorded, then a notification entry is written to `.specweave/state/notifications.json` with severity `error`
- [ ] **AC-US3-04**: Given the user navigates to the SyncPage, when sync errors exist, then each error row is expandable to show the full error message and stack trace
- [ ] **AC-US3-05**: Given increments with incomplete provider coverage exist, when the user views the OverviewPage, then a sync gap count badge is displayed showing the number of increments with missing provider syncs

---

### US-004: Sync Gap Detection CLI (P1)
**Project**: specweave
**As a** SpecWeave user
**I want** CLI commands to detect and remediate sync gaps
**So that** I can verify all increments are properly synced to configured providers and fix any that are not

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given the user runs `specweave sync-gaps`, when increments have metadata with partial provider coverage (e.g., synced to GitHub but not JIRA), then each gap is listed with increment ID, synced providers, and missing providers
- [ ] **AC-US4-02**: Given the user runs `specweave sync-gaps --fix`, when gaps are detected, then the command attempts the missing provider syncs for each listed increment
- [ ] **AC-US4-03**: Given the user runs `specweave sync-gaps --json`, when gaps exist, then the output is a valid JSON array with objects containing incrementId, syncedProviders, missingProviders, and lastSyncTimestamp
- [ ] **AC-US4-04**: Given the user runs `specweave sync-status`, when the sync infrastructure is active, then the output shows retry queue depth, per-provider circuit breaker state, and rate limit remaining counts
- [ ] **AC-US4-05**: Given the user runs `specweave sync-gaps` or `specweave sync-status`, when issues are found, then the command exits with a non-zero exit code

## Out of Scope

- Webhook-based real-time sync (push from providers back to SpecWeave)
- Multi-user conflict resolution for concurrent syncs
- Provider-specific retry strategies (all providers use the same backoff)
- Historical sync analytics or trend reporting
- Dashboard UI for manually triggering retries (CLI-only for now)

## Technical Notes

### Dependencies
- `SyncCircuitBreaker` (exists at `src/core/increment/sync-circuit-breaker.ts`) -- wire as per-provider singletons
- `RateLimitChecker` (exists at `src/core/cache/rate-limit-checker.ts`) -- integrate into sync flow
- `LifecycleHookDispatcher` (exists at `src/core/hooks/LifecycleHookDispatcher.ts`) -- modify `onTaskCompleted()`
- `ac-progress-sync.ts` -- existing AC state parsing infrastructure
- Dashboard SSE manager (`src/dashboard/server/sse-manager.ts`) -- new `sync-error` event type
- Dashboard notifications system (`notifications.json`)

### Constraints
- Retry queue file must not exceed 1MB (auto-prune entries older than 7 days)
- JSONL audit file must rotate at 5MB
- AC state comparison must be O(n) where n = number of ACs in the spec
- All new CLI commands must complete within 10 seconds for increments with up to 500 tasks

### Architecture Decisions
- **File-based persistence** for retry queue and audit log (no database dependency, consistent with existing SpecWeave state management)
- **Per-provider circuit breakers** rather than a single global breaker, so GitHub outage does not block JIRA sync
- **AC-gating at the dispatcher level** (`onTaskCompleted`) rather than deep in provider code, keeping provider sync functions unaware of gating logic

## Success Metrics

- Zero silent sync failures (all failures either retried or surfaced to user)
- 70%+ reduction in unnecessary external API calls (AC-gating)
- Retry queue resolves 90%+ of transient failures within 3 attempts
- Sync gap detection catches 100% of missing provider syncs
