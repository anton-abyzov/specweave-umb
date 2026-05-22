# 0849 Tasks

### T-001: Remove duplicate Connect CTA in web cabinet
**AC**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test**: account-repos.test.tsx "renders empty state without a duplicate connect CTA" asserts queryByTestId("repos-connect-empty-cta") is null.

### T-002: Sectioned Public/Private rendering in web ConnectedReposTable
**AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: account-repos.test.tsx "renders Private section before Public when both exist" + "omits a section header for an empty bucket".

### T-003: Remove duplicate Connect CTA in desktop AccountShell
**AC**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: eval-ui ConnectedReposTable.test.tsx "renders empty state when no repos and triggers connect-new from the canonical chip button".

### T-004: Sectioned rendering in desktop ConnectedReposTable (parity)
**AC**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**Test**: covered by snapshot consistency with web; visual parity verified manually + via shared test data shape.

### T-005: Release desktop 1.0.46 with the redesign
**AC**: — | **Status**: [x] completed
**Test**: `gh run view <id>` for desktop-v1.0.46 returns conclusion=success.
