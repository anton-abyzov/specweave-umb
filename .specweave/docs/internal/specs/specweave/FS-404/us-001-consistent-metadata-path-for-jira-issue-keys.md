---
id: US-001
feature: FS-404
title: Consistent Metadata Path for JIRA Issue Keys
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** SpecWeave user syncing tasks to JIRA,."
external:
  github:
    issue: 1469
    url: "https://github.com/anton-abyzov/specweave/issues/1469"
---

# US-001: Consistent Metadata Path for JIRA Issue Keys

**Feature**: [FS-404](./FEATURE.md)

**As a** SpecWeave user syncing tasks to JIRA,
**I want** all plugin files to read/write the JIRA issue key from one canonical metadata path,
**So that** auto-sync, commit sync, and manual sync all work together without silent data loss.

---

## Acceptance Criteria

- [x] **AC-US1-01**: All plugin files use `.external_sync.jira.issueKey` as the single canonical path
- [x] **AC-US1-02**: A shared constant/utility defines the canonical path (no string literals scattered)
- [x] **AC-US1-03**: Backward-compatible migration reads old paths (`.jira.issue`, `.jira.issueKey`) and writes canonical path
- [x] **AC-US1-04**: `enhanced-jira-sync.js:64` no longer returns placeholder `SPEC-001` as real data

---

## Implementation

**Increment**: [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
