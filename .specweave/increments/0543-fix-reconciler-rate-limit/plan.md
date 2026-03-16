# Architecture Plan: Fix GitHub API Rate Limit Exhaustion in Reconciler

## Overview

The reconciler's `scanIncrements()` makes one `gh issue list --search` API call per increment directory without GitHub metadata. With ~161 increments and no caching, deduplication, or budget, this exhausts the 5000/hour REST API quota within a single session. This plan introduces three layered defenses -- status filtering, negative cache persistence, and a per-scan budget cap -- that reduce API calls from ~161 to ~3 under normal conditions.

## Architecture Decisions

### AD-1: Status Allowlist for Search Eligibility

**Decision**: Use a hardcoded allowlist of statuses that warrant GitHub search. Only `active`, `planning`, `in-progress`, `backlog`, `ready_for_review`, and `paused` trigger searches. Everything else (`completed`, `abandoned`, `created`, `unknown`, any unrecognized string) is skipped.

**Rationale**: The `IncrementStatus` enum defines the complete lifecycle. Completed and abandoned increments have finished their lifecycle -- any GitHub issues they had are already recorded in metadata or irrelevant. Using an allowlist (not a denylist) is safer: new unknown status values default to "skip" rather than "search", which is the correct failure mode for rate limit protection.

**Location**: Constant `SEARCHABLE_STATUSES` defined at module level in `github-reconciler.ts`, referencing `IncrementStatus` enum values.

### AD-2: Negative Cache in metadata.json Under `github.*` Namespace

**Decision**: When `searchGitHubForIssues()` returns zero results and the increment has no existing `metadata.github.issue`, write three fields into `metadata.json`:

```
metadata.github.searched = true
metadata.github.searchedAt = "<ISO timestamp>"
metadata.github.noIssuesFound = true
```

On subsequent scans, if `metadata.github.noIssuesFound === true`, skip the search entirely.

**Rationale**: Persisting negative results in `metadata.json` means the cache survives across sessions, CLI restarts, and process boundaries. The `extractGitHubState()` method reads only specific sub-keys (`github.issue`, `github.url`, `github.issues[]`) and ignores unknown keys, so adding `searched`/`searchedAt`/`noIssuesFound` is fully backward-compatible. Storing in `metadata.json` (not a separate cache file) keeps the data co-located with the increment and requires no new infrastructure.

**When NOT to write negative cache**: If `metadata.github.issue` already exists (main issue present), we skip negative caching because user story issues may appear later. Also, on search errors (network failure, API error), no negative cache is written -- only on confirmed empty results.

### AD-3: Session Search Cache as Static Map on GitHubClientV2

**Decision**: Add a `searchCache` static Map to `GitHubClientV2`, mirroring the existing `issueCache` pattern (line 22). Key: `"{owner}/{repo}#search:{featureId}"`. Value: `{ data: GitHubIssue[], fetchedAt: number }`. TTL: 30 seconds (same constant as `issueCache`).

**Rationale**: The `issueCache` pattern is already proven in this codebase. Static class-level Maps are the established caching mechanism for `GitHubClientV2`. The 30-second TTL prevents redundant calls within a single scan while ensuring stale data does not persist. Since Node.js is single-threaded, concurrent Map reads/writes within a scan are safe.

### AD-4: Per-Scan Budget Cap of 20

**Decision**: `scanIncrements()` maintains a local `searchBudget` counter starting at 0. Each `searchGitHubForIssues()` call increments it. When `searchBudget >= 20`, further searches are skipped. After the loop, if any searches were skipped, log the count.

**Rationale**: Per-call scope (not per-session) keeps the mechanism stateless and predictable. The budget resets naturally on every invocation. 20 is generous given that Phase 1 (status filtering) reduces eligible increments to ~3-5 in typical workspaces. The budget is a safety net for edge cases (new workspace, many active increments). Hard-coding avoids config surface area (YAGNI per spec).

## Component Boundaries

### Files Modified

```
github-reconciler.ts (primary)
+------------------------------------------------------------+
| SEARCHABLE_STATUSES constant (new, module-level)           |
| scanIncrements() - add status filter, budget counter,      |
|                    negative cache check, negative cache     |
|                    write-back, budget log                   |
| searchGitHubForIssues() - no changes to signature or core  |
|                           logic; called fewer times         |
+------------------------------------------------------------+

github-client-v2.ts (secondary)
+------------------------------------------------------------+
| searchCache: static Map (new, mirrors issueCache)          |
| searchIssuesByFeature() - check searchCache before         |
|                           executing gh CLI; cache result    |
+------------------------------------------------------------+

github-reconciler.test.ts (test)
+------------------------------------------------------------+
| New describe blocks for:                                    |
|   - Status-based filtering (US-001)                        |
|   - Negative cache (US-002)                                |
|   - Session search cache (US-003)                          |
|   - Budget cap (US-004)                                    |
| Existing tests: no changes needed (backward-compatible)    |
+------------------------------------------------------------+
```

### Files NOT Modified

- `increment-metadata.ts` -- No type changes. The `github.*` negative cache fields are untyped (`metadata: any` in the reconciler), consistent with how `github.issue`/`github.url` are already accessed dynamically.
- `base-reconciler.ts` -- Status constants are already available via `IncrementStatus` enum.
- Config files -- No new config surface per spec's "Out of Scope".

## Data Flow

```
scanIncrements()
  |
  for each increment directory:
  |
  +-- read metadata.json
  |
  +-- extractGitHubState(metadata) --> IncrementGitHubState
  |
  +-- [NEW] Check: is metadata.status in SEARCHABLE_STATUSES?
  |     no  --> skip search, use metadata refs only
  |     yes --> continue
  |
  +-- [NEW] Check: metadata.github.noIssuesFound === true?
  |     yes --> skip search (negative cache hit)
  |     no  --> continue
  |
  +-- [NEW] Check: searchBudget < 20?
  |     no  --> skip search, log "budget exhausted"
  |     yes --> continue
  |
  +-- searchGitHubForIssues(state)
  |     |
  |     +-- client.searchIssuesByFeature(featureId)
  |     |     |
  |     |     +-- [NEW] Check searchCache Map
  |     |     |     hit  --> return cached results
  |     |     |     miss --> gh issue list --search --> cache result
  |     |     |
  |     |     +-- return GitHubIssue[]
  |     |
  |     +-- if results.length === 0 AND no mainIssue:
  |     |     [NEW] write negative cache to metadata.json
  |     |
  |     +-- searchBudget++
  |
  +-- if mainIssue or userStoryIssues found --> push to results
```

## Implementation Strategy

### Phase 1: Status Filter + Budget Cap (US-001, US-004)

Modify `scanIncrements()` to add two guards before the `searchGitHubForIssues()` call at line 354:

1. **Status allowlist check**: Read `metadata.status`, skip search if not in `SEARCHABLE_STATUSES`.
2. **Budget counter**: Declare `let searchesMade = 0` before the loop. Increment on each search call. Skip when `>= 20`.

This phase alone reduces searches from ~161 to ~5 (only active-like increments without metadata).

### Phase 2: Negative Cache (US-002)

After `searchGitHubForIssues()` returns, check if the result is empty and no `mainIssue` exists. If so, write negative cache markers back to `metadata.json` using the same `fs.writeFile` pattern already at line 860.

On entry to the search decision, check `metadata.github.noIssuesFound === true` and skip if present.

### Phase 3: Session Search Cache (US-003)

Add `searchCache` to `GitHubClientV2` and wrap `searchIssuesByFeature()` with cache-check logic. This mirrors the `issueCache` pattern exactly:

```typescript
private static searchCache = new Map<string, { data: GitHubIssue[]; fetchedAt: number }>();

async searchIssuesByFeature(featureId: string, userStoryId?: string): Promise<GitHubIssue[]> {
  const cacheKey = `${this.fullRepo}#search:${featureId}${userStoryId ? ':' + userStoryId : ''}`;
  const cached = GitHubClientV2.searchCache.get(cacheKey);
  if (cached && Date.now() - cached.fetchedAt < GitHubClientV2.CACHE_TTL_MS) {
    return cached.data;
  }
  // ... existing gh CLI call ...
  GitHubClientV2.searchCache.set(cacheKey, { data: results, fetchedAt: Date.now() });
  return results;
}
```

### Test Strategy (TDD: RED -> GREEN -> REFACTOR)

All tests in `tests/unit/sync/github-reconciler.test.ts`. Existing mocking infrastructure (`mockSearchIssuesByFeature`, `mockReadFile`, `mockExistsSync`, `mockReaddir`) is sufficient. No new mock setup needed except `mockWriteFile`.

**New mock needed**: `mockWriteFile` -- the test file currently does not mock `fs.promises.writeFile` because existing tests don't exercise metadata write-back from `scanIncrements`. Add it to the hoisted mock block.

Test categories:

1. **Status filtering** (5 tests, one per AC in US-001): Set `metadata.status` to each value, assert `searchIssuesByFeature` is/isn't called.
2. **Negative cache read** (2 tests): metadata with `noIssuesFound: true` skips search; without it, search runs.
3. **Negative cache write** (3 tests): empty search result writes markers; non-empty result does not; main issue present does not.
4. **Session cache** (3 tests): cache miss calls CLI; cache hit returns cached; expired cache re-fetches.
5. **Budget cap** (4 tests): 20th search works; 21st is skipped; budget resets per call; log message emitted.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Negative cache prevents finding late-created issues | Only written when zero results AND no main issue; manual `specweave reconcile --force` can bypass |
| Status string not in enum (custom/corrupted) | Allowlist approach defaults to "skip" -- safe for rate limiting |
| `fs.writeFile` failure during negative cache write | Wrap in try/catch, log warning, do not propagate -- search already completed |
| Test file grows beyond 1500 line limit | Group tests by US, use shared setup helpers, keep each test focused |

## Constraints

- Budget hard-coded at 20 (no config.json surface)
- Negative cache fields use existing `github` namespace in metadata.json
- Search cache follows `issueCache` pattern: static Map, 30s TTL, same constant
- No changes to `IncrementMetadata` TypeScript type (fields accessed via `any`)
- Backward-compatible: increments without negative cache fields are searched normally (lazy population)

## Domain Delegation

No domain skill delegation needed. This is a pure backend/Node.js change within the existing sync subsystem. The changes are confined to two TypeScript files and their test, all within the specweave CLI codebase. No frontend, infrastructure, or external service changes required.
