# Tasks: 0518-remove-scope-prompt

### T-001: Remove scope selection prompt from add.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given user runs `vskill i` without `--global` → When install flow runs → Then no scope prompt appears and skills install to project

### T-002: Update tests in add.test.ts for new scope behavior
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given scope prompt is removed → When tests run → Then all 1177+ tests pass

### T-003: Bump version and publish to npm
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given version bumped → When `npm publish` runs → Then `npx vskill` serves 0.4.16 with all fixes
