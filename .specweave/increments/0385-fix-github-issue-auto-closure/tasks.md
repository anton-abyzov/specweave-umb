---
totalTasks: 3
completedTasks: 3
---

# Tasks

### T-001: Add closeCompletedIncrementIssues to GitHubReconciler
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given metadata with issue numbers → When closeCompletedIncrementIssues called → Then open issues are closed via API

### T-002: Wire fallback into completeIncrement
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given completeIncrement runs → When LifecycleHookDispatcher finishes → Then GitHubReconciler.closeCompletedIncrementIssues is called

### T-003: Write unit tests for closure method
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given test suite → When vitest runs → Then all 10 tests pass covering both formats, dedup, idempotency, partial failures, milestone, metadata accuracy
