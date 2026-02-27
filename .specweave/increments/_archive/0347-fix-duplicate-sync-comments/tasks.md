# Tasks: 0347 - Fix Duplicate Sync Comments

## US-001: Idempotent Completion Comments

### T-001: Add GitHub completion comment dedup
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given a GitHub issue with an existing "User Story Complete" comment → When `closeGitHubIssuesForUserStories()` runs again → Then no duplicate comment is posted and the issue is still closed

In `sync-coordinator.ts` `closeGitHubIssuesForUserStories()` (~line 610), before posting the completion comment:
1. Call `client.getLastComment(existingIssue.number)`
2. If last comment body includes `✅ User Story Complete`, log skip and continue
3. Still close the issue if state is open (pass no comment to `closeIssue`)

### T-002: Add `getLastComment()` to ADO client
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given an ADO work item with comments → When `getLastComment()` is called → Then it returns the most recent comment text

In `src/integrations/ado/ado-client.ts`, add:
```typescript
public async getLastComment(workItemId: number): Promise<{ text: string } | null>
```
Uses ADO REST API: `GET _apis/wit/workitems/{id}/comments?$top=1&$orderBy=createdDate desc`

### T-003: Add ADO completion comment dedup
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given an ADO work item with an existing completion comment → When `syncUserStory()` runs again → Then no duplicate comment is posted

In `sync-coordinator.ts` `syncUserStory()` ADO branch (~line 1470), before `addComment`:
1. Call `adoClient.getLastComment(workItemId)`
2. If last comment text matches `completionComment`, log skip and return

### T-004: Add filesystem lock to `syncIncrementClosure()`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given two concurrent calls to `syncIncrementClosure()` for the same increment → When both execute → Then only one proceeds and the other is skipped

At the top of `syncIncrementClosure()`, add a `LockManager` lock:
- Lock path: `.specweave/state/.locks/sync-closure-{incrementId}`
- TTL: 60 seconds
- If lock acquisition fails, log and return early with `{ success: true, closedIssues: [] }`

### T-005: Unit tests for dedup logic
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test**: Tests cover: GitHub dedup skip, ADO dedup skip, lock prevents concurrent execution

Add tests in `tests/unit/sync/` covering:
1. GitHub: `closeGitHubIssuesForUserStories` skips comment when last comment matches
2. ADO: `syncUserStory` skips comment when last comment matches
3. Lock: second concurrent `syncIncrementClosure` returns early
