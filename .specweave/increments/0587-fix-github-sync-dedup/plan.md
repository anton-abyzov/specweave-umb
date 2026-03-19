# Architecture Plan: Fix GitHub Sync Duplication and Progress Spam

## Problem Statement

GitHub sync currently suffers from five related issues:

1. **Progress comment spam** -- `postACProgressComments()` in `github-ac-comment-poster.ts` posts a new comment on every sync regardless of whether progress changed. JIRA has fingerprint-based dedup (line 303 of `jira-status-sync.ts`); GitHub does not.
2. **Redundant body edits** -- `updateUserStoryIssue()` (line 1009-1031 of `github-feature-sync.ts`) calls `gh issue edit` on every sync even when the body is identical, creating empty edit events.
3. **Race conditions from parallel syncs** -- The in-memory lock (lines 60-63 of `github-feature-sync.ts`) only protects within a single process. Multiple Claude sessions or CLI invocations can sync concurrently, causing duplicate issues and comment spam.
4. **Phase 3 verification disabled** -- `duplicate-detector.ts` line 489 requires opt-in via `SPECWEAVE_VERIFY_DUPLICATES=1`. This leaves the duplicate auto-correction safety net off by default.
5. **No sync throttle coordination** -- Multiple trigger paths (status-change-sync-trigger, sync-progress CLI, auto-create hook) can fire syncs in rapid succession with no cross-path coordination.

## Architecture Decisions

### AD-1: Comment Fingerprint Dedup (P0)

**Pattern**: HTML comment fingerprint in GitHub progress comments, matching JIRA's proven approach.

**Format**: `<!-- sw-progress:N/M -->` embedded at the top of every progress comment body.

**How it works**:
1. Before posting a progress comment, fetch the last SpecWeave comment from the issue
2. Extract the fingerprint from the HTML comment (invisible in rendered markdown)
3. If fingerprint matches current progress state, skip posting
4. If different or no fingerprint found, post new comment with updated fingerprint

**Components affected**:
- `github-ac-comment-poster.ts` -- `buildProgressCommentForUS()` adds fingerprint; `postACProgressComments()` checks before posting
- `github-ac-checkbox-sync.ts` -- progress comment section (line 201-218) adds fingerprint and dedup check
- `github-feature-sync.ts` -- `postProgressCommentIfChanged()` (line 1262-1306) already does body-text dedup; enhance with fingerprint for reliability

**Why HTML comments over body-text normalization**:
- `postProgressCommentIfChanged()` already normalizes comment bodies, but this is fragile -- any formatting change defeats the comparison
- HTML comments are invisible, stable, and machine-readable
- JIRA uses the same approach (fingerprint string in italicized text at bottom of ADF) and it works reliably

### AD-2: Cross-Process File Lock (P0)

**Pattern**: Reuse existing `LockManager` from `src/utils/lock-manager.ts` (file-based mkdir, already used by JIRA sync).

**Lock scope**: One lock per `{owner}/{repo}` pair, stored at `.specweave/state/locks/github-sync-{owner}-{repo}/`.

**Integration points**:
- `GitHubFeatureSync.syncFeature()` -- wrap the entire sync operation in `LockManager.acquire()/release()`
- `GitHubACCheckboxSync.syncACCheckboxesToGitHub()` -- acquire same lock before checkbox updates
- `github-ac-comment-poster.ts` -- acquire same lock before posting comments

**Replace existing in-memory lock**: Remove the `static syncLocks: Map<string, number>` (line 62 of `github-feature-sync.ts`) and replace with `LockManager`. The in-memory map only works within a single Node process; `LockManager` uses `mkdir` atomicity for cross-process safety.

**Stale lock handling**: `LockManager` already handles stale locks via PID checking and configurable timeout (default 300s). GitHub sync operations should use a 120s stale threshold since individual syncs rarely exceed 60s.

### AD-3: Phase 3 Env Var Inversion (P0)

**Current**: `SPECWEAVE_VERIFY_DUPLICATES=1` (opt-in) at line 489 of `duplicate-detector.ts`.
**New**: `SPECWEAVE_SKIP_VERIFY_DUPLICATES=1` (opt-out).

**Change**: Invert the condition so Phase 3 runs by default. Users who want to skip verification for speed can set `SPECWEAVE_SKIP_VERIFY_DUPLICATES=1`.

**Rationale**: Duplicate detection was disabled by default to reduce API calls. In practice, the race condition it catches (parallel sync sessions creating duplicate issues) is common enough that the protection should be on by default. The 2-second delay in `verifyAfterCreate()` is acceptable given that issue creation is already a slow operation.

### AD-4: Body Diff Before Edit (P1)

**Pattern**: Fetch current issue body, normalize both old and new, compare before calling `gh issue edit`.

**Normalization**:
```
1. Strip trailing whitespace per line
2. Collapse multiple blank lines to single
3. Normalize checkbox states for comparison: [ ] and [x] are part of the diff
4. Strip HTML comments (timestamps, fingerprints) -- these change every sync
```

**Components affected**:
- `github-feature-sync.ts` -- `updateUserStoryIssue()` (line 1009-1031): fetch current body, normalize, compare, skip edit if identical
- `github-ac-checkbox-sync.ts` -- already does this correctly (line 189: `if (body === originalBody)` skip)

**Implementation**: Extract a shared `normalizeIssueBody(body: string): string` utility function into a new file `github-body-utils.ts` in the GitHub plugin directory. Both `updateUserStoryIssue` and `postProgressCommentIfChanged` will use it.

### AD-5: Sync Throttle Coordination (P1)

**Pattern**: Extend the throttle concept from existing `USSyncThrottle` (`src/core/us-sync-throttle.ts`) into a new generalized `SyncThrottle` class.

**Current state**: `USSyncThrottle` already exists as a singleton with file-based state at `.specweave/state/us-sync-throttle.json`. It tracks last sync time per increment with a 60s throttle window.

**New class**: `SyncThrottle` in `src/core/sync-throttle.ts` generalizes the pattern:
- Tracks sync operations by `{provider}:{scope}` key (e.g., `github:anton-abyzov/specweave`, `github-ac:0587`)
- Configurable throttle windows per operation type
- File-based state at `.specweave/state/sync-throttle.json`

**Throttle windows**:
| Operation | Window | Rationale |
|-----------|--------|-----------|
| Full feature sync | 60s | Expensive -- milestones + all issues |
| AC checkbox sync | 30s | Medium -- reads/writes individual issues |
| Progress comment | 30s | Light but visible -- comment spam prevention |
| Issue body update | 30s | Medium -- single API call per issue |

**Integration into trigger paths**:
- `status-change-sync-trigger.ts` -- check throttle before `spawnAsyncSync()` (line 95)
- `sync-progress.ts` (CLI) -- check throttle at start; `--force` flag bypasses throttle
- `auto-create-external-issue.ts` -- check throttle for the create operation

## Component Design

### New Files

```
plugins/specweave/lib/integrations/github/
  github-body-utils.ts          -- normalizeIssueBody(), buildFingerprint(),
                                   extractFingerprint()

src/core/
  sync-throttle.ts              -- SyncThrottle class (generalized from USSyncThrottle)
```

### Modified Files

```
plugins/specweave/lib/integrations/github/
  github-ac-comment-poster.ts   -- Add fingerprint to comments, dedup before posting
  github-ac-checkbox-sync.ts    -- Add fingerprint to progress comments, dedup check
  github-feature-sync.ts        -- Replace in-memory lock with LockManager,
                                   add body diff check, use SyncThrottle
  duplicate-detector.ts         -- Invert Phase 3 env var

src/core/increment/
  status-change-sync-trigger.ts -- Add SyncThrottle check before triggering

src/cli/commands/
  sync-progress.ts              -- Add SyncThrottle check (with --force bypass)

src/hooks/
  auto-create-external-issue.ts -- Add SyncThrottle check for create operations
```

## Data Flow

### Progress Comment Flow (After Fix)

```
Trigger (status change / CLI / hook)
  |
  v
SyncThrottle.shouldSkip("github-ac:{incrementId}")?
  |-- yes --> return (throttled)
  |-- no --+
            v
LockManager.acquire("github-sync-{owner}-{repo}")
  |-- fail --> return (locked by another process)
  |-- ok --+
            v
For each user story issue:
  1. Fetch last SpecWeave comment from issue
  2. Extract fingerprint: <!-- sw-progress:N/M -->
  3. Compare with current progress state
  |-- same --> skip (no change)
  |-- different --+
                  v
  4. Build comment body with new fingerprint
  5. Post comment via gh issue comment
            |
            v
SyncThrottle.record("github-ac:{incrementId}")
LockManager.release()
```

### Issue Body Update Flow (After Fix)

```
Trigger (feature sync)
  |
  v
LockManager.acquire("github-sync-{owner}-{repo}")
  |
  v
For each user story issue:
  1. Build new issue body from living docs
  2. Fetch current body via gh issue view
  3. normalizeIssueBody(current) vs normalizeIssueBody(new)
  |-- same --> skip edit
  |-- different --+
                  v
  4. gh issue edit with new body
            |
            v
LockManager.release()
```

### Duplicate Detection Flow (After Fix)

```
DuplicateDetector.createWithProtection()
  |
  v
Phase 1: Search for existing issues (unchanged)
  |-- found --> reuse (unchanged)
  |-- not found --+
                  v
Phase 2: Create issue (unchanged)
  |
  v
Phase 3: Verify (NOW ON BY DEFAULT)
  |-- SPECWEAVE_SKIP_VERIFY_DUPLICATES=1 --> skip
  |-- default --+
                v
  Wait 2s for GitHub indexing
  Search for issues with same title pattern
  |-- count == 1 --> OK
  |-- count > 1 --+
                  v
  Phase 4: Close duplicates (keep oldest)
```

## Implementation Order

**Phase 1 (P0 -- Safety)**:
1. `github-body-utils.ts` -- Create shared utility (fingerprint + normalization)
2. `github-ac-comment-poster.ts` -- Add fingerprint dedup
3. `github-feature-sync.ts` -- Replace in-memory lock with LockManager
4. `duplicate-detector.ts` -- Invert Phase 3 env var

**Phase 2 (P1 -- Polish)**:
5. `sync-throttle.ts` -- Create generalized throttle
6. `github-feature-sync.ts` -- Add body diff check using shared normalizer
7. `github-ac-checkbox-sync.ts` -- Add fingerprint to progress comments
8. Integration: Wire throttle into all three trigger paths

## Testing Strategy

**Unit tests** (per component):
- `github-body-utils.test.ts` -- normalizeIssueBody edge cases, fingerprint build/extract
- `sync-throttle.test.ts` -- throttle window, file persistence, force bypass
- `duplicate-detector.test.ts` -- Phase 3 default-on behavior, opt-out via env var

**Integration tests**:
- `github-ac-comment-poster.test.ts` -- fingerprint dedup prevents duplicate comments
- `github-feature-sync.test.ts` -- LockManager prevents concurrent syncs, body diff skips no-op edits

**Manual verification gate**:
- Run sync twice in rapid succession on a real GitHub repo; verify no duplicate comments or redundant edits appear

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LockManager stale lock blocks sync | Medium | 120s stale threshold with PID check; `SPECWEAVE_DISABLE_LOCKS=1` escape hatch |
| Phase 3 default-on adds 2s delay | Low | Delay only applies to issue creation (rare); skip via env var |
| Fingerprint format change breaks dedup | Low | Stable format `<!-- sw-progress:N/M -->`; old comments without fingerprint treated as "different" (safe fallback) |
| Throttle prevents legitimate rapid syncs | Low | CLI `--force` flag bypasses throttle; windows are short (30-60s) |
