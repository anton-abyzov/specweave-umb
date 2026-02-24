# Tasks: Fix intermittent search failures and preferences 500 on cold starts

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed

## Phase 1: Core Fixes

### T-001: Fix getCloudflareContext({ async: true }) in search.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given search.ts getKv() → When inspecting the getCloudflareContext call → Then it uses `{ async: true }` parameter

### T-002: Add retry logic to preferences GET route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given preferences GET endpoint → When DB fails on first attempt → Then retries once and succeeds

### T-003: Add retry logic to preferences PATCH route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given preferences PATCH endpoint → When DB fails on first attempt → Then retries the full read-merge-write

## Phase 2: Verification

### T-004: Run tests and build
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given all changes → When running test suite and build → Then all pass with no regressions
