# Tasks: Fix Develop Branch Tests & Auto-Merge

## Phase 1: Module Resolution Fixes (US-001)

### T-001: Delete context.test.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given context.ts was removed → When test file deleted → Then no module resolution errors

### T-002: Delete playwright-cli test files
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given playwright plugin migrated out → When 5 test files deleted → Then no module resolution errors

## Phase 2: Assertion Drift Fixes (US-002 through US-005)

### T-003: Fix external-issue-auto-creator.test.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given updated expectations → When tests run → Then all pass

### T-004: Fix GitHub sync tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given updated call count expectations → When tests run → Then all 3 files pass

### T-005: Fix CLI and plugin tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test**: Given updated mock expectations → When tests run → Then all 4 files pass

### T-006: Fix skills and infrastructure tests
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test**: Given updated skill lists and line count constraints → When tests run → Then all 3 files pass

## Phase 3: Workflow Fix (US-006)

### T-007: Document Dependabot auto-merge repo setting
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Test**: Given workflow file → When repo setting documented → Then maintainers know to enable "Allow Actions to approve PRs"

## Phase 4: Verification

### T-008: Run full test suite
**User Story**: US-001 through US-005 | **Status**: [x] completed
**Test**: Given all fixes applied → When `npx vitest run tests/unit` → Then 0 failures (592 files, 16604 tests pass)
