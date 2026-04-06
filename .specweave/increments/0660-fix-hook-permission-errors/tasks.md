# Tasks: Fix shell hook permission errors

### T-001: Update tests to expect no `; true` (TDD RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given test assertions check for `; true`, When we update them, Then tests FAIL because source still has `; true`

### T-002: Remove `; true` from SKILL.md DCI hooks
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given SKILL.md files have `; true` removed, When we grep for `; true` in skills/, Then zero matches

### T-003: Convert inline DCI patterns in command .md files
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given command .md files use script calls, When we grep for inline patterns, Then zero matches

### T-004: Verify all tests pass (TDD GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test Plan**: Given all changes applied, When we run tests, Then all pass
