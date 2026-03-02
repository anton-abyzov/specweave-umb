---
id: US-004
feature: FS-404
title: "Dynamic Epic Link Field Detection"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** user with a customized JIRA instance,."
---

# US-004: Dynamic Epic Link Field Detection

**Feature**: [FS-404](./FEATURE.md)

**As a** user with a customized JIRA instance,
**I want** the plugin to discover my Epic Link custom field ID dynamically,
**So that** epic linking works regardless of JIRA configuration.

---

## Acceptance Criteria

- [x] **AC-US4-01**: Plugin queries `/rest/api/*/field` to discover the Epic Link field ID at startup
- [x] **AC-US4-02**: Plugin detects Next-gen vs Classic project style and uses `parent` or custom field accordingly
- [x] **AC-US4-03**: `customfield_10014` is no longer hardcoded anywhere
- [x] **AC-US4-04**: Field ID is cached per JIRA instance to avoid repeated lookups

---

## Implementation

**Increment**: [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
