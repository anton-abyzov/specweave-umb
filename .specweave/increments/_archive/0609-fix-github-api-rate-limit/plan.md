# Implementation Plan

## Overview

Targeted optimization of 3 files in `plugins/specweave/lib/integrations/github/`. No new modules, no architecture changes. Thread cached issue data through the sync call chain, add rate limit awareness using existing infrastructure, and add skip-unchanged guards.

## Architecture

### Current Flow (Per User Story)
```
syncFeatureToGitHub() → loop over stories
  → DuplicateDetector.createWithProtection()  [4 API calls]
  → updateUserStoryIssue()                    [1 fetch body + 1 edit]
    → getIssue() AGAIN                        [REDUNDANT]
    → getLastComment()                        [1 call]
    → updateStatusLabels()
      → getIssue() AGAIN                      [REDUNDANT]
      → getIssue() AGAIN                      [REDUNDANT]
      → getLastComment() AGAIN                [REDUNDANT]
    → postProgressCommentIfChanged()
      → direct gh api call                    [BYPASSES CACHE]
Total: ~13 API calls
```

### Optimized Flow
```
syncFeatureToGitHub()
  → checkRateLimit() — abort if < 200         [1 call, amortized]
  → loop over stories
    → DuplicateDetector.createWithProtection() [3-4 calls, skip Phase 3 if reuse]
    → updateUserStoryIssue()                   [1 fetch body + conditional edit]
      → REUSE fetched issue data               [0 calls — cached]
      → getLastComment() ONCE                  [1 call]
      → updateStatusLabels(cachedIssue, cachedComment)
        → SKIP if labels match                 [0 calls when unchanged]
      → postProgressCommentIfChanged(cachedComment)
        → SKIP if comment matches              [0 calls when unchanged]
Total: ~6-7 API calls
```

## Files to Modify

1. **`github-feature-sync.ts`** — Main sync engine
   - `syncFeatureToGitHub()`: add rate limit pre-check
   - `updateUserStoryIssue()`: cache issue data, pass to downstream
   - `updateStatusLabels()`: accept cached data param, remove double fetch
   - `postProgressCommentIfChanged()`: use client.getLastComment(), accept cached data

2. **`duplicate-detector.ts`** — Issue creation with dedup
   - `createWithProtection()`: skip Phase 3 when reusing existing issue

3. **`github-client-v2.ts`** — API client (minimal changes)
   - Possibly no changes needed if existing 30s cache suffices

## Testing Strategy

- Unit tests with vi.mock() for gh CLI calls
- Verify cached data flows through call chain
- Verify rate limit pre-check behavior
- Verify skip-unchanged guards
