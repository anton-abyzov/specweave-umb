# Tasks: 0299 Reconciler Config Cache + Stale Issue Closure

### T-001: Add config caching to GitHubReconciler
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given GitHubReconciler with loadConfig() called twice -> When reconcile() runs -> Then config.json is read from disk only once

Add `configCache` field and modify `loadConfig()` to cache after first read. Verify fd61f51c fix (passing config to initClient) is in place.

### T-002: Add regression test for single loadConfig call
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given mocked fs -> When reconcile() runs -> Then mockReadFile is called for config.json exactly once

Add test to `github-reconciler.test.ts` that tracks how many times config.json is read during a full reconcile cycle.

### T-003: Run full test suite and verify all pass
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given all changes applied -> When `vitest run github-reconciler.test.ts` -> Then all tests pass (59 existing + new)

### T-004: Close stale GitHub issues with status:complete
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test**: Given 13 open issues with status:complete label -> When gh issue close is run -> Then all 13 issues are closed with reconciliation comment

Close issues: #1192, #1193, #1194, #1195, #1196, #1197, #1198, #1199, #1200, #1201, #1212, #1213, #1214

### T-005: Close bug issue #1223
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given issue #1223 open -> When gh issue close is run -> Then issue is closed with reference to fd61f51c fix commit

### T-006: Add loadConfig cache test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given GitHubReconciler instance -> When loadConfig() called 3 times -> Then readFile called once and all 3 return same object
