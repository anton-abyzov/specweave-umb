# Tasks: FS-529 Fix GitHub API Rate Limit Exhaustion

### T-001: Scope reconciler scanIncrements() to active-only
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed
**Test**: Given 529 increments → When reconciler.scanIncrements() runs → Then only active directories are scanned, _archive/ and _abandoned/ are skipped

### T-002: Add 5-minute debounce to reconciler
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] completed
**Test**: Given reconciler ran 2 min ago → When triggered again → Then returns immediately with debounced result

### T-003: Add session cache to GitHubClientV2.getIssue()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] completed
**Test**: Given getIssue(42) called twice within 30s → When second call executes → Then cached result returned, no subprocess spawned

### T-004: Reduce DuplicateDetector to single search phase
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] completed
**Test**: Given no duplicate found in Phase 1 → When issue is created → Then Phase 3 verification is skipped, total API calls = 1

### T-005: Add rate limit pre-flight check to reconciler and feature sync
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] completed
**Test**: Given rate limit remaining = 50 → When sync starts → Then operation skipped with warning log

### T-006: Add batchGetIssues() GraphQL method to GitHubClientV2
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [x] completed
**Test**: Given 10 issue numbers → When batchGetIssues() called → Then 1 GraphQL query fetches all 10

### T-007: Use batchGetIssues() in AC checkbox sync
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [x] completed
**Test**: Given 4 user stories with GitHub issues → When AC sync runs → Then 1 batch fetch instead of 4 individual calls
