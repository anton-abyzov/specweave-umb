---
increment: 0613-reduce-github-api-calls-phase1
type: tasks
---

# Tasks: Reduce GitHub API Calls (Phase 1)

## Domain A: Eliminate Duplicate GitHub Sync (US-001)

### T-001: Add skipGitHubComments option to syncACProgressToProviders
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given syncACProgressToProviders is called with `skipGitHubComments: true`
- When GitHub provider is enabled
- Then postACProgressComments is skipped for GitHub but autoCloseCompletedUserStories still runs
- And JIRA/ADO providers execute normally regardless of the flag

### T-002: Wire skipGitHubComments in sync-progress command
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given GitHubACCheckboxSync (Step 5) completes successfully
- When syncACProgressToProviders is called in Step 6
- Then skipGitHubComments is true
- And when Step 5 throws an error, skipGitHubComments is false (fallback)

### T-003: Add tests for skipGitHubComments behavior
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [x] completed
**Test Plan**:
- Given a mocked 7-US increment
- When sync runs with skipGitHubComments=true
- Then postACProgressComments mock is NOT called for GitHub
- And autoCloseCompletedUserStories mock IS called
- And JIRA/ADO mocks are called normally

## Domain B: Optimize autoClose Operations (US-002)

### T-004: Hoist ensureLabelExists outside per-US loop
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**:
- Given 3 user stories with all ACs complete
- When autoCloseCompletedUserStories runs
- Then ensureLabelExists is called exactly once (not 3 times)

### T-005: Add module-level label cache
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given ensureLabelExists was called for repo/label combo in a previous sync
- When ensureLabelExists is called again for the same repo/label
- Then no gh label list API call is made (cache hit)

### T-006: Combine close + label edit into single API call
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-05 | **Status**: [x] completed
**Test Plan**:
- Given a user story with all ACs complete and issue is open
- When autoClose runs
- Then a single gh api PATCH call sets state=closed and adds status:completed label
- And completion comment is still posted separately

### T-007: Skip state check for known-closed USs
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test Plan**:
- Given metadata.json externalLinks has status "closed" for a US
- When autoCloseCompletedUserStories processes that US
- Then no gh issue view API call is made
- And the US is skipped with reason "already-closed"

## Domain C: Skip Unnecessary Comments (US-003)

### T-008: Skip addComment when no checkbox changes
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**:
- Given GitHubACCheckboxSync processes an issue where body === originalBody
- When addComment option is true
- Then addComment is NOT called (no changes to report)
- And given checkboxes actually changed, addComment IS called
