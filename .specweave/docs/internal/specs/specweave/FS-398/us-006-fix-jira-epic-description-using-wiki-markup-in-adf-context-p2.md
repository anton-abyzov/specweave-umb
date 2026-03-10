---
id: US-006
feature: FS-398
title: "Fix JIRA Epic Description Using Wiki Markup in ADF Context (P2)"
status: completed
priority: P0
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** user with JIRA Cloud."
project: specweave
---

# US-006: Fix JIRA Epic Description Using Wiki Markup in ADF Context (P2)

**Feature**: [FS-398](./FEATURE.md)

**As a** user with JIRA Cloud
**I want** JIRA descriptions to render correctly
**So that** auto-created epics look professional

---

## Acceptance Criteria

- [x] **AC-US6-01**: `external-issue-auto-creator.ts` buildJiraEpicDescription() uses plain text or ADF format instead of wiki markup (`h2.`, `h3.`, `*bold*`) since the createIssue API wraps content in ADF

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
