---
increment: 0425-umbrella-sync-e2e-test
title: "Umbrella Sync E2E Verification"
---

# Tasks

### T-001: Verify resolver routes all three platforms for each child repo
**User Story**: US-SPE-001, US-VSK-001, US-VPL-001 | **Satisfies ACs**: AC-SPE-US1-01, AC-VSK-US1-01, AC-VPL-US1-01 | **Status**: [x] completed
**Test**: Given umbrella config with 3 child repos each having GitHub/JIRA/ADO sync → When resolveSyncTarget is called per project → Then correct per-repo targets returned for all 3 platforms

### T-002: Sync progress to GitHub for specweave child repo
**User Story**: US-SPE-001 | **Satisfies ACs**: AC-SPE-US1-01 | **Status**: [ ] pending
**Test**: Given increment with **Project**: specweave → When /sw:progress-sync runs → Then GitHub issue created in anton-abyzov/specweave

### T-003: Sync progress to GitHub for vskill child repo
**User Story**: US-VSK-001 | **Satisfies ACs**: AC-VSK-US1-01 | **Status**: [ ] pending
**Test**: Given increment with **Project**: vskill → When /sw:progress-sync runs → Then GitHub issue created in anton-abyzov/vskill

### T-004: Sync progress to GitHub for vskill-platform child repo
**User Story**: US-VPL-001 | **Satisfies ACs**: AC-VPL-US1-01 | **Status**: [ ] pending
**Test**: Given increment with **Project**: vskill-platform → When /sw:progress-sync runs → Then GitHub issue created in anton-abyzov/vskill-platform

### T-005: Verify JIRA routing per child repo
**User Story**: US-SPE-001, US-VSK-001, US-VPL-001 | **Satisfies ACs**: AC-SPE-US1-02, AC-VSK-US1-02, AC-VPL-US1-02 | **Status**: [ ] pending
**Test**: Given umbrella config → When JIRA sync triggered → Then tickets route to per-repo projectKey

### T-006: Verify ADO routing per child repo
**User Story**: US-SPE-001, US-VSK-001, US-VPL-001 | **Satisfies ACs**: AC-SPE-US1-03, AC-VSK-US1-03, AC-VPL-US1-03 | **Status**: [ ] pending
**Test**: Given umbrella config with ADO targets → When ADO sync triggered → Then work items route to per-repo ADO project
