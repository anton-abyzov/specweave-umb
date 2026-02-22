---
id: US-004
feature: FS-318
title: Wire LifecycleHookDispatcher into done skill post-closure
status: complete
priority: P2
created: 2026-02-22
project: specweave
external:
  github:
    issue: 1257
    url: https://github.com/anton-abyzov/specweave/issues/1257
---
# US-004: Wire LifecycleHookDispatcher into done skill post-closure

**Feature**: [FS-318](./FEATURE.md)

SpecWeave user
**I want** the done skill to explicitly report sync results after closure
**So that** I can see which post-closure operations succeeded or failed

---

## Acceptance Criteria

- [x] **AC-US4-01**: The done skill's Step 9 (Post-Closure Sync) is updated to show the sync result summary table after `specweave complete` runs
- [x] **AC-US4-02**: If any sync operation fails, the skill shows "Run /sw:progress-sync to retry" guidance

---

## Implementation

**Increment**: [0318-post-closure-sync-pipeline](../../../../../increments/0318-post-closure-sync-pipeline/spec.md)

