---
increment_id: "0423-e2e-distributed-sync-test"
title: "E2E test: distributed sync routing to child project"
feature_id: "FS-423"
status: "active"
created: "2026-03-04"
by_user_story:
  US-001:
    tasks: ["T-001"]
    acs: ["AC-US1-01"]
---

# E2E Test: Distributed Sync Routing

## Summary

Verify that when `umbrella.enabled: true` and `syncStrategy: "distributed"`, external sync routes tickets to the child project's configured repos based on the Project field.

## User Stories

### US-001: Distributed sync routes to child project repos
**Project**: specweave

**As a** SpecWeave umbrella user with distributed sync
**I want** external tickets routed to the child project's repos
**So that** each team tracks work in their own repos

**Acceptance Criteria**:
- [ ] **AC-US1-01**: GitHub issue created in child repo (anton-abyzov/specweave) and JIRA issue in child project (WTTC)
