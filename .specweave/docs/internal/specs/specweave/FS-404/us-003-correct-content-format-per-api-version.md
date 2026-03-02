---
id: US-003
feature: FS-404
title: "Correct Content Format Per API Version"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** user syncing specs/epics to JIRA,."
---

# US-003: Correct Content Format Per API Version

**Feature**: [FS-404](./FEATURE.md)

**As a** user syncing specs/epics to JIRA,
**I want** descriptions and comments to use the correct format (ADF for Cloud, wiki markup for Server),
**So that** formatting is preserved and API calls succeed.

---

## Acceptance Criteria

- [x] **AC-US3-01**: A format adapter converts content to ADF (v3/Cloud) or wiki markup (v2/Server) based on detected API version
- [x] **AC-US3-02**: Epic descriptions use correct format
- [x] **AC-US3-03**: Spec descriptions use correct format
- [x] **AC-US3-04**: Status sync comments use ADF format for Cloud, wiki for Server
- [x] **AC-US3-05**: Existing wiki-to-ADF conversion is extracted into a shared utility

---

## Implementation

**Increment**: [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
