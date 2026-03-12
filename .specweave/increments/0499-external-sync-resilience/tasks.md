---
increment: 0499-external-sync-resilience
title: "External Sync Resilience & Observability"
status: planned
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004, T-005, T-006, T-007]
  US-003: [T-008, T-009, T-010]
  US-004: [T-011, T-012, T-013]
---

# Tasks: External Sync Resilience & Observability

## Implementation Order
- Phase 1 (US-002 core): T-003 → T-004 → T-005 → T-006 → T-007
- Phase 2 (US-001, parallel with Phase 1): T-001 → T-002
- Phase 3 (US-003 dashboard): T-008 → T-009 → T-010
- Phase 4 (US-004 CLI): T-011 → T-012 → T-013

---

## User Story: US-001 — AC-Gated External Sync

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

### T-001: Implement ACGate module

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a completed task whose AC checkboxes did not change state
- **When** `ACGate.shouldSyncExternal()` is called with spec and tasks content
- **Then** it returns `{ shouldSync: false, transitionedACs: [], affectedStoryIds: [] }`

- **Given** a completed task that caused one AC to transition from `[ ]` to `[x]`
- **When** `ACGate.shouldSyncExternal()` is called
- **Then** it returns `{ shouldSync: true, transitionedACs: ['AC-US1-02'], affectedStoryIds: ['US-001'] }`

- **Given** a task with no AC tags
- **When** `ACGate.shouldSyncExternal()` is called
- **Then** it returns `{ shouldSync: true, transitionedACs: [], affectedStoryIds: [] }` (backward compat)

**Test Cases**:
1. **Unit**: `src/core/sync/__tests__/ac-gate.test.ts`
   - `testNoACTransition_returnsShouldSyncFalse()`: mock spec/tasks with unchanged ACs
   - `testACTransition_returnsShouldSyncTrue()`: one AC flips from unchecked to checked
   - `testMultipleACTransitions_returnsAllAffectedStories()`: two ACs across two user stories
   - `testNoACTags_returnsShouldSyncTrue()`: task block has no AC-* references
   - `testAllACsAlreadyChecked_returnsShouldSyncFalse()`: no net new transitions
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/core/sync/ac-gate.ts`
2. Define `ACGateResult`: `{ shouldSync: boolean; transitionedACs: string[]; affectedStoryIds: string[] }`
3. Implement `ACGate.shouldSyncExternal(specContent: string, tasksContent: string, taskId: string): ACGateResult`
4. Use existing `ACStatusManager.parseSpecForACs()` to extract AC checkbox states from spec content
5. Use existing `ACStatusManager.parseTasksForACStatus()` to compute which ACs are now satisfied
6. Compare before/after states: any AC transitioning from unchecked to checked triggers sync
7. If task has no AC-* references in its task block, return `shouldSync: true` (AC-US1-04)
8. Run tests: `npx vitest run src/core/sync/__tests__/ac-gate.test.ts`

---

### T-002: Wire ACGate into LifecycleHookDispatcher.onTaskCompleted()

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a task completion with no AC transitions
- **When** `onTaskCompleted()` runs
- **Then** `LivingDocsSync.syncIncrement` IS called AND `SyncResilience.syncWithResilience` is NOT called

- **Given** a task completion with AC transitions
- **When** `onTaskCompleted()` runs
- **Then** both `LivingDocsSync.syncIncrement` AND `SyncResilience.syncWithResilience` are called

- **Given** a task with no AC tags
- **When** `onTaskCompleted()` runs
- **Then** `SyncResilience.syncWithResilience` IS called (backward compatibility)

**Test Cases**:
1. **Unit**: `src/core/hooks/__tests__/lifecycle-hook-dispatcher-ac-gate.test.ts`
   - `testOnTaskCompleted_noACTransition_skipsExternalSync()`: verify syncWithResilience not called
   - `testOnTaskCompleted_ACTransition_callsExternalSync()`: verify syncWithResilience is called
   - `testOnTaskCompleted_alwaysCallsLivingDocsSync()`: living docs fires regardless of AC state
   - `testOnTaskCompleted_legacyTask_callsExternalSync()`: no AC tags → external sync fires
   - **Coverage Target**: 90%

**Implementation**:
1. Locate `LifecycleHookDispatcher.onTaskCompleted()` in `src/core/hooks/LifecycleHookDispatcher.ts`
2. Before calling external sync, read spec.md and tasks.md content for the increment
3. Call `ACGate.shouldSyncExternal(specContent, tasksContent, taskId)`
4. If `result.shouldSync === false`: skip external sync, log at debug level (AC-US1-01)
5. If `result.shouldSync === true`: call `SyncResilience.syncWithResilience()` (replaces raw `syncToExternalTools()`)
6. Ensure `LivingDocsSync.syncIncrement()` is NOT gated — always fires (AC-US1-03)
7. Wire `onIncrementDone()` to drain retry queue after closure sync (prerequisite for T-007)
8. Run tests: `npx vitest run src/core/hooks/__tests__/lifecycle-hook-dispatcher-ac-gate.test.ts`

---

## User Story: US-002 — Sync Retry Queue with Smart Rate Limiting

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08
**Tasks**: 5 total, 0 completed

### T-003: Implement SyncRetryQueue and SyncResilienceAuditLogger

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-06, AC-US2-07
**Status**: [x] completed

**Test Plan**:
- **Given** a failed sync for increment "0499-test" on provider "github"
- **When** `SyncRetryQueue.enqueue()` is called
- **Then** an entry is persisted to `.specweave/state/sync-retry-queue.json` with all required schema fields

- **Given** a retry entry has `attemptCount === 3` (maxAttempts)
- **When** `SyncRetryQueue.markFailed()` is called for it
- **Then** the entry status becomes "failed" and it remains in the queue for manual review

- **Given** a sync operation completes
- **When** `SyncResilienceAuditLogger.append()` is called
- **Then** a JSONL line is appended to `.specweave/state/sync-audit.jsonl` with all required fields

- **Given** `sync-audit.jsonl` has reached 5MB
- **When** the next `append()` call is made
- **Then** the file is rotated to `sync-audit.jsonl.1` and a new `sync-audit.jsonl` begins

**Test Cases**:
1. **Unit**: `src/core/sync/__tests__/sync-retry-queue.test.ts`
   - `testEnqueue_writesEntryWithCorrectSchema()`: validate all required fields present
   - `testEnqueue_exponentialBackoff_nextRetryAt()`: verify 1m → 5m → 30m windows
   - `testPrune_removesEntriesOlderThan7Days()`: inject stale entries, verify removal
   - `testMarkFailed_setsStatusFailed_doesNotRemove()`: entry persists with failed status
   - `testEnqueue_cap100Entries_prunesOldest()`: inject 101 entries, verify cap enforced
   - `testAtomicWrite_usesTempFileThenRename()`: verify write-to-temp pattern
   - **Coverage Target**: 95%

2. **Unit**: `src/core/sync/__tests__/sync-resilience-audit-logger.test.ts`
   - `testAppend_writesValidJSONLLine()`: parse appended line, verify schema
   - `testRotate_at5MB_renamesFile()`: mock fs stat returning 5MB, verify rotation
   - `testReadRecent_filtersBy24Hours()`: inject entries spanning 48h window
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/core/sync/sync-retry-queue.ts`
   - Define `RetryEntry` interface (id, incrementId, provider, featureId, projectPath, projectName, error, attemptCount, maxAttempts, status, createdAt, nextRetryAt, lastAttemptAt)
   - `enqueue(params)`: read queue file, add new entry, prune (7 days + 100 cap), atomic write via temp file rename
   - Exponential backoff: attempt 1 → nextRetryAt = now + 1m; attempt 2 → +5m; attempt 3 → +30m
   - `dequeue(id)`, `getByIncrement(incrementId)`, `getByProvider(provider)`, `markFailed(id)`, `remove(id)`, `prune()`, `getAll()`, `size()`
2. Create `src/core/sync/sync-resilience-audit-logger.ts` (separate from existing `SyncAuditLogger`)
   - File: `.specweave/state/sync-audit.jsonl`; schema: timestamp, incrementId, provider, outcome, error?, errorStack?, durationMs?, attemptNumber?
   - `append(entry)`: check file size, rotate if >= 5MB, then appendFile
   - `readRecent(hours)`: read file lines, parse JSON, filter by timestamp within window
   - `rotate()`: rename `.jsonl` to `.jsonl.1`, remove `.jsonl.2` if it exists
3. Run tests: `npx vitest run src/core/sync/__tests__/sync-retry-queue.test.ts src/core/sync/__tests__/sync-resilience-audit-logger.test.ts`

---

### T-004: Implement CachedRateLimiter and CircuitBreakerRegistry

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-08
**Status**: [x] completed

**Test Plan**:
- **Given** a rate limit check was cached 30 seconds ago
- **When** `CachedRateLimiter.canProceed()` is called again
- **Then** the cached result is returned without calling the underlying `GitHubRateLimiter`

- **Given** a rate limit check was cached 61 seconds ago
- **When** `CachedRateLimiter.canProceed()` is called
- **Then** `GitHubRateLimiter.checkRateLimit()` is called again and cache is refreshed

- **Given** no circuit breaker exists for provider "jira"
- **When** `CircuitBreakerRegistry.get("jira")` is called
- **Then** a new closed-state `SyncCircuitBreaker` is lazy-created and stored

- **Given** a "github" circuit breaker is in "open" state
- **When** `circuitBreakerRegistry.get("github").canSync()` is called
- **Then** it returns false

**Test Cases**:
1. **Unit**: `src/core/sync/__tests__/cached-rate-limiter.test.ts`
   - `testCacheHit_within60s_doesNotCallUnderlying()`: mock time, assert no re-fetch within TTL
   - `testCacheMiss_after60s_callsUnderlying()`: advance fake timer past TTL
   - `testCanProceed_delegatesToCachedStatus()`: verify result matches underlying response
   - **Coverage Target**: 90%

2. **Unit**: `src/core/sync/__tests__/circuit-breaker-registry.test.ts`
   - `testGet_lazyCreatesBreaker()`: first call creates instance, second returns same
   - `testGetAll_returnsStateMap()`: verify all registered providers included
   - `testReset_clearsBreakerFromMap()`: after reset, next get creates fresh breaker
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/core/sync/cached-rate-limiter.ts`
   - Wraps `GitHubRateLimiter` (from plugin) with injectable dependency for testing
   - Cache field: `{ status: RateLimitStatus; cachedAt: number } | null`
   - `canProceed(estimatedCalls)`: check if `Date.now() - cachedAt < 60_000`; if stale, call `GitHubRateLimiter.checkRateLimit()` and cache result; delegate `canProceed` logic
2. Create `src/core/sync/circuit-breaker-registry.ts`
   - Private `Map<string, SyncCircuitBreaker>` — activates existing dead-code module
   - `get(provider)`: lazy-create `new SyncCircuitBreaker(provider)` if absent
   - `getAll()`: return `Map<string, CircuitBreakerState>`
   - `reset(provider)`: delete from map
   - Export singleton `circuitBreakerRegistry`
3. Run tests: `npx vitest run src/core/sync/__tests__/cached-rate-limiter.test.ts src/core/sync/__tests__/circuit-breaker-registry.test.ts`

---

### T-005: Implement SyncResilience facade

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-06
**Status**: [x] completed

**Test Plan**:
- **Given** the circuit breaker for "github" is open
- **When** `SyncResilience.syncWithResilience({ provider: "github", ... })` is called
- **Then** `syncToExternalTools()` is NOT called, a retry entry is enqueued, audit records "skipped_circuit_open"

- **Given** the rate limiter returns `canProceed: false`
- **When** `SyncResilience.syncWithResilience()` is called for GitHub
- **Then** sync is not attempted, retry is enqueued, audit records "skipped_rate_limit"

- **Given** `syncToExternalTools()` throws a network error
- **When** `SyncResilience.syncWithResilience()` is called
- **Then** error is caught, retry enqueued, audit records "failure", method returns without throwing

- **Given** `syncToExternalTools()` succeeds
- **When** `SyncResilience.syncWithResilience()` is called
- **Then** circuit breaker records success, audit records "success", returns `{ ok: true }`

**Test Cases**:
1. **Integration**: `src/core/sync/__tests__/sync-resilience.test.ts`
   - `testCircuitOpen_enqueuesRetry_doesNotCallSync()`: inject open circuit breaker mock
   - `testRateLimitExceeded_enqueuesRetry_doesNotCallSync()`: inject rate limiter returning false
   - `testSyncFailure_enqueuesRetry_writesAuditEntry()`: syncToExternalTools throws
   - `testSyncSuccess_recordsSuccessOnBreaker_writesAuditEntry()`: happy path
   - `testSyncResilience_neverThrows_alwaysReturnsResult()`: any scenario → no throw
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/core/sync/sync-resilience.ts`
2. Define `SyncResilienceResult`: `{ ok: boolean; skipped?: string; error?: string }`
3. Define `SyncResilienceParams`: `{ incrementId, provider, featureId, projectPath, projectName, storyIds }`
4. Class accepts injected deps: `CircuitBreakerRegistry`, `CachedRateLimiter`, `SyncRetryQueue`, `SyncResilienceAuditLogger`, `NotificationManager`
5. `syncWithResilience(params)`: entire body in try/catch, returns `SyncResilienceResult` (never throws)
   - Pre-flight check: `circuitBreakerRegistry.get(provider).canSync()` → if false: enqueue, audit "skipped_circuit_open", return
   - Pre-flight check: if provider === "github", `cachedRateLimiter.canProceed(1)` → if false: enqueue, audit "skipped_rate_limit", return
   - Time the call: record `startMs = Date.now()`
   - Call existing `syncToExternalTools(...)`, capture durationMs
   - On success: `breaker.recordSuccess()`, audit "success" with durationMs
   - On failure (catch): `breaker.recordFailure()`, enqueue retry, audit "failure", write notification, return `{ ok: false }`
6. Run tests: `npx vitest run src/core/sync/__tests__/sync-resilience.test.ts`

---

### T-006: Add SSE sync-error event type and notification wiring

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-06
**Status**: [x] completed

**Test Plan**:
- **Given** `SyncResilience` records a retryable sync failure
- **When** the failure path executes
- **Then** `NotificationManager.addNotification()` is called with `severity: "warning"`

- **Given** a retry entry reaches maxAttempts and is marked "failed"
- **When** `sync-retry` processes it
- **Then** `NotificationManager.addNotification()` is called with `severity: "critical"`

- **Given** `'sync-error'` is added to the SSEEventType union
- **When** `sseManager.broadcast({ type: 'sync-error', ... })` is called
- **Then** TypeScript accepts it without type errors

**Test Cases**:
1. **Unit**: `src/dashboard/__tests__/sse-sync-error-type.test.ts`
   - `testSSEEventType_syncError_acceptedByTypeSystem()`: type assertion compile check
   - `testSyncResilience_writesWarningNotification_onRetryableFailure()`: mock NotificationManager
   - `testSyncRetry_writesCriticalNotification_onMaxAttemptExhaustion()`: mock NotificationManager
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/dashboard/types.ts`, add `'sync-error'` to the `SSEEventType` union
2. In `SyncResilience` failure path: call `NotificationManager.addNotification({ severity: 'warning', title: 'Sync failed', ... })`
3. In `sync-retry` command when marking entry as failed: call `NotificationManager.addNotification({ severity: 'critical', ... })`
4. Dashboard FileWatcher monitors `.specweave/state/notifications.json` and broadcasts SSE to clients — no direct IPC needed
5. Run type check: `npx tsc --noEmit`
6. Run tests: `npx vitest run src/dashboard/__tests__/sse-sync-error-type.test.ts`

---

### T-007: Wire retry queue drain into onIncrementDone() and implement sync-retry command

**User Story**: US-002
**Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US2-07
**Status**: [x] completed

**Test Plan**:
- **Given** the retry queue has 2 pending entries for increment "0499-test"
- **When** `onIncrementDone("0499-test")` executes
- **Then** both entries are attempted before closure completes

- **Given** a retry entry with `nextRetryAt` in the future
- **When** `specweave sync-retry` is run
- **Then** that entry is NOT attempted (skipped)

- **Given** a retry entry has `attemptCount === 3` after a failed attempt
- **When** `sync-retry` processes it
- **Then** entry is marked "failed" (status: "failed") and not retried further

**Test Cases**:
1. **Unit**: `src/core/hooks/__tests__/lifecycle-hook-dispatcher-retry-drain.test.ts`
   - `testOnIncrementDone_drainsRetryQueue_forThisIncrement()`: mock retryQueue.getByIncrement, verify each called
   - `testOnIncrementDone_drainFailure_doesNotBlockClosure()`: drain throws, closure still proceeds

2. **Unit**: `src/cli/commands/__tests__/sync-retry.test.ts`
   - `testSyncRetry_skipsEntriesNotYetDue()`: nextRetryAt in future → not attempted
   - `testSyncRetry_attemptsEntriesDue()`: nextRetryAt in past → SyncResilience called
   - `testSyncRetry_marksFailedAtMaxAttempts()`: attempt 3 fails → markFailed called
   - `testSyncRetry_exits0_whenQueueEmpty()`: empty queue → exit code 0
   - **Coverage Target**: 90%

**Implementation**:
1. In `LifecycleHookDispatcher.onIncrementDone()`: after closure sync, call `syncRetryQueue.getByIncrement(incrementId)` and attempt each pending entry via `SyncResilience.syncWithResilience()`; wrap entire drain in try/catch
2. Create `src/cli/commands/sync-retry.ts`
   - Read pending entries where `status === 'pending' && nextRetryAt <= now`
   - For each: call `SyncResilience.syncWithResilience()`
   - On failure and `entry.attemptCount >= entry.maxAttempts`: call `retryQueue.markFailed(entry.id)`
   - Otherwise: increment `attemptCount`, update `nextRetryAt` via backoff, update `lastAttemptAt`
   - Exit code 1 if any retries failed; exit code 0 if all succeeded or queue empty
3. Register `sync-retry` in CLI command router
4. Run tests: `npx vitest run src/core/hooks/__tests__/lifecycle-hook-dispatcher-retry-drain.test.ts src/cli/commands/__tests__/sync-retry.test.ts`

---

## User Story: US-003 — Dashboard Sync Error Display

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 3 total, 0 completed

### T-008: Add dashboard data endpoints for sync errors and sync gaps

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** `sync-audit.jsonl` contains 3 failure entries within the last 24 hours
- **When** `GET /api/:project/sync-errors` is called
- **Then** a JSON array of up to 5 entries is returned with provider, incrementId, error, and timestamp

- **Given** an increment metadata shows synced to "github" only but "jira" is also configured
- **When** `GET /api/:project/sync-gaps` is called
- **Then** a gap entry is returned with incrementId, syncedProviders: ["github"], missingProviders: ["jira"]

**Test Cases**:
1. **Unit**: `src/dashboard/server/data/__tests__/dashboard-data-aggregator-sync.test.ts`
   - `testGetSyncErrors_returnsRecentFailures()`: mock audit file with mixed outcomes
   - `testGetSyncErrors_limitsTo5Results()`: 10 failure entries → only 5 returned
   - `testGetSyncGaps_detectsMissingProviders()`: mock metadata with partial provider coverage
   - `testGetSyncGaps_returnsEmpty_whenAllProvidersSynced()`: all providers present → empty array
   - **Coverage Target**: 90%

**Implementation**:
1. Add `getSyncErrors(projectPath, hours?)` to `src/dashboard/server/data/dashboard-data-aggregator.ts`
   - Reads from `SyncResilienceAuditLogger.readRecent(24)`, filters to outcome "failure", returns up to 5 most recent
2. Add `getSyncGaps(projectPath)` to the same aggregator
   - Scan active increment `metadata.json` files; load configured providers from `config.json`
   - Compare `metadata.syncedProviders` against configured set; return gap objects
3. Add `GET /api/:project/sync-errors` route in `src/dashboard/server/dashboard-server.ts` calling `getSyncErrors()`
4. Add `GET /api/:project/sync-gaps` route calling `getSyncGaps()`
5. In dashboard FileWatcher handler: when `sync-audit.jsonl` changes, broadcast `{ type: 'sync-error' }` SSE event (AC-US3-02)
6. Run tests: `npx vitest run src/dashboard/server/data/__tests__/dashboard-data-aggregator-sync.test.ts`

---

### T-009: OverviewPage — Recent Sync Errors panel and sync gap badge

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** the API returns 3 sync errors from the last 24 hours
- **When** OverviewPage renders
- **Then** a "Recent Sync Errors" panel is visible showing provider, incrementId, message, and timestamp for each

- **Given** 2 increments have sync gaps
- **When** OverviewPage renders
- **Then** a badge displays "2 sync gaps"

- **Given** no sync errors and no gaps exist
- **When** OverviewPage renders
- **Then** the errors panel and gap badge are not rendered

**Test Cases**:
1. **Unit**: `src/dashboard/client/src/__tests__/OverviewPage-sync.test.tsx`
   - `testRecentSyncErrorsPanel_visibleWhenErrorsExist()`: mock API with errors, assert panel rendered
   - `testRecentSyncErrorsPanel_hiddenWhenNoErrors()`: empty API response, assert panel absent
   - `testSyncGapBadge_showsCountWhenGapsExist()`: mock gaps response with 2 entries
   - `testSyncGapBadge_hiddenWhenNoGaps()`: empty gaps response, assert badge absent
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/dashboard/client/src/pages/OverviewPage.tsx`:
   - Add `useSyncErrors()` hook fetching `/api/:project/sync-errors` on mount and on SSE `sync-error` event
   - Add `useSyncGaps()` hook fetching `/api/:project/sync-gaps` on mount
   - Render "Recent Sync Errors" panel (conditional on `syncErrors.length > 0`): rows with provider badge, incrementId, truncated error, relative timestamp
   - Render sync gap badge near page title (conditional on `syncGaps.length > 0`): shows count with link to SyncPage
2. Subscribe to SSE `sync-error` events to refresh errors panel in real time
3. Run tests: `npx vitest run src/dashboard/client/src/__tests__/OverviewPage-sync.test.tsx`

---

### T-010: SyncPage — Expandable error rows

**User Story**: US-003
**Satisfies ACs**: AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** sync errors are listed on SyncPage
- **When** the user clicks an error row
- **Then** the row expands to show full error message and stack trace (first 3 lines)

- **Given** an expanded error row
- **When** the user clicks it again
- **Then** the row collapses

**Test Cases**:
1. **Unit**: `src/dashboard/client/src/__tests__/SyncPage-expandable.test.tsx`
   - `testErrorRow_expandsOnClick()`: simulate click, assert expanded content is visible
   - `testErrorRow_collapsesOnSecondClick()`: two clicks, assert content returns to hidden
   - `testErrorRow_showsFullMessageAndStack()`: verify errorStack field rendered when present
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/dashboard/client/src/pages/SyncPage.tsx`:
   - Fetch sync errors via `/api/:project/sync-errors`
   - Add `expandedErrorId: string | null` local state
   - Render error rows; clicking a row toggles `expandedErrorId`
   - When expanded: show full `error` text in `<pre>` block and `errorStack` lines if available
   - Use existing CSS classes for expand/collapse pattern (no new stylesheets)
2. Run tests: `npx vitest run src/dashboard/client/src/__tests__/SyncPage-expandable.test.tsx`

---

## User Story: US-004 — Sync Gap Detection CLI

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 3 total, 0 completed

### T-011: Implement sync-gaps CLI command

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** one increment is synced to "github" only but "jira" is also configured
- **When** `specweave sync-gaps` is run
- **Then** output lists the increment with syncedProviders=["github"] and missingProviders=["jira"]

- **Given** `--json` flag is passed with gaps present
- **When** `specweave sync-gaps --json` is run
- **Then** stdout is a valid JSON array with objects containing incrementId, syncedProviders, missingProviders, lastSyncTimestamp

- **Given** `--fix` flag is passed with gaps detected
- **When** `specweave sync-gaps --fix` is run
- **Then** missing provider syncs are attempted for each gap increment via SyncResilience

- **Given** gaps exist in any mode
- **When** the command finishes
- **Then** process exits with code 1

**Test Cases**:
1. **Unit**: `src/cli/commands/__tests__/sync-gaps.test.ts`
   - `testSyncGaps_listsGaps_humanReadable()`: mock metadata, assert text output includes incrementId and provider names
   - `testSyncGaps_jsonFlag_outputsValidJSON()`: parse stdout as JSON, validate all required fields
   - `testSyncGaps_fixFlag_callsSyncResilienceForEachGap()`: mock SyncResilience, verify called per gap
   - `testSyncGaps_noGaps_exits0()`: all providers synced → exit code 0
   - `testSyncGaps_gapsExist_exits1()`: gaps detected → exit code 1
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/cli/commands/sync-gaps.ts`
2. Parse flags: `--fix` (boolean), `--json` (boolean)
3. Scan `.specweave/increments/*/metadata.json` for all active increments
4. Load configured sync providers from `config.json` using existing `SyncConfigValidator`
5. For each increment: compare `metadata.syncedProviders[]` against configured providers → collect gap objects
6. Output: if `--json` → print JSON array; else print formatted list
7. If `--fix`: for each gap, call `SyncResilience.syncWithResilience()` for each missing provider
8. Exit code 1 if gaps found (with or without `--fix`), exit code 0 if no gaps
9. Register command in CLI router
10. Run tests: `npx vitest run src/cli/commands/__tests__/sync-gaps.test.ts`

---

### T-012: Implement sync-status CLI command

**User Story**: US-004
**Satisfies ACs**: AC-US4-04, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** retry queue has 3 pending entries, github circuit is closed, jira circuit is open
- **When** `specweave sync-status` is run
- **Then** output shows "Retry queue: 3 pending", "github: closed", "jira: open"

- **Given** any circuit breaker is in "open" state
- **When** `specweave sync-status` is run
- **Then** process exits with code 1

- **Given** no issues (empty queue, all circuits closed, adequate rate limit)
- **When** `specweave sync-status` is run
- **Then** process exits with code 0

**Test Cases**:
1. **Unit**: `src/cli/commands/__tests__/sync-status.test.ts`
   - `testSyncStatus_showsRetryQueueDepth()`: mock queue returning 3 entries
   - `testSyncStatus_showsCircuitBreakerStates()`: mock registry with mixed states
   - `testSyncStatus_showsGitHubRateLimitInfo()`: mock CachedRateLimiter with remaining count
   - `testSyncStatus_exits1_whenAnyIssueDetected()`: open circuit → exit 1
   - `testSyncStatus_exits0_whenAllHealthy()`: all clear → exit 0
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/cli/commands/sync-status.ts`
2. Read retry queue depth via `syncRetryQueue.size()` (count pending entries)
3. Read circuit breaker states via `circuitBreakerRegistry.getAll()`
4. Read GitHub rate limit via `cachedRateLimiter.canProceed(0)` (status-only check)
5. Print formatted output:
   - "Retry Queue" section: pending count
   - "Circuit Breakers" section: per-provider state (closed/open + time-to-reset for open)
   - "Rate Limits" section: GitHub remaining/limit if GitHub is configured
6. Determine exit code: 1 if queue has pending entries OR any circuit is open OR rate limit critically low; 0 otherwise
7. Register command in CLI router
8. Run tests: `npx vitest run src/cli/commands/__tests__/sync-status.test.ts`

---

### T-013: Register all CLI commands and add graceful missing-file guards

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** a fresh project with no `.specweave/state/` directory
- **When** `specweave sync-status` is run
- **Then** it exits with code 0 without crashing

- **Given** no retry queue file exists
- **When** `specweave sync-retry` is run
- **Then** it treats the queue as empty and exits with code 0

- **Given** all three new commands are registered
- **When** `specweave --help` is run
- **Then** `sync-retry`, `sync-gaps`, and `sync-status` are listed

**Test Cases**:
1. **Integration**: `src/cli/commands/__tests__/sync-commands-integration.test.ts`
   - `testSyncRetry_withMissingQueueFile_exits0()`: no queue file → graceful exit
   - `testSyncGaps_withNoIncrements_exits0()`: empty increments dir → graceful exit
   - `testSyncStatus_withMissingStateDir_exits0()`: no state dir → graceful exit
   - **Coverage Target**: 85%

**Implementation**:
1. Verify `sync-retry`, `sync-gaps`, `sync-status` are registered in `src/cli/cli.ts` (or equivalent CLI entry)
2. Add missing-file guard to `SyncRetryQueue`: if `sync-retry-queue.json` does not exist, return empty queue
3. Add missing-file guard to `SyncResilienceAuditLogger`: if `sync-audit.jsonl` does not exist, `readRecent()` returns `[]`
4. Ensure `.specweave/state/` directory is created on demand in `SyncRetryQueue.enqueue()` and `SyncResilienceAuditLogger.append()`
5. Run integration tests: `npx vitest run src/cli/commands/__tests__/sync-commands-integration.test.ts`
6. Run full test suite: `npx vitest run`
7. Run type check: `npx tsc --noEmit`
