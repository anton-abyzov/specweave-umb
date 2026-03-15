---
id: US-001
feature: FS-530
title: "AC completion auto-posts comments to all platforms"
status: not_started
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave user."
---

# US-001: AC completion auto-posts comments to all platforms

**Feature**: [FS-530](./FEATURE.md)

**As a** SpecWeave user
**I want** AC completion to automatically post progress comments to GitHub, JIRA, and ADO stories
**So that** stakeholders on any platform see real-time AC progress without manual updates

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked GitHub issue showing which ACs are done
- [ ] **AC-US1-02**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked JIRA story showing AC completion percentage
- [ ] **AC-US1-03**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked ADO work item showing AC completion percentage

---

## Implementation

**Increment**: [0530-verify-full-sync-pipeline](../../../../../increments/0530-verify-full-sync-pipeline/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
