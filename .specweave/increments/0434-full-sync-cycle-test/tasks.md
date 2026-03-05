---
increment: 0434-full-sync-cycle-test
title: "Full Sync Cycle E2E Test"
---

# Tasks

### T-001: Sync to GitHub for all child repos
**User Story**: US-SPE-002, US-VSK-002, US-VPL-002 | **Satisfies ACs**: AC-SPE-US2-01, AC-VSK-US2-01, AC-VPL-US2-01 | **Status**: [x] completed
**Test**: Given increment with 3 user stories targeting different repos → When sync-progress runs → Then GitHub issues created in specweave, vskill, vskill-platform repos

### T-002: Sync to JIRA for all child repos
**User Story**: US-SPE-002, US-VSK-002, US-VPL-002 | **Satisfies ACs**: AC-SPE-US2-02, AC-VSK-US2-02, AC-VPL-US2-02 | **Status**: [x] completed
**Test**: Given increment with 3 user stories → When sync-progress runs → Then JIRA tickets created in WTTC and SWE2E projects

### T-003: Sync to ADO for specweave repo
**User Story**: US-SPE-002 | **Satisfies ACs**: AC-SPE-US2-03 | **Status**: [x] completed
**Test**: Given increment with specweave user story → When sync-progress runs → Then ADO work item created in SpecWeaveSync

### T-004: Verify progress comments with AC status
**User Story**: US-SPE-002 | **Satisfies ACs**: AC-SPE-US2-01 | **Status**: [x] completed
**Test**: Given ACs partially completed → When sync-progress runs → Then GitHub issue body shows AC checkboxes with correct checked/unchecked state

### T-005: Verify close flow transitions external items
**User Story**: US-SPE-002, US-VSK-002, US-VPL-002 | **Satisfies ACs**: AC-SPE-US2-01, AC-VSK-US2-01, AC-VPL-US2-01 | **Status**: [x] completed
**Test**: Given all ACs completed → When sync-progress runs → Then GitHub issues closed with completion comments
