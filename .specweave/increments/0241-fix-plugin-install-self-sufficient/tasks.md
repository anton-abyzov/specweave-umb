# Tasks — 0241: Fix Plugin Installation

### T-001: Create plugin-copier.ts module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given a valid specweave root with marketplace.json → When copyPlugin('sw', root) is called → Then files are copied to ~/.claude/commands/sw/ with correct permissions

### T-002: Write plugin-copier unit tests (TDD RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given test cases for copyPlugin, hash, lockfile → When tests run → Then all fail (no implementation yet)

### T-003: Update refresh-plugins.ts to use plugin-copier
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given specweave refresh-plugins command → When executed → Then plugins installed without vskill dependency

### T-004: Update refresh-plugins.test.ts mocks
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given updated refresh-plugins → When tests run → Then all pass with copyPlugin mocks

### T-005: Update plugin-installer.ts to use plugin-copier
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given specweave init → When installAllPlugins() runs → Then core plugin installed via inline copier

### T-006: Update plugin-installer test mocks
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given updated plugin-installer → When tests run → Then all pass with copyPlugin mocks

### T-007: Update user-prompt-submit.sh hook
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given lazy loading trigger → When install_plugin_direct() runs → Then plugin copied without npx vskill

### T-008: Build and verify all tests pass
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: Given all changes → When npm run rebuild && npm run test:unit:fast → Then zero failures
