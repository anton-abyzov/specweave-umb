# Plan: FS-529 Fix GitHub API Rate Limit Exhaustion

## Architecture

### Root Cause Analysis
| Component | Calls/Run | Frequency | Est. Calls/Hr |
|-----------|-----------|-----------|---------------|
| Reconciler: getIssue() loop | 350 | 5-10x/hr | 1,750-3,500 |
| Reconciler: searchGitHubForIssues | 350 | 5-10x/hr | 1,750-3,500 |
| DuplicateDetector: triple-scan | 4/feature | 20/hr | 80-200 |
| AC Checkbox Sync | 4/increment | 20x/hr | 80-200 |
| **Total** | | | **3,660-7,400** |

### Solution Strategy
1. **Scope** (Changes 1-2): Only scan active increments + debounce = 90% reduction
2. **Cache** (Change 3): In-memory 30s TTL cache = eliminate redundant fetches
3. **Deduplicate** (Change 4): Single search instead of triple = 66% reduction per creation
4. **Batch** (Changes 6-7): GraphQL bulk fetch = O(1) instead of O(n)
5. **Safety** (Change 5): Rate limit pre-flight = prevent cascading failures

### Key Files
- `src/sync/github-reconciler.ts` — Changes 1, 2, 5
- `plugins/specweave-github/lib/github-client-v2.ts` — Changes 3, 6
- `plugins/specweave-github/lib/duplicate-detector.ts` — Change 4
- `plugins/specweave-github/lib/github-ac-checkbox-sync.ts` — Change 7
- `src/core/us-sync-throttle.ts` — Reference for debounce pattern
