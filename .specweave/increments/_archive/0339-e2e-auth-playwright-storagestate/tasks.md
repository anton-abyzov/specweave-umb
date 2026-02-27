# Tasks — 0339 E2E Auth Playwright storageState

### T-001: Create auth.setup.ts with storageState persistence
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given no `.auth/user.json` → When setup runs → Then browser pauses for manual login → Then saves cookies to `.auth/user.json`

### T-002: Update playwright.config.ts with 3 projects
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given config → When playwright runs → Then setup, chromium, and authenticated projects execute in correct order

### T-003: Update .gitignore and package.json
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given `.auth/` directory → When git status → Then it is ignored

### T-004: Create authenticated E2E test files
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given valid storageState → When authenticated tests run → Then all pass with 200 responses

### T-005: Verify existing tests unaffected
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given new config → When `playwright test --project=chromium` → Then all existing tests pass
