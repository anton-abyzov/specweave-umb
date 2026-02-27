# Tasks: 0341 Search Performance & Reliability

### T-001: Fix SearchPalette race conditions and debounce
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given user types "re" then "rea" rapidly → When debounce fires → Then only "rea" results displayed, "re" fetch aborted

### T-002: Optimize search response payload
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given search query → When response returned → Then only 8 fields per result (no description, certMethod, etc.)

### T-003: Consolidate SQL query branches
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given search with/without category → When query executes → Then single SQL template used with dynamic fragments

### T-004: Add ILIKE fallback for substring matching
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test**: Given search "ado" with 0 tsvector results → When fallback runs → Then ILIKE matches returned with highlights

### T-005: Reduce search timeout
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [x] completed
**Test**: Given SEARCH_TIMEOUT_MS → When checked → Then equals 8000

### T-006: Update frontend tests
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test**: Given SearchPalette.test.tsx → When run → Then debounce 300ms tests pass, abort tests pass

### T-007: Update backend tests
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US3-01, AC-US5-01 | **Status**: [x] completed
**Test**: Given search.test.ts → When run → Then lean payload tests pass, ILIKE fallback tests pass
