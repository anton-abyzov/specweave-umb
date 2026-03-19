# Architecture Plan: 0549 — External Sync Reliability

## Executive Summary

This increment fixes the end-to-end sync lifecycle across 3 platform plugins (GitHub, JIRA, ADO) in the specweave repo. The work falls into 5 architectural layers: (1) closure hooks wiring, (2) error surfacing pipeline, (3) resilience parity for JIRA/ADO, (4) import-to-increment pipeline fix, and (5) ADO-specific improvements. Each layer reuses existing core infrastructure (circuit breaker, retry queue, lock manager, cached rate limiter) rather than building parallel systems.

---

## Architecture Overview

```
specweave complete <id>
         |
         v
  +------------------+
  | SyncCoordinator  |   existing entry point
  | .syncIncrement   |
  | Completion()     |
  +--------+---------+
           |
  +--------v---------+     +------------------+
  | Living Docs Sync |---->| Format           |
  | (existing)       |     | Preservation     |
  +--------+---------+     +------------------+
           |
  +--------v---------+
  | Closure Hook     |  <-- NEW: post-increment-done
  | Dispatcher       |     dispatches to enabled providers
  +----+----+----+---+
       |    |    |
       v    v    v
     [G]  [J]  [A]    per-provider closure functions
       |    |    |     (reuse existing status sync modules)
       v    v    v
  +--------+---------+
  | Per-Provider      |   circuit breaker + retry + locking
  | Resilience Stack  |   (shared from core)
  +-------------------+
```

---

## ADR Review

The following existing ADRs directly govern this increment's design:

| ADR | Key Decision | Impact on 0549 |
|-----|-------------|----------------|
| ADR-0068 | 7-layer error isolation, circuit breaker pattern | Extend to JIRA/ADO; reuse SyncCircuitBreaker from core |
| ADR-0233 | Platform suffix system (G/J/A/E) | Suffix utility must be shared; enforce in import pipeline |
| ADR-0234 | SyncEngine unified API with ProviderAdapter | SyncEngine exists but is NOT in production (ADR-0240 confirmed); do NOT wire through it |
| ADR-0235 | ProviderAdapter interface | Interface exists; closure hooks use function-map pattern (ADR-0240) NOT adapter classes |
| ADR-0240 | Function-map over adapter interface | Closure hooks follow this pattern: `Record<SyncProvider, ClosureFn>` |
| ADR-0241 | AC checkbox formatter extraction | `ac-checkbox-formatter.ts` already in core; ADO AC sync must use it |
| ADR-0242 | Per-US link extension for JIRA/ADO | `externalLinks.{provider}.userStories[usId]` pattern exists; closure hooks resolve refs from this |
| ADR-0066 | SyncCoordinator as integration point | Closure dispatch originates from SyncCoordinator |
| ADR-0139 | Unified post-increment GitHub sync | GitHub closure already partially wired; JIRA/ADO need same treatment |
| ADR-0163 | Bidirectional sync (hybrid model) | ADO pull sync follows this: push=automatic on /done, pull=manual |

**Critical constraint from ADR-0240**: The codebase has 6 parallel adapter/provider systems. This increment MUST NOT create system #7. All new code uses the function-map pattern with direct calls to existing plugin modules via lazy imports.

---

## Component Design

### Component 1: Closure Hook Dispatcher (US-001)

**Location**: `src/core/closure-dispatcher.ts` (new file, ~150 lines)

**Pattern**: Function-map (ADR-0240), mirroring `ac-progress-sync.ts` structure.

```typescript
type ClosureFn = (
  incrementId: string,
  specPath: string,
  config: ClosureConfig,
) => Promise<ClosureResult>;

const CLOSURE_MAP: Record<SyncProvider, ClosureFn> = {
  github: closeGitHubIssues,
  jira:   closeJiraIssues,
  ado:    closeAdoWorkItems,
};

export async function dispatchClosure(
  incrementId: string,
  specPath: string,
  config: ClosureConfig,
): Promise<ClosureDispatchResult> { ... }
```

Each provider function:
- **GitHub** (`closeGitHubIssues`): Calls `github-us-auto-closer.ts` (existing). Closes issues via GitHub API.
- **JIRA** (`closeJiraIssues`): Calls `JiraStatusSync.updateStatus(issueKey, { state: 'Done' })` (existing). Queries available transitions dynamically (mitigates risk of hardcoded transition IDs).
- **ADO** (`closeAdoWorkItems`): Calls `AdoStatusSync.updateStatus(workItemId, { state: 'Closed' })` (existing). Tries "Done" first, falls back to "Closed" (process-dependent).

**Config gating**: Each provider has a hook toggle:
```json
{
  "hooks": {
    "post_increment_done": {
      "close_github_issue": true,
      "close_jira_issue": true,
      "close_ado_work_item": true
    }
  }
}
```
When toggle is false, that provider is skipped entirely (AC-US1-04).

**Error isolation**: Per-provider try/catch. If GitHub fails but JIRA succeeds, the increment is still closed locally. Failures are collected and reported to stderr (AC-US1-05).

**Integration point**: Called from `SyncCoordinator.syncIncrementCompletion()` after living docs sync, gated behind `canUpdateExternalItems` permission (existing gate).

### Component 2: Error Surfacing Pipeline (US-002)

**Location**: Modifications to existing plugin files, no new module.

**Design**: Replace silent `return false` / `catch (e) { /* swallow */ }` patterns with structured error propagation.

**Changes by file**:

1. `plugins/specweave-github/lib/github-push-sync.ts` -- `checkExistingGitHubIssue()`: Currently returns `false` on HTTP error. Change to throw `SyncError` with HTTP status and message (AC-US2-01).

2. `plugins/specweave-jira/lib/jira-status-sync.ts` -- `updateStatus()`: Currently catches non-2xx silently. Change to throw `SyncError` with JIRA error response body (AC-US2-02).

3. `plugins/specweave-ado/lib/ado-status-sync.ts` -- `updateStatus()`: Currently catches silently. Change to throw `SyncError` with structured line format `[ADO] sync failed: <status> <message>` (AC-US2-03).

4. `src/core/closure-dispatcher.ts` -- `dispatchClosure()`: Collects all provider errors, writes each to stderr separately, sets exit code non-zero when any failure occurs (AC-US2-04).

**Error type** (added to `src/core/errors/sync-error.ts`):
```typescript
export class SyncError extends Error {
  constructor(
    public readonly provider: SyncProvider,
    public readonly httpStatus: number | undefined,
    public readonly responseBody: string | undefined,
    message: string,
  ) {
    super(`[${provider.toUpperCase()}] sync failed: ${httpStatus ?? 'unknown'} ${message}`);
    this.name = 'SyncError';
  }
}
```

### Component 3: Resilience Parity -- Circuit Breaker + Retry for JIRA/ADO (US-003)

**Existing infrastructure to reuse**:
- `src/core/increment/sync-circuit-breaker.ts` -- `SyncCircuitBreaker` class (3 failures, 5min reset, half-open)
- `src/core/sync/circuit-breaker-registry.ts` -- `CircuitBreakerRegistry` (per-provider singletons)
- `src/core/sync/sync-retry-queue.ts` -- `SyncRetryQueue` (file-based, exponential backoff, 100-entry cap, 7-day prune)

**What needs wiring**:

The `ac-progress-sync.ts` already has per-provider circuit breakers (module-level singletons). For the closure dispatcher and the broader sync paths in JIRA/ADO plugins, we wire:

1. **JIRA plugin** -- `jira-spec-sync.ts`, `jira-status-sync.ts`: Wrap API calls in circuit breaker check + retry enqueue on 5xx.
   - Import `CircuitBreakerRegistry` from core
   - Before each API call: `if (!registry.get('jira').canSync()) throw new CircuitOpenError()`
   - On 5xx: `retryQueue.enqueue({ provider: 'jira', ... })`; `registry.get('jira').recordFailure()`
   - On success: `registry.get('jira').recordSuccess()`

2. **ADO plugin** -- `ado-status-sync.ts`, `ado-spec-sync.ts`: Same pattern as JIRA.

3. **Backoff tuning**: Spec requires base 1s, max 30s. The existing `SyncRetryQueue` uses 1m/5m/30m intervals for async recovery. For inline retries within a single sync operation, implement a simple retry wrapper:

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  opts: { maxRetries: number; baseMs: number; maxMs: number },
): Promise<T> {
  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === opts.maxRetries || !isRetryable(err)) throw err;
      const delay = Math.min(opts.baseMs * Math.pow(2, attempt), opts.maxMs);
      await sleep(delay);
    }
  }
  throw new Error('unreachable');
}
```

**Location**: `src/core/sync/retry-wrapper.ts` (~40 lines). Used by both JIRA and ADO sync modules.

### Component 4: JIRA File Locking (US-009)

**Existing infrastructure**: `src/utils/lock-manager.ts` -- `LockManager` class. Already used by GitHub plugin (via SyncCoordinator). Features: mkdir-based atomic lock, 5-minute stale threshold, PID checking, 10-second timeout.

**What needs wiring**: JIRA sync operations must acquire lock before proceeding.

**Implementation**: In `plugins/specweave-jira/lib/jira-spec-sync.ts` (and jira-status-sync.ts), wrap the sync entry points:

```typescript
const lockDir = path.join(projectRoot, '.specweave/state/.jira-sync.lock');
const lock = new LockManager(lockDir, 300, { logger });

if (!(await lock.acquire())) {
  throw new SyncError('jira', undefined, undefined,
    'sync in progress -- lock not acquired after 10s');
}
try {
  // ... existing sync logic
} finally {
  await lock.release();
}
```

This reuses the exact same LockManager that GitHub uses (AC-US9-04). Stale lock recovery at 5 minutes is already built in (AC-US9-03).

### Component 5: ADO Rate Limiting (US-008)

**Existing infrastructure**: `src/core/sync/cached-rate-limiter.ts` -- `CachedRateLimiter` wraps a `RateLimitChecker`. GitHub plugin has `github-rate-limiter.ts` as a concrete checker.

**Design**: Create `ado-rate-limiter.ts` in the ADO plugin implementing the `RateLimitChecker` interface, backed by a token bucket algorithm.

ADO PAT limit: 200 requests/minute. Unlike GitHub (which has `gh api rate_limit`), ADO does not expose a rate limit query endpoint. The rate limiter must be self-tracking.

```typescript
export class AdoRateLimiter implements RateLimitChecker {
  private tokens: number;
  private readonly maxTokens = 200;
  private readonly refillIntervalMs = 60_000; // 1 minute
  private lastRefill: number;

  constructor() {
    this.tokens = this.maxTokens;
    this.lastRefill = Date.now();
  }

  async checkRateLimit(): Promise<RateLimitStatus> {
    this.refill();
    return {
      remaining: this.tokens,
      limit: this.maxTokens,
      resetAt: new Date(this.lastRefill + this.refillIntervalMs),
      percentUsed: Math.round(
        ((this.maxTokens - this.tokens) / this.maxTokens) * 100
      ),
    };
  }

  consume(count: number = 1): boolean {
    this.refill();
    if (this.tokens >= count) {
      this.tokens -= count;
      return true;
    }
    return false;
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = now - this.lastRefill;
    if (elapsed >= this.refillIntervalMs) {
      this.tokens = this.maxTokens;
      this.lastRefill = now;
    }
  }
}
```

**429 handling**: When ADO returns HTTP 429, read `Retry-After` header, wait that duration, then retry (AC-US8-03). Handled in the `withRetry` wrapper from Component 3, with additional checks:

```typescript
function isRetryable(err: unknown): boolean {
  if (err instanceof AxiosError) {
    if (err.response?.status === 429) return true;
    if (err.response && err.response.status >= 500) return true;
  }
  return false;
}

function getRetryDelay(err: unknown): number | undefined {
  if (err instanceof AxiosError && err.response?.status === 429) {
    const retryAfter = err.response.headers['retry-after'];
    if (retryAfter) return parseInt(retryAfter, 10) * 1000;
  }
  return undefined;
}
```

**Integration**: Wrap `AdoClient` and `AdoStatusSync` API calls through the rate limiter's `consume()` before each request, and through `CachedRateLimiter.canProceed()` for batch operations.

### Component 6: Import Creates Increments (US-004)

**Existing infrastructure**: `src/importers/import-to-increment.ts` -- `ImportToIncrementConverter` class already exists. It creates increment directories with `metadata.json`, `spec.md`, `tasks.md` using `createIncrementTemplates()`.

**Current bug**: The import coordinator (`src/importers/import-coordinator.ts`) calls `ExternalImporter.import()` which creates living docs files, NOT increments. The `ImportToIncrementConverter` exists but is not wired into the main import flow.

**Fix**: Wire `ImportToIncrementConverter` into `import-coordinator.ts`:

1. After `ExternalImporter.import()` fetches items, pass them through `ImportToIncrementConverter.importBatch()` instead of (or in addition to) writing living docs.
2. `ImportToIncrementConverter.importBatch()` already handles:
   - Duplicate detection via `IncrementExternalRefDetector` (AC-US4-05)
   - Platform suffix allocation (G/J/A) (AC-US4-01/02/03)
   - Increment ID generation via `IncrementNumberManager`
3. **AC parsing from description** (AC-US4-04): Extend `createIncrementTemplates()` to parse acceptance criteria from the external item's description field. Add `parseExternalACs(description: string, platform: Platform): ACEntry[]` in `src/importers/ac-parser.ts` (~60 lines).
4. **metadata.json external links** (AC-US4-02/03): `ImportToIncrementConverter` already populates `externalLinks` via the `ExternalSourceInfo` parameter. Verify structure matches `externalLinks.{provider}` from ADR-0242.

### Component 7: Platform Suffix Convention (US-005)

**Existing infrastructure**: `src/sync/types.ts` already has `SUFFIX_MAP`:
```typescript
export const SUFFIX_MAP: Record<Platform, PlatformSuffix> = {
  github: 'G', jira: 'J', ado: 'A',
};
```

**What needs fixing**: Some sync modules use inline string concatenation for suffixes instead of the shared utility. Extract a single function:

```typescript
export function formatSuffixedId(
  baseId: string, platform?: Platform
): string {
  if (!platform) return baseId; // local = no suffix
  return `${baseId}${SUFFIX_MAP[platform]}`;
}
```

**Location**: `src/sync/types.ts` (extend existing file, ~10 lines).

**Audit**: Grep for inline suffix concatenation across all 3 plugins and replace with `formatSuffixedId()` calls.

### Component 8: Bidirectional ADO State Sync (US-006)

**Pattern**: Follows ADR-0163 (hybrid bidirectional sync). Push is automatic on `/done`. Pull is manual via `specweave sync pull`.

**Implementation**: Add `pullAdoChanges()` to ADO plugin:

```typescript
async function pullAdoChanges(
  incrementId: string,
  config: AdoSyncConfig,
): Promise<PullResult> {
  const metadata = await loadMetadata(incrementId);
  const adoLinks = metadata.externalLinks?.ado;
  if (!adoLinks) return { updated: false, reason: 'no-ado-link' };

  const adoSync = new AdoStatusSync(
    config.organization, config.project, config.pat
  );
  const adoStatus = await adoSync.getStatus(adoLinks.featureId);
  const mappedStatus = mapAdoStateToSpecweave(adoStatus.state);

  // Last-write-wins by timestamp (AC-US6-03)
  const localModified = new Date(metadata.updatedAt || metadata.createdAt);
  const adoModified = await getAdoWorkItemModifiedDate(
    adoLinks.featureId, config
  );
  if (localModified > adoModified) {
    return { updated: false, reason: 'local-newer' };
  }

  // Permission gate (AC-US6-04)
  if (!config.canUpsertInternalItems) {
    return { updated: false, reason: 'permission-denied' };
  }

  metadata.status = mappedStatus;
  await saveMetadata(incrementId, metadata);
  return { updated: true, oldStatus: metadata.status, newStatus: mappedStatus };
}
```

**State mapping**:

| ADO State | SpecWeave Status |
|-----------|-----------------|
| New | planned |
| Active | active |
| Resolved | active |
| Closed | completed |
| Removed | abandoned |

### Component 9: Replace ADO Regex-Based AC Sync (US-007)

**Current implementation** (in `ado-ac-checkbox-sync.ts` lines 137-170): Uses regex to flip unicode checkboxes in HTML by AC ID. Fragile -- breaks if ADO changes description format or if user manually edits HTML.

**New implementation**: Use ADO REST API's JSON Patch to update the description field with structured section manipulation instead of regex:

1. Fetch current description HTML via `GET /wit/workitems/{id}?fields=System.Description`
2. Parse HTML to identify the "Acceptance Criteria" section (look for heading or section marker)
3. If section exists: replace only the checkbox block within that section using `formatACCheckboxes()` from core (ADR-0241)
4. If section does not exist: append a new section at the end of the description
5. Preserve all non-AC portions of the description unchanged (AC-US7-02)
6. PATCH back via JSON Patch: `[{ "op": "replace", "path": "/fields/System.Description", "value": newHtml }]`

**Backward compatibility** (AC-US7-04): The new implementation reads existing markers to detect current state, then overwrites the entire AC section. Existing work items with old checkbox markup will have their AC section replaced with the new structured format on first sync, which is backward compatible because the content is preserved.

**Location**: Rewrite `updateStoryCheckboxes()` method in `ado-ac-checkbox-sync.ts` (~80 lines). Add `src/core/ado-description-updater.ts` (~60 lines) for the HTML section manipulation logic.

### Component 10: End-to-End Integration Tests (US-010)

**Test infrastructure** (from spec):
- Real GitHub: `anton-abyzov/specweave` repo
- Real JIRA: SWE2E project on `antonabyzov.atlassian.net`
- Real ADO: `EasyChamp/SpecWeaveSync` project

**Test structure**:
```
tests/
  integration/
    sync/
      github-lifecycle.test.ts       -- create -> sync -> close round-trip
      jira-lifecycle.test.ts         -- create -> sync -> close round-trip
      ado-lifecycle.test.ts          -- create -> sync -> close round-trip
      multi-provider-failure.test.ts -- partial failure isolation
      import-round-trip.test.ts      -- import -> work -> close -> external closure
```

**Test patterns**:
- Each test creates a test increment, syncs it, verifies via API read-back, then cleans up
- Multi-provider failure test mocks one provider (503) while hitting real APIs for others
- All integration tests tagged with `@integration` for separate CI stage
- Retry in test harness (2 attempts with 5s delay) to handle transient API flakiness

**Testability via DI**: All new modules accept their dependencies via constructor/parameters (circuit breaker, retry queue, lock manager, logger). Tests inject mocks. No module-level singletons except where ADR-0240 explicitly calls for them (the provider function map).

---

## Dependency Graph

```
Phase 1 (Foundation - no external deps):
  T-001: SyncError type + retry-wrapper
  T-002: formatSuffixedId utility extraction
  T-003: ADO rate limiter (token bucket)

Phase 2 (Core wiring - depends on Phase 1):
  T-004: Circuit breaker + retry wiring for JIRA
  T-005: Circuit breaker + retry wiring for ADO
  T-006: JIRA file locking integration
  T-007: Error surfacing in github-push-sync, jira-status-sync, ado-status-sync

Phase 3 (Feature - depends on Phase 2):
  T-008: Closure hook dispatcher
  T-009: Import-to-increment pipeline fix
  T-010: ADO bidirectional pull sync
  T-011: ADO regex-to-API AC sync replacement
  T-012: Suffix convention audit + enforcement

Phase 4 (Testing - depends on Phase 3):
  T-013: Unit tests for all new modules
  T-014: Integration tests (real API lifecycle)
```

---

## File Change Map

All paths relative to `repositories/anton-abyzov/specweave/`.

### New Files (~7)

| File | Lines | Purpose |
|------|-------|---------|
| `src/core/closure-dispatcher.ts` | ~150 | Closure hook dispatch (function-map pattern) |
| `src/core/errors/sync-error.ts` | ~30 | Structured sync error type |
| `src/core/sync/retry-wrapper.ts` | ~40 | Inline retry with exponential backoff |
| `src/importers/ac-parser.ts` | ~60 | Parse ACs from external item descriptions |
| `plugins/specweave-ado/lib/ado-rate-limiter.ts` | ~70 | Token bucket for ADO 200 req/min limit |
| `src/core/ado-description-updater.ts` | ~60 | HTML section manipulation for ADO descriptions |
| `tests/integration/sync/*.test.ts` | ~500 | 5 integration test files |

### Modified Files (~12)

| File | Change | Lines |
|------|--------|-------|
| `src/sync/sync-coordinator.ts` | Wire closure dispatcher after living docs sync | ~20 |
| `plugins/specweave-github/lib/github-push-sync.ts` | Throw SyncError instead of returning false | ~15 |
| `plugins/specweave-jira/lib/jira-status-sync.ts` | Throw SyncError + wire circuit breaker | ~30 |
| `plugins/specweave-jira/lib/jira-spec-sync.ts` | Wire circuit breaker + file locking | ~25 |
| `plugins/specweave-ado/lib/ado-status-sync.ts` | Throw SyncError + wire circuit breaker + rate limiter | ~30 |
| `plugins/specweave-ado/lib/ado-spec-sync.ts` | Wire circuit breaker + rate limiter | ~25 |
| `plugins/specweave-ado/lib/ado-ac-checkbox-sync.ts` | Replace regex with API-based AC sync | ~80 |
| `src/importers/import-coordinator.ts` | Wire ImportToIncrementConverter into main flow | ~40 |
| `src/sync/types.ts` | Add formatSuffixedId utility | ~10 |
| `src/core/config/types.ts` | Add closure hook config types | ~15 |
| `plugins/specweave-ado/lib/ado-client.ts` | Add pullWorkItemState method | ~20 |
| `src/core/types/sync-profile.ts` | Extend with closure config types | ~10 |

---

## Trade-off Decisions

### Decision 1: Function-map vs. ProviderAdapter for closure hooks

**Chosen**: Function-map (`Record<SyncProvider, ClosureFn>`)

**Why**: ADR-0240 explicitly warns against creating adapter system #7. The function-map pattern used by `ac-progress-sync.ts` is proven in production, requires ~150 lines total, and adding a 4th provider means writing one function + adding to map.

**Rejected**: ProviderAdapter interface -- SyncEngine is not used in production (only tests). Wiring through it would require a migration that is out of scope.

### Decision 2: Inline retry vs. retry queue for 5xx errors

**Chosen**: Both. Inline retry (`withRetry`, base 1s, max 30s) for synchronous operations within a single command. File-based retry queue for async recovery across process restarts.

**Why**: Spec requires exponential backoff (1s base, 30s max) which implies inline retry within the operation. But the retry queue is needed for NFR (persist across restarts). The two mechanisms serve different time horizons: inline for seconds, queue for minutes/hours.

### Decision 3: ADO AC sync -- regex replacement vs. section rewrite

**Chosen**: Section rewrite (find AC section, replace its content, preserve everything else).

**Why**: Regex is the root cause of the fragility (US-007). A full section rewrite using `formatACCheckboxes()` from core eliminates regex entirely. The ADO API supports JSON Patch for field updates, so we can surgically replace the description.

**Risk**: If ADO description has no recognizable AC section, we append. If the user manually reorganizes the AC section, the next sync will normalize it. Acceptable trade-off -- the alternative (regex) is worse.

### Decision 4: ADO rate limiter -- self-tracking token bucket vs. querying ADO API

**Chosen**: Self-tracking token bucket.

**Why**: ADO does not expose a rate limit query endpoint (unlike GitHub's `gh api rate_limit`). The token bucket is deterministic, requires zero API calls, and matches the spec requirement for a "token bucket algorithm consistent with the existing config schema" (AC-US8-04).

---

## Non-Functional Requirements Verification

| NFR | Design Approach | Met? |
|-----|----------------|------|
| Rate-limited ADO: max 500ms latency per request | Token bucket consume() is O(1) in-memory; no API call | Yes |
| Circuit breaker fail-fast: within 5ms | SyncCircuitBreaker.canSync() is a single boolean check + Date comparison | Yes |
| Retry queue persists across restarts | SyncRetryQueue uses file-based JSON with atomic write | Yes |
| Circuit breaker state survives restarts | Currently in-memory only; add file persistence wrapper (~40 lines) | Needs impl |
| No new credential storage | All API calls use existing config.json PAT/token fields | Yes |
| Lock files contain no sensitive data | LockManager writes only PID and session ID | Yes |
| Backward compatible config schema | New hook config fields are additive; defaults preserve current behavior | Yes |

**Note on circuit breaker persistence**: The existing `SyncCircuitBreaker` is in-memory. The NFR requires survival across restarts. Add a `PersistentCircuitBreaker` wrapper that serializes state to `.specweave/state/circuit-breakers.json` on `recordFailure()`/`recordSuccess()` and reads on construction. This is ~40 lines wrapping the existing class.

---

## Edge Case Handling

| Edge Case | Handling |
|-----------|---------|
| Stale lock recovery | LockManager already handles: 5-min threshold + PID check + forced acquire with warning |
| Partial closure (2/3 providers succeed) | Closure dispatcher collects errors per provider; increment closes locally; stderr reports partial sync warning |
| Import deduplication | ImportToIncrementConverter uses IncrementExternalRefDetector (existing); scans all increment dirs for matching externalLinks |
| Empty AC list | formatACCheckboxes() returns empty string; ADO description updater skips AC section creation |
| Config changes mid-sync | Provider enablement checked at dispatch time (start of sync); in-flight operations complete; no new operations start for disabled provider |
| ADO manual HTML edits | Section rewrite preserves all content outside the AC section; only the checkbox block within "Acceptance Criteria" heading is touched |
| JIRA transition IDs vary | JiraStatusSync.updateStatus() queries available transitions dynamically before attempting state change (existing behavior) |

---

## Recommended Domain Skill Delegation

This increment is backend TypeScript (Node.js ESM) only. No frontend, no infrastructure changes.

- **Primary**: `backend:nodejs` -- for implementation of all components
- **Testing**: `testing:vitest` -- for unit + integration test implementation (TDD mode active)

No other domain skills needed. The complexity is medium (auth/sync patterns, 3 providers) with 1-2 domain plugins appropriate per the complexity gate.
