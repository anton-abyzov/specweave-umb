# Plan: Fix Duplicate Completion Comments

## Approach: 2-Layer Defense

### Layer 1 — Comment dedup before posting (GitHub + ADO)

Mirror JIRA's `getLastComment()` pattern in both GitHub and ADO closure paths.

**GitHub** — `closeGitHubIssuesForUserStories()` in sync-coordinator.ts (~line 610):
- Before `client.closeIssue(number, completionComment)`, call `client.getLastComment(number)`
- If last comment body includes `## ✅ User Story Complete`, skip the comment but still close
- `getLastComment()` already exists on `GitHubClientV2` (line 606)

**ADO** — `syncUserStory()` in sync-coordinator.ts (~line 1472):
- Add `getLastComment()` to `AdoClient` (uses ADO REST API: `GET _apis/wit/workitems/{id}/comments`)
- Before `adoClient.addComment(id, comment)`, call `adoClient.getLastComment(id)`
- Skip if last comment text matches

### Layer 2 — Filesystem lock on `syncIncrementClosure()`

Add a `LockManager` lock at the top of `syncIncrementClosure()` keyed by increment ID:
- Path: `.specweave/state/.locks/sync-closure-{incrementId}`
- TTL: 60 seconds
- Pattern: same as `format-preservation-sync.ts` line 155-182
- This prevents the second trigger from executing at all

## Files to Modify

1. **`src/sync/sync-coordinator.ts`** — Add dedup to GitHub closure + lock on syncIncrementClosure + ADO dedup
2. **`src/integrations/ado/ado-client.ts`** — Add `getLastComment()` method
3. **Unit tests** for dedup logic
