# Tasks — 0330 Error Boundaries & Terminal Aesthetic

### T-001: Create global-error.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given an unhandled error → When it escapes the root layout → Then global-error.tsx renders with terminal aesthetic

### T-002: Create error.tsx
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given a route-level error → When it occurs in a child route → Then error.tsx renders inside the root layout

### T-003: Create not-found.tsx
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given a request to /nonexistent → When the page doesn't exist → Then not-found.tsx renders with navigation

### T-004: Redesign auth/error/page.tsx
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given /auth/error?reason=oauth_failed&step=db_upsert → When rendered → Then shows terminal-style error with step indicator

### T-005: Harden OAuth callback catch block
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test**: Given the redirect in catch throws → When catch executes → Then returns fallback HTML response

### T-006: Verify build
**Status**: [x] completed
**Test**: Given all changes → When `npm run build` runs → Then build succeeds
