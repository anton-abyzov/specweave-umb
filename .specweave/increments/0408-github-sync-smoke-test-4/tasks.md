# Tasks — 0408-github-sync-smoke-test-4

## Implementation Tasks

### T-001: Verify AC markers section is populated on auto-create
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given spec.md with 2 ACs → When GitHub auto-create runs → Then issue body has AC checkboxes inside specweave:ac-start/end markers

### T-002: Verify AC checkboxes update after marking ACs complete
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given ACs marked [x] in spec.md → When AC sync runs → Then issue body checkboxes in markers section show [x]
