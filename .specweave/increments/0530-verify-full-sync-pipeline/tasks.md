# Tasks: FS-530 Verify Full Sync Pipeline

### T-001: Run sync-living-docs and verify all 3 platforms create items correctly
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [ ] pending
**Test**: Given FS-530 increment → When sync-living-docs runs → Then GitHub milestone + issues, JIRA epic + stories, ADO epic + issues are created with correct hierarchy

### T-002: Add JIRA AC comment posting to jira-ac-checkbox-sync
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [ ] pending
**Test**: Given AC marked complete → When AC hook fires → Then JIRA story gets a progress comment with AC completion percentage

### T-003: Verify GitHub AC comment posting works automatically
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [ ] pending
**Test**: Given AC marked complete → When AC hook fires → Then GitHub issue gets a progress comment

### T-004: Verify ADO AC comment posting works automatically
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [ ] pending
**Test**: Given AC marked complete → When AC hook fires → Then ADO work item gets a progress comment

### T-005: Measure API call count for update cycle (not creation)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [ ] pending
**Test**: Given items already exist → When sync runs again → Then GitHub uses < 100 calls, JIRA uses < 4 per story
