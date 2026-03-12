---
id: US-001
feature: FS-499
title: "AC-Gated External Sync (P1)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** SpecWeave user."
project: specweave
---

# US-001: AC-Gated External Sync (P1)

**Feature**: [FS-499](./FEATURE.md)

**As a** SpecWeave user
**I want** external sync to fire only when an acceptance criterion becomes fully satisfied
**So that** I avoid unnecessary API calls and rate limit consumption on every task completion

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a task is completed but no new ACs transitioned from unchecked to checked, when `onTaskCompleted()` runs, then `syncToExternalTools()` is NOT called
- [ ] **AC-US1-02**: Given a task completion causes one or more ACs to transition from `[ ]` to `[x]`, when `onTaskCompleted()` runs, then `syncToExternalTools()` IS called with the affected user story IDs
- [ ] **AC-US1-03**: Given any task is completed, when `onTaskCompleted()` runs, then living docs sync (`LivingDocsSync.syncIncrement`) still fires regardless of AC state changes
- [ ] **AC-US1-04**: Given a task has no AC tags (legacy or unlinked tasks), when that task is completed, then external sync fires on every completion for backward compatibility

---

## Implementation

**Increment**: [0499-external-sync-resilience](../../../../../increments/0499-external-sync-resilience/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Implement ACGate module
- [ ] **T-002**: Wire ACGate into LifecycleHookDispatcher.onTaskCompleted()
