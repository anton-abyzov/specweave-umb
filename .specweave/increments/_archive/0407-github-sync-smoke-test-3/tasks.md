# Tasks — 0407-github-sync-smoke-test-3

## Implementation Tasks

### T-001: Verify AC progress comment shows correct count
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given AC-US1-01 marked [x] in spec.md → When AC sync runs → Then progress comment shows 1/2 ACs complete (50%)

### T-002: Verify AC checkbox syncs to issue body
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given both ACs marked [x] → When AC sync runs → Then issue body checkboxes show [x] for both ACs
