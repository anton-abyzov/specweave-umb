# Implementation Plan: External Sync Resilience & Observability

## Overview

This increment adds resilience and observability to SpecWeave's external sync pipeline (GitHub/JIRA/ADO). Four capabilities are introduced: (1) AC-gated sync that eliminates unnecessary API calls by only triggering external sync when acceptance criteria transition to complete, (2) a persistent retry queue with per-provider circuit breakers and rate limiting, (3) dashboard sync error display with real-time SSE updates, and (4) CLI commands for sync gap detection and remediation.

The design activates two existing dead-code modules (`SyncCircuitBreaker`, `RateLimitChecker`) and wraps `syncToExternalTools()` in a new `SyncResilience` facade that handles pre-flight checks, error capture, retry persistence, and audit logging. The non-blocking contract (AC-US5-05) is preserved: all new logic lives outside the living docs sync path.

## Architecture

### System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    LifecycleHookDispatcher                        │
│                                                                  │
│  onTaskCompleted()                  onIncrementDone()            │
│       │                                   │                      │
│       ▼                                   ▼                      │
│  ┌─────────────┐                    ┌──────────────┐            │
│  │ AC Gate     │──── no change ────▶│ Drain retry  │            │
│  │ (new)       │                    │ queue for     │            │
│  └──────┬──────┘                    │ increment     │            │
│         │ AC transitioned?          └──────┬───────┘            │
│         │                                  │                     │
│    yes  │  no (+ has AC tags)              │                     │
│    │    │  → skip external sync            │                     │
│    ▼    ▼                                  ▼                     │
│  ┌──────────────────────────────────────────────┐               │
│  │              SyncResilience                   │               │
│  │  ┌────────────────┐  ┌───────────────────┐   │               │
│  │  │ CircuitBreaker │  │ CachedRateLimiter │   │               │
│  │  │ Registry       │  │ (60s TTL)         │   │               │
│  │  │ (per provider) │  │ (GitHub only)     │   │               │
│  │  └───────┬────────┘  └────────┬──────────┘   │               │
│  │          │ canSync()?         │ canProceed()? │               │
│  │          ▼                    ▼               │               │
│  │  ┌────────────────────────────────────┐      │               │
│  │  │   syncToExternalTools() [existing] │      │               │
│  │  └─────────────┬──────────────────────┘      │               │
│  │                │                              │               │
│  │         success│failure                       │               │
│  │           │    │                              │               │
│  │           ▼    ▼                              │               │
│  │  ┌─────────┐ ┌──────────────┐                │               │
│  │  │ Record  │ │ Enqueue      │                │               │
│  │  │ success │ │ retry entry  │                │               │
│  │  └────┬────┘ └──────┬───────┘                │               │
│  │       │             │                         │               │
│  │       ▼             ▼                         │               │
│  │  ┌──────────────────────────────────────┐    │               │
│  │  │         SyncAuditLogger              │    │               │
│  │  │  → .specweave/state/sync-audit.jsonl │    │               │
│  │  └──────────────────────────────────────┘    │               │
│  │       │             │                         │               │
│  │       ▼             ▼                         │               │
│  │  ┌──────────────────────────────────────┐    │               │
│  │  │  NotificationManager (on failure)    │    │               │
│  │  │  → notifications.json               │    │               │
│  │  │  → SSE broadcast: sync-error         │    │               │
│  │  └──────────────────────────────────────┘    │               │
│  └──────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────┘

  CLI Layer:
  ┌────────────────────┐  ┌──────────────────────┐
  │ specweave sync-gaps│  │ specweave sync-status │
  │ specweave sync-gaps│  │ specweave sync-retry  │
  │   --fix / --json   │  │                       │
  └────────────────────┘  └──────────────────────┘
```

### Components

#### 1. ACGate (new: `src/core/sync/ac-gate.ts`)

Determines whether external sync should fire after a task completion by comparing AC state before and after the edit.

- Reads `spec.md` to extract current AC checkbox state via `ACStatusManager.parseSpecForACs()`
- Reads `tasks.md` to compute which ACs would now be complete via `ACStatusManager.parseTasksForACStatus()`
- Returns `{ shouldSync: boolean, transitionedACs: string[], affectedStoryIds: string[] }`
- For tasks with no AC tags (legacy/unlinked), returns `shouldSync: true` for backward compatibility (AC-US1-04)

#### 2. SyncResilience (new: `src/core/sync/sync-resilience.ts`)

Facade that wraps `syncToExternalTools()` with pre-flight checks and post-sync bookkeeping.

- Holds a `Map<string, SyncCircuitBreaker>` keyed by provider name (`github`, `jira`, `ado`)
- Holds a `CachedRateLimiter` instance (wraps `GitHubRateLimiter` with 60s TTL cache)
- Pre-flight: checks circuit breaker state, checks rate limiter (GitHub only)
- If blocked: enqueues to retry queue instead of calling sync
- On success: records success on circuit breaker, appends audit entry
- On failure: records failure on circuit breaker, enqueues retry, appends audit entry, writes notification, broadcasts SSE event

#### 3. SyncRetryQueue (new: `src/core/sync/sync-retry-queue.ts`)

File-based retry queue persisted to `.specweave/state/sync-retry-queue.json`.

- JSON format (not JSONL) for random access by incrementId or provider
- Capped at 100 entries; auto-prunes entries older than 7 days on every write
- Schema per entry:
  ```
  id            string      UUID
  incrementId   string      e.g. "0499-external-sync-resilience"
  provider      string      "github" | "jira" | "ado"
  featureId     string      e.g. "FS-499"
  projectPath   string      path to project living docs
  projectName   string      project name for sync target resolution
  error         string      error message from failed sync
  attemptCount  number      starts at 1
  maxAttempts   number      3
  status        string      "pending" | "failed"
  createdAt     string      ISO timestamp
  nextRetryAt   string      ISO timestamp (exponential: 1m, 5m, 30m)
  lastAttemptAt string      ISO timestamp
  ```
- Methods: `enqueue()`, `dequeue()`, `getByIncrement()`, `getByProvider()`, `markFailed()`, `remove()`, `prune()`, `getAll()`, `size()`

#### 4. SyncAuditLogger (new: `src/core/sync/sync-audit-logger.ts`)

Append-only JSONL audit log at `.specweave/state/sync-audit.jsonl`.

- Rotates at 5MB (renames to `sync-audit.jsonl.1`, keeps at most 2 rotated files)
- Schema per line:
  ```
  timestamp     string      ISO timestamp
  incrementId   string
  provider      string
  outcome       string      "success" | "failure" | "skipped_circuit_open" | "skipped_rate_limit" | "retry_enqueued"
  error         string?     error message (failures only)
  durationMs    number?     sync duration
  ```
- Methods: `append()`, `readRecent(hours: number)`, `rotate()`

#### 5. CachedRateLimiter (new: `src/core/sync/cached-rate-limiter.ts`)

Thin wrapper around `GitHubRateLimiter` that caches the `checkRateLimit()` result for 60 seconds (AC-US2-08).

- On first call or after TTL expiry: delegates to `GitHubRateLimiter.checkRateLimit()` and caches result
- On subsequent calls within TTL: returns cached `RateLimitStatus`
- `canProceed(estimatedCalls)` wraps `GitHubRateLimiter.canProceed()` using cached status
- Only applies to GitHub provider; JIRA/ADO rate limits are detected via response headers in `RateLimitChecker`

#### 6. CircuitBreakerRegistry (new: `src/core/sync/circuit-breaker-registry.ts`)

Singleton map of per-provider `SyncCircuitBreaker` instances.

- `get(provider: string): SyncCircuitBreaker` -- lazy-creates per provider
- `getAll(): Map<string, CircuitBreakerState>` -- for CLI status display
- `reset(provider: string)` -- manual reset for admin use

#### 7. Dashboard Extensions

**OverviewPage** (modify: `src/dashboard/client/src/pages/OverviewPage.tsx`):
- Add "Recent Sync Errors" panel showing up to 5 recent errors from sync-audit.jsonl
- Add sync gap count badge (number of increments with incomplete provider coverage)

**SyncPage** (modify: `src/dashboard/client/src/pages/SyncPage.tsx`):
- Add expandable error rows with full error message and stack trace

**SSE** (modify: `src/dashboard/types.ts`):
- Add `'sync-error'` to `SSEEventType` union

**Dashboard Server** (modify: `src/dashboard/server/dashboard-server.ts`):
- Add API endpoint `GET /api/:project/sync-errors` returning recent audit entries
- Add API endpoint `GET /api/:project/sync-gaps` returning sync gap analysis

**Data Aggregator** (modify: `src/dashboard/server/data/dashboard-data-aggregator.ts`):
- Add `getSyncErrors()` method reading from `sync-audit.jsonl`
- Add `getSyncGaps()` method scanning increment metadata for incomplete provider coverage

#### 8. CLI Commands

**sync-retry** (new: `src/cli/commands/sync-retry.ts`):
- Processes all pending retry queue entries with exponential backoff
- Entries at max attempts are marked `failed`, not retried
- Exits with code 1 if any retries failed

**sync-gaps** (new: `src/cli/commands/sync-gaps.ts`):
- Scans all active increment `metadata.json` files
- Compares synced providers against configured providers from config.json sync profiles
- `--fix` flag: attempts missing syncs
- `--json` flag: outputs JSON array
- Exits with code 1 if gaps found

**sync-status** (new: `src/cli/commands/sync-status.ts`):
- Shows: retry queue depth, per-provider circuit breaker state, GitHub rate limit remaining
- Exits with code 1 if any issues detected

### Data Model

#### sync-retry-queue.json

```
┌──────────────────────────────────────────────────────────────────┐
│                     sync-retry-queue.json                        │
├──────────────┬──────────┬────────────────────────────────────────┤
│ Field        │ Type     │ Description                            │
├──────────────┼──────────┼────────────────────────────────────────┤
│ version      │ number   │ Schema version (1)                     │
│ entries[]    │ array    │ Retry queue entries                    │
│  .id         │ string   │ UUID                                   │
│  .incrementId│ string   │ Increment full ID                      │
│  .provider   │ string   │ github | jira | ado                    │
│  .featureId  │ string   │ FS-XXX                                 │
│  .projectPath│ string   │ Path to living docs project dir        │
│  .projectName│ string   │ Project name for sync target           │
│  .error      │ string   │ Error message from failed attempt      │
│  .attemptCount│ number  │ Current attempt number (1-3)           │
│  .maxAttempts│ number   │ Max retry count (3)                    │
│  .status     │ string   │ pending | failed                       │
│  .createdAt  │ string   │ ISO 8601 creation timestamp            │
│  .nextRetryAt│ string   │ ISO 8601 next eligible retry time      │
│  .lastAttemptAt│ string │ ISO 8601 last attempt timestamp        │
│ lastPruned   │ string   │ ISO 8601 last prune timestamp          │
└──────────────┴──────────┴────────────────────────────────────────┘

Max entries: 100 (oldest pruned first)
Max age: 7 days (auto-pruned on write)
Max file size: 1MB (enforced by 100-entry cap)
```

#### sync-audit.jsonl

```
┌──────────────────────────────────────────────────────────────────┐
│                      sync-audit.jsonl                            │
│                   (one JSON object per line)                     │
├──────────────┬──────────┬────────────────────────────────────────┤
│ Field        │ Type     │ Description                            │
├──────────────┼──────────┼────────────────────────────────────────┤
│ timestamp    │ string   │ ISO 8601 timestamp                     │
│ incrementId  │ string   │ Increment ID                           │
│ provider     │ string   │ github | jira | ado                    │
│ outcome      │ string   │ success | failure | skipped_circuit_   │
│              │          │ open | skipped_rate_limit |             │
│              │          │ retry_enqueued                          │
│ error        │ string?  │ Error message (failures only)          │
│ errorStack   │ string?  │ Stack trace (first 3 lines)            │
│ durationMs   │ number?  │ Sync duration in milliseconds          │
│ attemptNumber│ number?  │ Retry attempt number (if retry)        │
└──────────────┴──────────┴────────────────────────────────────────┘

Max size: 5MB (rotates to .jsonl.1, max 2 rotated files)
```

### Data Flow

1. **Task Completion (happy path with AC transition)**:
   - Shell hook `task-ac-sync-guard.sh` fires, marks ACs in spec.md, spawns `specweave sync-task <id>`
   - `sync-task` calls `LifecycleHookDispatcher.onTaskCompleted()`
   - `onTaskCompleted()` runs `LivingDocsSync.syncIncrement()` (living docs always sync)
   - NEW: Before calling `syncToExternalTools()`, `ACGate.shouldSyncExternal()` checks if any AC transitioned
   - If AC transitioned: `SyncResilience.syncWithResilience()` is called
   - `SyncResilience` checks circuit breaker, checks rate limiter
   - If all clear: calls existing `syncToExternalTools()`, records outcome
   - If blocked or failed: enqueues retry, writes notification, broadcasts SSE

2. **Task Completion (no AC transition)**:
   - Same as above but `ACGate.shouldSyncExternal()` returns `false`
   - External sync is skipped; living docs sync still runs

3. **Increment Done**:
   - `onIncrementDone()` runs normally (living docs + closure sync)
   - NEW: After closure sync, drains retry queue for this increment
   - Any remaining pending entries are attempted one final time

4. **Manual Retry**:
   - User runs `specweave sync-retry`
   - Reads retry queue, filters entries where `nextRetryAt <= now && status === 'pending'`
   - For each: checks circuit breaker, attempts sync, updates queue

## Technology Stack

- **Language**: TypeScript (ESM, consistent with codebase)
- **Runtime**: Node.js (consistent with specweave CLI)
- **Libraries**: None new -- reuses `fs`, `path`, `crypto` (for UUID), existing `SyncCircuitBreaker`, `GitHubRateLimiter`, `RateLimitChecker`, `ACStatusManager`, `NotificationManager`
- **Dashboard**: React (existing), SSE (existing `SSEManager`)

## Architecture Decisions

### AD-1: AC-gating at the dispatcher level, not inside providers

**Decision**: The AC transition check happens in `LifecycleHookDispatcher.onTaskCompleted()` before `syncToExternalTools()` is called, rather than inside each provider sync method.

**Rationale**: Provider sync methods (`syncToGitHub`, `syncToJira`, `syncToADO`) should remain unaware of gating logic. This keeps them reusable for manual sync operations (`sync-gaps --fix`, `sync-retry`) where AC-gating does not apply.

### AD-2: Retry queue as JSON with random access, not JSONL

**Decision**: Use a JSON file with an array of entries, not JSONL append-only.

**Rationale**: Retry queue needs random access by incrementId and provider (to check for duplicates, to drain by increment on closure). JSONL would require full-file scan for lookups. At max 100 entries, the JSON file remains small (well under 1MB) and can be atomically rewritten safely.

### AD-3: Per-provider circuit breakers via in-memory singletons

**Decision**: Circuit breakers are in-memory per process, not file-persisted.

**Rationale**: Circuit breaker state is transient by design -- a 5-minute reset timeout makes persistence unnecessary. If the CLI process restarts, the circuit breaker resets to closed, which is the desired behavior (gives the provider another chance). File persistence would add complexity for no benefit.

### AD-4: SyncResilience as a facade wrapping syncToExternalTools()

**Decision**: Rather than modifying `syncToExternalTools()` internals, a new `SyncResilience` facade wraps the call with pre-flight checks and post-sync bookkeeping.

**Rationale**: `syncToExternalTools()` is a 80-line method with permission checks, tool detection, and per-provider dispatch. Modifying it would increase its complexity. The facade pattern preserves the existing method unchanged and layers resilience concerns around it.

### AD-5: CachedRateLimiter wraps GitHubRateLimiter, does not modify it

**Decision**: The 60-second cache is implemented as a new wrapper class rather than modifying `GitHubRateLimiter` in the plugin directory.

**Rationale**: `GitHubRateLimiter` lives in `plugins/specweave-github/lib/` and is a plugin-owned module. Core sync code should not depend directly on plugin internals. The wrapper in `src/core/sync/` provides the caching layer and can be used without the plugin if GitHub is not configured.

### AD-6: Notification severity is `error` (not `critical`) for sync failures

**Decision**: Sync failure notifications use `severity: 'error'`, not `'critical'`.

**Rationale**: Looking at existing `NotificationSeverity` type, only `'info' | 'warning' | 'critical'` are defined. We need to use the existing type. Sync failures that will be auto-retried should be `'warning'`. Sync failures that have exhausted retries should be `'critical'`. This maps naturally to the existing severity levels.

## Implementation Phases

### Phase 1: Core Infrastructure (US-002 foundations)

1. **SyncRetryQueue**: File-based queue with enqueue/dequeue/prune
2. **SyncAuditLogger**: JSONL append with rotation
3. **CachedRateLimiter**: 60s TTL wrapper around GitHubRateLimiter
4. **CircuitBreakerRegistry**: Per-provider singleton map (activating existing `SyncCircuitBreaker`)
5. **SyncResilience facade**: Orchestrates pre-flight + sync + post-sync

### Phase 2: AC-Gating (US-001)

6. **ACGate**: AC transition detection using ACStatusManager
7. **LifecycleHookDispatcher modification**: Wire ACGate into `onTaskCompleted()`, preserve living docs sync, add retry queue drain in `onIncrementDone()`

### Phase 3: Dashboard & SSE (US-003)

8. **SSE sync-error event type**: Add to types, wire broadcast on failure
9. **Dashboard data endpoints**: Sync errors API, sync gaps API
10. **OverviewPage panel**: "Recent Sync Errors" + sync gap badge
11. **SyncPage expansion**: Expandable error rows

### Phase 4: CLI Commands (US-004)

12. **sync-retry command**: Process retry queue with backoff
13. **sync-gaps command**: Detect and optionally fix missing provider syncs
14. **sync-status command**: Show queue depth, circuit state, rate limits

## Testing Strategy

- **Unit tests** (Vitest): Each new module gets a `.test.ts` file testing pure logic. ACGate tested with mock spec/tasks content. SyncRetryQueue tested with temp file I/O. SyncAuditLogger tested with rotation scenarios. CachedRateLimiter tested with time mocking.
- **Integration tests**: SyncResilience facade tested with mocked syncToExternalTools, verifying circuit breaker interactions, retry enqueueing, and audit logging work together.
- **TDD cycle**: RED (write failing test) -> GREEN (minimal implementation) -> REFACTOR. Enforced by config `testing.defaultTestMode: "TDD"`.
- **Coverage target**: 90% (per spec).

## Technical Challenges

### Challenge 1: Non-blocking contract preservation

`syncToExternalTools()` failures must never crash `LivingDocsSync.syncIncrement()`. The existing try/catch at line 1719-1726 of `living-docs-sync.ts` already handles this. The new `SyncResilience` facade adds its own try/catch layer, ensuring a double safety net. The facade returns a result object (never throws) so the dispatcher can inspect the outcome without risk.

**Mitigation**: All new code wrapped in try/catch. `SyncResilience.syncWithResilience()` signature returns `Promise<SyncResilienceResult>` (never rejects).

### Challenge 2: Race condition between AC state read and sync trigger

The shell hook writes AC checkboxes to spec.md before spawning `sync-task`. By the time `ACGate` reads spec.md, the AC state should already be updated. However, in rare cases the file write may not have flushed.

**Mitigation**: `ACGate` re-reads spec.md fresh (no caching) and compares against tasks.md state directly, which is the same approach the shell hook uses. If spec.md has not been flushed yet, the worst case is an unnecessary sync call (not a missed sync), which is acceptable.

### Challenge 3: Retry queue file contention

Multiple concurrent `sync-task` processes could write to `sync-retry-queue.json` simultaneously. This is unlikely in practice (syncs are sequential within an increment) but possible in multi-repo umbrella setups.

**Mitigation**: Use atomic write pattern (write to temp file, rename). The queue is small enough that read-modify-write with rename provides adequate safety. Full file locking is not necessary given the low contention scenario.

### Challenge 4: Dashboard SSE broadcast from CLI process

The CLI process (running `sync-task`) and the dashboard server are separate processes. The CLI cannot directly call `sseManager.broadcast()`.

**Mitigation**: The CLI writes to `notifications.json` and `sync-audit.jsonl`. The dashboard server's `FileWatcher` already monitors `.specweave/state/` for changes. When the audit file changes, the dashboard reads the latest entry and broadcasts a `sync-error` SSE event. No inter-process communication needed.
