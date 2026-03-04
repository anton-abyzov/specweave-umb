---
increment_id: "0422-e2e-centralized-sync-test"
title: "E2E test: centralized sync routing"
feature_id: "FS-422"
status: "active"
created: "2026-03-04"
by_user_story:
  US-001:
    tasks: ["T-001"]
    acs: ["AC-US1-01"]
---

# E2E Test: Centralized Sync Routing

## Summary

Verify that when `umbrella.enabled: false`, external sync routes all tickets to the global config targets (centralized mode) regardless of the project field.

## User Stories

### US-001: Centralized sync routes to global targets
**Project**: specweave

**As a** SpecWeave user with centralized sync
**I want** external tickets created in the global config repos
**So that** all tracking stays in one place

**Acceptance Criteria**:
- [ ] **AC-US1-01**: GitHub issue created in global repo (anton-abyzov/specweave) and JIRA issue in global project (SWE2E)
