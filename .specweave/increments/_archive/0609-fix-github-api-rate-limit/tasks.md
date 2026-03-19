# Tasks

## Phase 1: Cache Issue Data Through Call Chain

### T-001: Pass cached issue data from updateUserStoryIssue to updateStatusLabels
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- Given `updateUserStoryIssue()` fetches issue data at line ~1021, When it calls `updateStatusLabels()`, Then the fetched data is passed as a parameter
- Given `updateStatusLabels()` receives cached issue data, When it needs issue state, Then it uses the cached data instead of calling `getIssue()`
- Given `updateStatusLabels()` previously called `getIssue()` twice (lines ~1143 and ~1228), When cached data is provided, Then zero `getIssue()` calls are made

### T-002: Deduplicate getLastComment calls
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- Given `updateUserStoryIssue()` calls `getLastComment()` at line ~1065, When it passes the result to `updateStatusLabels()` and `postProgressCommentIfChanged()`, Then `getLastComment()` is called exactly once per user story

## Phase 2: Rate Limit Pre-Check

### T-003: Add rate limit check to syncFeatureToGitHub
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- Given `syncFeatureToGitHub()` is called, When it starts, Then `checkRateLimit()` is called before acquiring the sync lock
- Given remaining API calls < 200, When the rate limit check runs, Then sync returns early with a warning log and retriable status
- Given remaining API calls >= 200, When the rate limit check runs, Then sync proceeds normally

### T-004: Queue rate-limited syncs for retry
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- Given sync was skipped due to rate limit, When the result is returned, Then the sync is queued in the retry infrastructure for later execution

## Phase 3: Skip-If-Unchanged Guards

### T-005: Add label comparison guard to updateStatusLabels
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed

**Test Plan**:
- Given current issue labels match the desired status labels, When `updateStatusLabels()` runs, Then no `gh issue edit --add-label` or `--remove-label` calls are made
- Given current labels differ from desired, When `updateStatusLabels()` runs, Then only the necessary add/remove calls are made

### T-006: Standardize postProgressCommentIfChanged to use client.getLastComment
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- Given `postProgressCommentIfChanged()` previously used direct `gh api` call, When refactored, Then it uses `this.client.getLastComment()` or accepts cached comment data
- Given body, labels, and progress are all unchanged, When sync runs for that user story, Then zero write API calls are made

## Phase 4: DuplicateDetector Optimization

### T-007: Skip Phase 3 verification when reusing existing issue
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed

**Test Plan**:
- Given Phase 1 (`checkBeforeCreate`) found an existing issue, When `createWithProtection()` returns the existing issue, Then Phase 3 (`verifyAfterCreate`) is NOT called
- Given Phase 1 found no existing issue and a new issue was created, When `createWithProtection()` completes, Then Phase 3 verification still runs to catch race conditions
