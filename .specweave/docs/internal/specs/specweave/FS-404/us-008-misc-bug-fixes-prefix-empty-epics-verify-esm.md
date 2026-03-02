---
id: US-008
feature: FS-404
title: "Misc Bug Fixes (Prefix, Empty Epics, Verify, ESM)"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** developer using the JIRA sync plugin,."
---

# US-008: Misc Bug Fixes (Prefix, Empty Epics, Verify, ESM)

**Feature**: [FS-404](./FEATURE.md)

**As a** developer using the JIRA sync plugin,
**I want** miscellaneous bugs fixed,
**So that** the plugin behaves correctly in edge cases.

---

## Acceptance Criteria

- [x] **AC-US8-01**: Epic sync derives project prefix from actual project key, not hardcoded `FS-`
- [x] **AC-US8-02**: Multi-project sync only creates epics for projects that have classified stories
- [x] **AC-US8-03**: Duplicate detector returns `success: false` when verification fails
- [x] **AC-US8-04**: `refresh-cache.ts` uses ESM-compatible entry point detection (`import.meta.url`)

---

## Implementation

**Increment**: [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
