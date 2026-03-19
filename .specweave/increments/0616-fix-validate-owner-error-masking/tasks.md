---
increment: 0616-fix-validate-owner-error-masking
title: "Fix GitHub API error masking in validateOwner"
type: bug
test_mode: TDD
tdd_enforcement: strict
---

# Tasks: Fix GitHub API error masking in validateOwner

## US-001: Accurate GitHub API error reporting in owner validation (P1)

### T-001: [TDD RED] Write failing 401 test in github-provider.test.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] completed
**Test**: Given `fetch()` is mocked to return 401 for both `/users/{owner}` and `/orgs/{owner}` → When `GitHubProvider.validateOwner(owner, token)` is called → Then the returned error object has `status: 401` and the formatted error message contains "Authentication Failed" (not "404 Not Found")

---

### T-002: [TDD RED] Write failing 403 tests in github-provider.test.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] completed
**Test**: Given `fetch()` is mocked to return 403 for both endpoints AND separately mocked to return 403 for user + 404 for org → When `GitHubProvider.validateOwner()` is called in each scenario → Then the error has `status: 403` and message contains "Permission Denied" (not "404 Not Found") in both cases; the mixed-status case selects the more informative 403

---

### T-003: [TDD RED] Write 404 regression test in github-provider.test.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] completed
**Test**: Given `fetch()` is mocked to return 404 for both `/users/{owner}` and `/orgs/{owner}` → When `GitHubProvider.validateOwner()` is called → Then the error has `status: 404` and the message contains "Not Found" (existing behavior preserved)

---

### T-004: [TDD RED] Write 401/403 tests in github-validator.test.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] completed
**Test**: Given `fetch()` is mocked to return 401 (and separately 403) for owner endpoints → When the standalone `validateOwner()` from `github-validator.ts` is called → Then the error output matches exactly what `GitHubProvider.validateOwner()` produces for the same HTTP status (consistent error reporting across both implementations)

---

### T-005: [TDD GREEN] Fix github-provider.ts to capture actual HTTP status
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given tests T-001, T-002, T-003 are red (failing) → When the hardcoded `{ status: 404 }` in `GitHubProvider.validateOwner()` is replaced with the status-priority logic (prefer `userResponse.status` when it is 401/403 and `orgResponse.status` is 404, otherwise use `orgResponse`) → Then all three red tests turn green without breaking existing `validateOwner` test cases

---

### T-006: [TDD GREEN] Refactor github-validator.ts to delegate to GitHubProvider
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] completed
**Test**: Given test T-004 is red (failing) → When the duplicate `validateOwner` body in `github-validator.ts` is replaced with a delegation to `GitHubProvider.validateOwner()` (mapping `type: 'organization'` → `'org'`) → Then T-004 turns green, no src/ callers break, and existing github-validator tests for the 404 path continue to pass
