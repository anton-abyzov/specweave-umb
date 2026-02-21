# Tasks: 0297 Dashboard Bug Fixes & Analytics

## Phase 1: Critical Bug Fixes

### T-001: Create ErrorBoundary component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [ ] pending
**Test**: Given a component that throws during render → When wrapped in ErrorBoundary → Then error UI is shown with "Reload" button instead of white screen

### T-002: Wrap App routes with ErrorBoundary
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04 | **Status**: [ ] pending
**Test**: Given App.tsx routes → When a page component throws → Then ErrorBoundary catches it and other pages remain navigable

### T-003: Create useProjectNavigate hook
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test**: Given active project with ?project=X → When useProjectNavigate('/path') called → Then navigates to /path?project=X

### T-004: Fix IncrementsPage navigate to use useProjectNavigate
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [ ] pending
**Test**: Given IncrementsPage with ?project=X → When clicking an increment row → Then navigates to /increments/:id?project=X

### T-005: Rebuild dashboard client and verify fixes
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01 | **Status**: [ ] pending
**Test**: Given rebuilt dashboard → When navigating to increment detail → Then page loads without crash

## Phase 2: Analytics Tracking

### T-006: Audit analytics tracking integration points
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test**: Given the codebase → When searching for trackCommand/trackSkill/trackAgent usage → Then all execution paths are identified

### T-007: Verify implicit command tracking
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-04 | **Status**: [ ] pending
**Test**: Given team-lead calling do internally → When checking events.jsonl → Then the implicit do call is logged

## Phase 3: Documentation

### T-008: Update README with Dashboard section
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test**: Given README.md → When read → Then contains Dashboard section with analytics feature descriptions

### T-009: Add analytics guide to public docs
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [ ] pending
**Test**: Given docs-site → When browsing → Then analytics dashboard guide exists with feature descriptions

### T-010: Update YouTube script with analytics mention
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [ ] pending
**Test**: Given youtube-tutorial-script.md → When read → Then contains analytics dashboard section
