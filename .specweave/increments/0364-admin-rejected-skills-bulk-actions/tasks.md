# Tasks: 0364-admin-rejected-skills-bulk-actions

### T-001: Create admin rejections API endpoint
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US2-03, AC-US3-02 | **Status**: [x] completed
**Test**: Given admin user → When GET /api/v1/admin/rejections?category=security&page=1 → Then returns paginated security issues

### T-002: Delete old public rejections endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given unauthenticated user → When GET /api/v1/rejections → Then 404

### T-003: Admin-gate rejected tab in Trust Center
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given non-admin user → When viewing Trust Center → Then no Rejected tab visible

### T-004: Rewrite RejectedSkillsTab with pagination and bulk actions
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US3-01 | **Status**: [x] completed
**Test**: Given admin on rejected tab → When selecting items and clicking Reprocess → Then POST with action=reprocess

### T-005: Add RejectedSkillsTab tests
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: Given test suite → When running → Then all 10 test cases pass

### T-006: Verify build and run full test suite
**User Story**: all | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: Given implementation → When build + tests → Then no errors
