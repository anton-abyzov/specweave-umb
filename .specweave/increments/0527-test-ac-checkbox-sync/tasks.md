# Tasks: FS-527 Test AC Checkbox Sync

### T-001: Run sync-living-docs twice and verify JIRA native checkboxes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test**: Given FS-527 increment exists → When sync-living-docs runs twice → Then JIRA story shows native ADF checkboxes and Priority/Status on separate lines

### T-002: Verify full hierarchy across JIRA, ADO, GitHub
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [ ] pending
**Test**: Given FS-527 synced → When each platform is checked → Then Epic→Story (JIRA), Feature→Issue (ADO), Milestone→Issue (GitHub) all correct
