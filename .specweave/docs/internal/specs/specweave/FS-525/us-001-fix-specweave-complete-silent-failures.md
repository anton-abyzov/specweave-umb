---
id: US-001
feature: FS-525
title: "Fix specweave complete silent failures"
status: completed
priority: P1
created: 2026-03-14T00:00:00.000Z
tldr: "**As a** developer using SpecWeave."
project: specweave
related_projects: [specweave-umb]
---

# US-001: Fix specweave complete silent failures

**Feature**: [FS-525](./FEATURE.md)

**As a** developer using SpecWeave
**I want** `specweave complete` to succeed even when external issues have drifted
**So that** completion is not blocked by stale external state

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given an increment with external drift >168 hours, when `specweave complete` runs, then it logs a warning to stderr and exits with code 0
- [x] **AC-US1-02**: Given a transition failure during completion with `--silent` flag, when the failure occurs, then diagnostic details are written to stderr (not suppressed)
- [x] **AC-US1-03**: Given a normal `specweave complete` invocation, when completion succeeds, then `LivingDocsSync.syncIncrement` is called exactly once (in `onIncrementDone`), not in `completeIncrement` pre-sync

---

## Implementation

**Increment**: [0525-fix-living-docs-sync-architecture](../../../../../increments/0525-fix-living-docs-sync-architecture/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
